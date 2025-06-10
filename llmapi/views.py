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

from posts.models import Post
from llmapi.embed_and_index import build_index_incremental


# Constants
UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'pdfs')
os.makedirs(UPLOAD_DIR, exist_ok=True)

INDEX_PATH = "llmapi/index.faiss"
CHUNKS_PATH = "llmapi/chunks.pkl"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5

# Load embedding model and index at startup
embedding_model = SentenceTransformer(EMBED_MODEL_NAME)

if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
else:
    index = faiss.IndexFlatL2(384)

if os.path.exists(CHUNKS_PATH):
    with open(CHUNKS_PATH, "rb") as f:
        chunk_metadata = pickle.load(f)
else:
    chunk_metadata = []


def ask_llama_with_context(question, context):
    """
    Run LLaMA 3.2 via Ollama with context-enhanced prompt.
    """
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


def get_top_chunks(query, top_k=TOP_K):
    """
    Search FAISS for top K relevant chunks for a given query.
    """
    query_vector = embedding_model.encode([query])
    query_vector = np.array(query_vector).astype("float32")
    D, I = index.search(query_vector, top_k)
    chunks = []

    for dist, i in zip(D[0], I[0]):
        if i < len(chunk_metadata):
            chunk_text = chunk_metadata[i]["text"]
            source = chunk_metadata[i]["source"]
            chunks.append(chunk_text)

    return chunks


@csrf_exempt
@require_http_methods(["POST"])
def upload_documents(request):
    """
    Accept PDF uploads, save them as Post objects, and re-index all documents in media/pdfs.
    """
    uploaded_files = request.FILES.getlist('documents')
    saved_files = []

    if not uploaded_files:
        return JsonResponse({'error': 'No files uploaded.'}, status=400)

    # For demonstration, assign request.user as author. Adjust if needed.
    author = request.user if request.user.is_authenticated else None

    for file in uploaded_files:
        # Save via Post model, which stores files to media/pdfs/
        post = Post(name=file.name, author=author)
        post.any_file.save(file.name, file)
        post.save()
        saved_files.append(post.any_file.path)  # Full path on disk

    try:
        # Rebuild index on all files in media/pdfs folder
        build_index_incremental(UPLOAD_DIR)

        return JsonResponse({
            'message': 'Files uploaded and indexed successfully.',
            'files': [os.path.basename(f) for f in saved_files]
        })
    except Exception as e:
        return JsonResponse({'error': f'Indexing failed: {str(e)}'}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def query_llama(request):
    """
    Accept a question, retrieve relevant context, and respond using LLaMA.
    """
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            question = data.get('question', '').strip()
        else:
            question = request.POST.get('question', '').strip()
    except Exception:
        return JsonResponse({'error': 'Invalid input.'}, status=400)

    if not question:
        return JsonResponse({'error': 'Question is required.'}, status=400)

    top_chunks = get_top_chunks(question, TOP_K)
    if not top_chunks:
        return JsonResponse({'answer': 'No document content indexed yet.'})

    context = "\n\n".join(top_chunks)
    answer = ask_llama_with_context(question, context)

    return JsonResponse({'answer': answer})
