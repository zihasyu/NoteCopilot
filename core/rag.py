"""
Milvus RAG System - Document Chunking and Embedding for Markdown Notes
"""
import os
from typing import List, Optional
from glob import glob

from pymilvus import (
    connections,
    Collection,
    FieldSchema,
    CollectionSchema,
    DataType,
    utility
)
from sentence_transformers import SentenceTransformer
import markdown


class NoteRAG:
    """Note RAG System"""

    def __init__(
        self,
        host: str = "localhost",
        port: str = "19530",
        collection_name: str = "notes",
        model_name: str = "BAAI/bge-large-zh-v1.5"
    ):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.collection: Optional[Collection] = None

    def connect(self):
        """Connect to Milvus"""
        connections.connect(host=self.host, port=self.port)

    def create_collection(self):
        """Create notes collection"""
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            return

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=65535),
            FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=512),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.dim)
        ]

        schema = CollectionSchema(fields, "Notes Vector DB")
        self.collection = Collection(self.collection_name, schema)

        # Create IVF_FLAT index
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        self.collection.create_index("embedding", index_params)

    def chunk_markdown(self, content: str, chunk_size: int = 500) -> List[str]:
        """Chunk markdown document"""
        # Remove markdown tags, extract plain text
        html = markdown.markdown(content)
        text = html.replace('<p>', '').replace('</p>', '\n').replace('<h1>', '# ').replace('</h1>', '\n')
        text = text.replace('<h2>', '## ').replace('</h2>', '\n').replace('<h3>', '### ').replace('</h3>', '\n')

        # Chunk by paragraphs
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                current_chunk += "\n" + para

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def ingest_notes(self, notes_path: str):
        """Batch import markdown notes"""
        md_files = glob(os.path.join(notes_path, "**/*.md"), recursive=True)

        all_chunks = []
        all_sources = []

        for file_path in md_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            chunks = self.chunk_markdown(content)
            all_chunks.extend(chunks)
            all_sources.extend([file_path] * len(chunks))

        if not all_chunks:
            return 0

        # Generate embeddings
        embeddings = self.model.encode(all_chunks, normalize_embeddings=True)

        # Insert into Milvus
        entities = [
            all_chunks,
            all_sources,
            embeddings.tolist()
        ]

        self.collection.insert(entities)
        self.collection.flush()
        self.collection.load()

        return len(all_chunks)

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        """Search related notes"""
        self.collection.load()

        query_embedding = self.model.encode([query], normalize_embeddings=True)

        search_params = {"metric_type": "L2", "params": {"nprobe": 10}}

        results = self.collection.search(
            data=query_embedding.tolist(),
            anns_field="embedding",
            param=search_params,
            limit=top_k,
            output_fields=["content", "source"]
        )

        notes = []
        for hits in results:
            for hit in hits:
                notes.append({
                    "content": hit.entity.get("content"),
                    "source": hit.entity.get("source"),
                    "score": float(hit.distance)
                })

        return notes
