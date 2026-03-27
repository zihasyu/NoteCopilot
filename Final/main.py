"""
NoteCopilot - Smart Notes Assistant
Built with LangGraph + Milvus + MCP
"""
import os
import sys
import argparse
from dotenv import load_dotenv

from core.rag import NoteRAG
from core.agent import NoteCopilotAgent
from checkpointer.sqlite import create_checkpointer, ConversationMemory
from mcp_tools.server import start_mcp_server


def init_db():
    """Initialize vector database"""
    print("[INFO] Initializing Milvus...")

    rag = NoteRAG(
        host=os.getenv("MILVUS_HOST", "localhost"),
        port=os.getenv("MILVUS_PORT", "19530")
    )
    rag.connect()
    rag.create_collection()

    notes_path = os.getenv("NOTES_PATH", "./notes")
    if os.path.exists(notes_path):
        count = rag.ingest_notes(notes_path)
        print(f"[OK] Imported {count} note chunks")
    else:
        print(f"[WARN] Notes path not found: {notes_path}")

    return rag


def chat_mode(rag: NoteRAG):
    """Interactive chat mode"""
    print("\n" + "="*50)
    print("NoteCopilot Chat Mode")
    print("="*50)
    print("Commands:")
    print("  /new <thread_id> - Create new conversation")
    print("  /history         - Show conversation history")
    print("  /quit            - Exit")
    print("-" * 50)

    # Create agent with persistence
    checkpointer = create_checkpointer()
    agent = NoteCopilotAgent(rag=rag, checkpointer=checkpointer)
    memory = ConversationMemory()

    current_thread = "default"

    while True:
        try:
            user_input = input(f"\n[{current_thread}] > ").strip()

            if not user_input:
                continue

            if user_input == "/quit":
                break

            if user_input.startswith("/new "):
                current_thread = user_input[5:].strip()
                memory.create_thread(current_thread)
                print(f"[OK] Switched to new thread: {current_thread}")
                continue

            if user_input == "/history":
                threads = memory.list_threads()
                print("\nConversation History:")
                for t in threads:
                    print(f"  - {t['thread_id']} (updated: {t['updated_at']})")
                continue

            # Execute agent
            print("[INFO] Processing...")
            result = agent.invoke(user_input, thread_id=current_thread)

            print(f"\n[Response]\n{result.get('response', 'No response')}")

            # Show retrieved notes
            notes = result.get('retrieved_notes', [])
            if notes:
                print(f"\n[Sources]")
                for n in notes[:2]:
                    print(f"  - {n['source']} (score: {n['score']:.2f})")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[ERROR] {e}")

    print("\n[OK] Goodbye!")


def mcp_mode(rag: NoteRAG):
    """MCP Server mode"""
    print("[INFO] Starting MCP Server (stdio mode)...")
    print("[INFO] Connect via Claude Desktop or other MCP clients")
    start_mcp_server(rag, transport="stdio")


def search_mode(rag: NoteRAG):
    """Direct RAG search mode"""
    print("\n" + "="*50)
    print("NoteCopilot RAG Search Mode")
    print("="*50)
    print("Type your query to search notes directly")
    print("Commands:")
    print("  /quit - Exit")
    print("-" * 50)

    while True:
        try:
            query = input("\n[Search] > ").strip()

            if not query:
                continue

            if query == "/quit":
                break

            print("[INFO] Searching...")
            results = rag.search(query, top_k=5)

            if not results:
                print("[INFO] No results found")
                continue

            print(f"\n[Results] Found {len(results)} matches:")
            for i, r in enumerate(results, 1):
                print(f"\n--- Result {i} ---")
                print(f"Source: {r['source']}")
                print(f"Score: {r['score']:.4f}")
                print(f"Content: {r['content'][:300]}...")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[ERROR] {e}")

    print("\n[OK] Goodbye!")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="NoteCopilot - Smart Notes Assistant")
    parser.add_argument(
        "--mode",
        choices=["chat", "mcp", "init", "search"],
        default="chat",
        help="Mode: chat (interactive), mcp (MCP server), init (init db only), search (RAG only)"
    )

    args = parser.parse_args()

    if args.mode == "init":
        init_db()
        return

    # Initialize RAG
    rag = init_db()

    if args.mode == "chat":
        chat_mode(rag)
    elif args.mode == "mcp":
        mcp_mode(rag)
    elif args.mode == "search":
        search_mode(rag)


if __name__ == "__main__":
    main()
