# net/api/rag_service.py

"""
RAG Service singleton for FastAPI.
Provides document retrieval and query functionality.
"""

from __future__ import annotations
from typing import Dict, List, Any, Optional
import os
import sys
import pathlib

# Add project root to path
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import load_config
from rag.pipeline import RagPipeline


class RagService:
    """Singleton RAG service for the API."""

    _instance: Optional["RagService"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Only initialize once
        if not self._initialized:
            self.cfg = None
            self.pipeline = None
            self.retriever = None
            self.qa = None

    def initialize(self, yaml_path: str = "config.yaml", use_yaml: bool = True):
        """Initialize the RAG pipeline."""
        if self._initialized:
            print("[RAG Service] Already initialized")
            return

        print("[RAG Service] Starting initialization...")
        print(f"[RAG Service] Working directory: {os.getcwd()}")
        print(f"[RAG Service] Config path: {yaml_path}")
        print(f"[RAG Service] Config exists: {os.path.exists(yaml_path)}")

        try:
            # Load config
            print("[RAG Service] Loading config...")
            self.cfg = load_config(yaml_path=yaml_path, use_yaml=use_yaml)
            print("[RAG Service] Config loaded successfully")

            # Create pipeline
            print("[RAG Service] Creating RAG pipeline...")
            self.pipeline = RagPipeline(self.cfg)
            print("[RAG Service] Pipeline created")

            # Bootstrap (load existing index or create new)
            print("[RAG Service] Bootstrapping...")
            self.pipeline.bootstrap()
            print("[RAG Service] Bootstrap complete")

            # Build retriever
            print("[RAG Service] Building retriever...")
            self.retriever = self.pipeline.serve()
            print("[RAG Service] Retriever built successfully")

            # Build QA chain (LLM)
            print("[RAG Service] Building QA chain...")
            self.qa = self.pipeline.build_qa()
            if isinstance(self.qa, dict) and self.qa.get("llm") == "disabled":
                print("[RAG Service] LLM disabled in config - retrieval-only mode")
            else:
                print("[RAG Service] QA chain built successfully")

            self._initialized = True
            RagService._initialized = True
            print("[RAG Service] Initialization complete!")

        except Exception as e:
            print(f"[RAG Service] Initialization failed: {e}")
            import traceback
            traceback.print_exc()
            # Don't raise - allow API to start even if RAG fails

    def is_ready(self) -> bool:
        """Check if the service is initialized and ready."""
        return self._initialized and self.pipeline is not None

    def is_llm_enabled(self) -> bool:
        """Check if LLM is enabled based on config and initialization."""
        if not self._initialized or self.qa is None:
            return False
        # Check if QA is a valid chain (not the disabled dict)
        if isinstance(self.qa, dict) and self.qa.get("llm") == "disabled":
            return False
        return True

    def retrieve_documents(self, query: str, k: int = 4) -> List[Any]:
        """
        Retrieve relevant documents for a query.
        Returns list of Document objects.
        """
        if not self.is_ready() or not self.retriever:
            print(f"[RAG Service] retrieve_documents: NOT READY (ready={self.is_ready()}, retriever={self.retriever is not None})")
            return []

        print(f"[RAG Service] Retrieving documents for query: '{query}'")

        try:
            # Try new interface first
            docs = self.retriever.invoke(query)
            print(f"[RAG Service] invoke() returned {len(docs) if docs else 0} documents")
        except (TypeError, AttributeError) as e:
            print(f"[RAG Service] invoke() failed ({type(e).__name__}), trying legacy interface")
            # Fall back to legacy interface
            try:
                docs = self.retriever.get_relevant_documents(query)
                print(f"[RAG Service] get_relevant_documents() returned {len(docs) if docs else 0} documents")
            except Exception as e2:
                print(f"[RAG Service] get_relevant_documents() also failed: {e2}")
                return []

        result = docs or []
        print(f"[RAG Service] Final: returning {len(result)} documents")
        return result

    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the RAG system and get an answer.

        In retrieval-only mode (LLM disabled), returns the most relevant documents.

        Returns:
            dict with keys:
                - answer: str (the answer text or retrieval summary)
                - source_documents: list (retrieved documents)
                - llm_enabled: bool
        """
        if not self.is_ready():
            return {
                "answer": "RAG service not initialized",
                "source_documents": [],
                "llm_enabled": False,
            }

        # Check if LLM is enabled from runtime settings
        llm_enabled = self.is_llm_enabled()

        # If LLM is enabled, use the QA chain
        if llm_enabled and self.qa:
            print(f"[RAG Service] Querying LLM with question: '{question}'")
            try:
                # Call the QA chain - it will retrieve and generate answer
                result = self.qa({"query": question})

                # Extract answer and source documents
                answer = result.get("result", "No answer generated.")
                docs = result.get("source_documents", [])

                print(f"[RAG Service] LLM returned answer (length: {len(answer)})")

                return {
                    "answer": answer,
                    "source_documents": docs,
                    "llm_enabled": True,
                }
            except Exception as e:
                print(f"[RAG Service] LLM query failed: {e}")
                import traceback
                traceback.print_exc()
                # Fall back to retrieval-only mode
                answer = f"Error calling LLM: {str(e)}\n\nFalling back to retrieval-only mode."
                docs = self.retrieve_documents(question)
                answer += "\n\n" + self._format_retrieval_response(docs)
                return {
                    "answer": answer,
                    "source_documents": docs,
                    "llm_enabled": False,
                }

        # Retrieval-only mode (LLM disabled)
        docs = self.retrieve_documents(question)

        # Format response based on LLM availability
        if not docs:
            answer = "No relevant documents found."
        else:
            answer = self._format_retrieval_response(docs)

        return {
            "answer": answer,
            "source_documents": docs,
            "llm_enabled": False,
        }

    def _format_retrieval_response(self, docs: List[Any]) -> str:
        """Format retrieval-only response (match Streamlit output)."""
        chunks = []
        for i, doc in enumerate(docs[:5], 1):
            src = doc.metadata.get("source", "unknown")
            page = doc.metadata.get("page_number") or doc.metadata.get("page", "?")
            content = doc.page_content or ""
            # Show up to 600 characters like Streamlit
            preview = content[:600] + ("..." if len(content) > 600 else "")
            # Format as markdown
            filename = src.split('/')[-1] if src else "unknown"
            chunks.append(f"**{i}. {filename} (page {page})**\n\n{preview}\n\n---")

        return (
            f"LLM disabled - showing retrieval only. Retrieved {len(docs)} chunk(s).\n\n" +
            "**Top Chunks:**\n\n" +
            "\n\n".join(chunks)
        )


# Global instance accessor
def get_rag_service() -> RagService:
    """Get the singleton RAG service instance."""
    return RagService()
