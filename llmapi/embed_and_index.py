import os
import pickle
import faiss
import fitz  # PyMuPDF
import camelot
from sentence_transformers import SentenceTransformer

def extract_tables_from_pdf(filepath):
    try:
        tables = camelot.read_pdf(filepath, pages='all', flavor='lattice')  # Try 'stream' if this fails
        if tables:
            all_tables_text = []
            for table in tables:
                table_text = table.df.to_string(index=False, header=False)
                all_tables_text.append(table_text)
            return "\n\n[Extracted Tables]\n" + "\n\n".join(all_tables_text)
        else:
            return ""
    except Exception as e:
        print(f"[WARN] Table extraction failed for {filepath}: {e}")
        return ""

def load_pdfs(folder_path, skip_files=None):
    skip_files = skip_files or []
    texts = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf") and file not in skip_files:
            print(f"[INFO] Loading: {file}")
            filepath = os.path.join(folder_path, file)

            # Extract text using PyMuPDF
            doc = fitz.open(filepath)
            full_text = "\n".join([page.get_text() for page in doc])

            # Extract tables using Camelot
            table_text = extract_tables_from_pdf(filepath)

            # Append table content to main text
            combined_text = full_text + "\n\n" + table_text
            texts.append((file, combined_text))
    return texts

def chunk_text(text, chunk_size=500):
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) <= chunk_size:
            current_chunk += " " + para
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para
    if current_chunk:
        chunks.append(current_chunk.strip())

    print(f"[INFO] Created {len(chunks)} chunks from document.")
    return chunks

def build_index_incremental(documents_folder):
    print(f"[START] Building FAISS index from folder: {documents_folder}")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Load existing index & metadata if available
    if os.path.exists("llmapi/index.faiss") and os.path.exists("llmapi/chunks.pkl"):
        print("[INFO] Loading existing FAISS index and metadata...")
        index = faiss.read_index("llmapi/index.faiss")
        with open("llmapi/chunks.pkl", "rb") as f:
            metadata = pickle.load(f)
        indexed_files = set(item['source'] for item in metadata)
        print(f"[INFO] Already indexed files: {indexed_files}")
    else:
        print("[INFO] No existing index found. Creating new index...")
        index = None
        metadata = []
        indexed_files = set()

    # Load new PDFs
    texts = load_pdfs(documents_folder, skip_files=indexed_files)
    if not texts:
        print("[INFO] No new documents to index.")
        return

    all_chunks = []
    new_metadata = []

    for filename, text in texts:
        print(f"[INFO] Processing file: {filename}")
        contains_table = "[Extracted Tables]" in text
        chunks = chunk_text(text)
        for chunk in chunks:
            all_chunks.append(chunk)
            new_metadata.append({
                "source": filename,
                "text": chunk,
                "contains_table": contains_table
            })

    print(f"[INFO] Embedding {len(all_chunks)} new chunks...")
    embeddings = model.encode(all_chunks, show_progress_bar=True)

    if index is None:
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        print(f"[INFO] Created new FAISS index with dimension: {dim}")

    index.add(embeddings)
    metadata.extend(new_metadata)

    os.makedirs("llmapi", exist_ok=True)
    faiss.write_index(index, "llmapi/index.faiss")
    with open("llmapi/chunks.pkl", "wb") as f:
        pickle.dump(metadata, f)

    print(f"[SUCCESS] Index updated. Total indexed chunks: {len(metadata)}")

if __name__ == "__main__":
    pdf_folder_path = os.path.join(os.getcwd(), "uploaded_docs")
    build_index_incremental(pdf_folder_path)
