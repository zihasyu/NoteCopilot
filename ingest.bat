@echo off
echo ==========================================
echo NoteCopilot - Ingest Notes to RAG
echo ==========================================
echo.

call .venv\Scripts\activate.bat

python -c "
import os
import sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv()

from core.rag import NoteRAG

print('[INFO] Connecting to Milvus...')
rag = NoteRAG(
    host=os.getenv('MILVUS_HOST', 'localhost'),
    port=os.getenv('MILVUS_PORT', '19530')
)
rag.connect()
rag.create_collection()

notes_path = os.getenv('NOTES_PATH', './notes')
print(f'[INFO] Scanning notes from: {notes_path}')

if not os.path.exists(notes_path):
    print(f'[ERROR] Notes path not found: {notes_path}')
    print('[INFO] Creating notes directory...')
    os.makedirs(notes_path)
    print('[INFO] Please add your .md files and run again')
    sys.exit(1)

count = rag.ingest_notes(notes_path)
print(f'[OK] Successfully ingested {count} chunks')
print('[INFO] You can now use: run.bat chat')
"

pause
