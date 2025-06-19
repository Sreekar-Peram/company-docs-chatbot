import os
import uuid
import json
import pickle
import subprocess
import numpy as np

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from sentence_transformers import SentenceTransformer
import faiss

from posts.models import Post, Client
from llmapi.embed_and_index import build_index_incremental

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from clients.models import Company

# Constants
UPLOAD_BASE_DIR = os.path.join(settings.MEDIA_ROOT, 'pdfs')
INDEX_BASE_DIR = os.path.join(settings.MEDIA_ROOT, 'faiss_indexes')
os.makedirs(UPLOAD_BASE_DIR, exist_ok=True)

EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5
embedding_model = SentenceTransformer(EMBED_MODEL_NAME)


@login_required
def upload_test_view(request):
    companies = Company.objects.all()
    return render(request, 'upload_test.html', {'companies': companies})


def ask_llama_with_context(question, context):
    prompt = f"""
You are an assistant that only answers questions using the given context from company documents.

Context:
{context}

Question:
{question}

If the answer is not in the context, respond with:
"The content is not present in the document."
"""
    try:
        result = subprocess.run(
            ['ollama', 'run', 'llama3.2'],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='replace'
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "[Error: LLaMA processing timed out.]"
    except Exception as e:
        return f"[Error: {str(e)}]"


@csrf_exempt
@require_http_methods(["POST"])
def upload_documents(request):
    uploaded_files = request.FILES.getlist('documents')
    company_name = request.POST.get('company_name')
    client_name = request.POST.get('client_name')

    if not uploaded_files or not company_name or not client_name:
        return JsonResponse({'error': 'Company name, client name, and documents are required.'}, status=400)

    try:
        company = Company.objects.get(name=company_name)
        client = Client.objects.get(name=client_name, company=company)
    except (Company.DoesNotExist, Client.DoesNotExist):
        return JsonResponse({'error': 'Client or Company not identified. Please contact support.'}, status=404)

    client_upload_dir = os.path.join(UPLOAD_BASE_DIR, company.name, client.name)
    os.makedirs(client_upload_dir, exist_ok=True)

    saved_files = []
    for file in uploaded_files:
        post = Post(name=file.name, client=client)
        post.any_file.save(os.path.join(client.name, file.name), file)
        post.save()
        saved_files.append(post.any_file.path)

    try:
        build_index_incremental(client_upload_dir, company.name, client.name)
        return JsonResponse({'message': 'Files uploaded and indexed successfully.', 'files': [os.path.basename(f) for f in saved_files]})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



@csrf_exempt
@require_http_methods(["POST"])
def query_llama(request):
    try:
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        company_name = data.get('company_name', '').strip()
        client_name = data.get('client_name', '').strip()
    except:
        return JsonResponse({'error': 'Invalid JSON format or missing fields.'}, status=400)

    if not question or not company_name or not client_name:
        return JsonResponse({'error': 'Question, company name, and client name are required.'}, status=400)

    try:
        company = Company.objects.get(name=company_name)
        client = Client.objects.get(name=client_name, company=company)
    except (Company.DoesNotExist, Client.DoesNotExist):
        return JsonResponse({'error': 'Client or Company not identified. Please contact support.'}, status=404)

    index_dir = os.path.join(INDEX_BASE_DIR, company.name, client.name)
    index_path = os.path.join(index_dir, "index.faiss")
    metadata_path = os.path.join(index_dir, "metadata.pkl")

    if not os.path.exists(index_path) or not os.path.exists(metadata_path):
        return JsonResponse({'error': 'Index or metadata not found for this client.'}, status=404)

    try:
        index = faiss.read_index(index_path)
        with open(metadata_path, "rb") as f:
            metadata = pickle.load(f)

        question_embedding = embedding_model.encode([question])
        distances, indices = index.search(np.array(question_embedding), TOP_K)

        context_chunks = [metadata[idx]["text"] for idx in indices[0] if idx < len(metadata)]
        context = "\n\n".join(context_chunks)
        answer = ask_llama_with_context(question, context)
        return JsonResponse({'answer': answer})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
