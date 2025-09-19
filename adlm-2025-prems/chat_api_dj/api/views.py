import json
import uuid
import io
from django.http import StreamingHttpResponse, JsonResponse, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.conf import settings
from ninja import NinjaAPI, Schema
from ollama import chat, ChatResponse
import markdown
import fitz  # PyMuPDF
from PIL import Image
import matplotlib
from typing import List, Optional, Dict, Any
from datetime import datetime

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from .models import Document, Chunk


# Pydantic Schemas for API responses
class RootResponse(Schema):
    version: str
    documentation: str


class HealthResponse(Schema):
    status: str
    service: str


class DocumentSummary(Schema):
    id: int
    relative_path: str


class PaginationInfo(Schema):
    page: int
    page_size: int
    total: int
    total_pages: int
    has_next: bool
    has_previous: bool


class SearchInfo(Schema):
    query: Optional[str]
    is_search: bool


class DocumentsResponse(Schema):
    documents: List[DocumentSummary]
    pagination: PaginationInfo
    search: SearchInfo


class DocumentDetail(Schema):
    id: int
    relative_path: str
    markdown: str
    #table_of_contents: Optional[Dict[str, Any]]
    #page_stats: Optional[Dict[str, Any]]
    num_pages: int
    num_chunks: int
    created_at: datetime
    updated_at: datetime
    page_urls: List[str]


class DocumentError(Schema):
    error: str


class ChunkDetail(Schema):
    id: int
    document_id: int
    chunk_index: int
    text: str
    text_length: int
    page_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ChunkSummary(Schema):
    id: int
    document_id: int
    document_path: str
    chunk_index: int
    text: str
    text_length: int
    page_metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class ChunksResponse(Schema):
    chunks: List[ChunkSummary]
    pagination: PaginationInfo
    search: SearchInfo


class ChatError(Schema):
    error: str


class MarkerResponse(Schema):
    blocks: List[Dict[str, Any]]


MODEL = "qwen3:0.6b"

SYSTEM_PROMPT = """
You are a helpful assistant running a streaming chat API that can use tools to help you answer questions.
"""


# Define a python tool
async def add_two_numbers(a: int, b: int) -> int:
    """
    Add two numbers

    Args:
        a (int): The first number as an int
        b (int): The second number as an int

    Returns:
        int: The sum of the two numbers
    """
    return a + b


async def search_documents(query: str) -> list[Chunk]:
    """
    Search for documents that contain the query

    Args:
        query (str): The query to search for

    Returns:
        list[Chunk]: The document chunks that contain the query
    """
    from asgiref.sync import sync_to_async

    # TODO use an actual full text search (haystack)
    # TODO also use vector search (chroma)
    chunks = await sync_to_async(list)(Chunk.objects.filter(text__icontains=query))
    return chunks


TOOLS = {"add_two_numbers": add_two_numbers}

# Create NinjaAPI instance
api = NinjaAPI(title="Chat API", version="1.0.0")


@api.get("/", response=RootResponse)
async def root(request):
    return {"version": "1.0.0", "documentation": "/api/docs"}


@api.get("/health", response=HealthResponse)
async def health_check(request):
    """Health check endpoint"""
    return {"status": "healthy", "service": "chat-api"}


@api.get("/documents", response=DocumentsResponse)
async def get_documents(request, page: int = 1, page_size: int = 50, q: str = None):
    """Get documents with pagination and optional search - returns list of id and relative_path with pagination metadata"""
    from asgiref.sync import sync_to_async
    from haystack.query import SearchQuerySet
    import math

    # Validate pagination parameters
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 1000:  # Limit max page size
        page_size = 50

    # Calculate offset
    offset = (page - 1) * page_size

    if q:
        # Use Haystack search if query parameter is provided
        def search_documents():
            sqs = SearchQuerySet().models(Document).filter(content=q)
            return [result.object for result in sqs if result.object]

        search_results = await sync_to_async(search_documents)()
        total_documents = len(search_results)

        # Apply pagination to search results
        documents = search_results[offset : offset + page_size]
    else:
        # Get total count
        total_documents = await sync_to_async(Document.objects.count)()

        # Get paginated documents
        documents = await sync_to_async(list)(
            Document.objects.all().order_by("relative_path")[
                offset : offset + page_size
            ]
        )

    # Calculate total pages
    total_pages = math.ceil(total_documents / page_size) if total_documents > 0 else 1

    return {
        "documents": [
            {
                "id": doc.id,
                "relative_path": doc.relative_path,
            }
            for doc in documents
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total_documents,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        },
        "search": {
            "query": q,
            "is_search": q is not None,
        },
    }


@api.get("/documents/{document_id}", response={200: DocumentDetail, 404: DocumentError})
async def get_document(request, document_id: int):
    """Get a specific document by ID"""
    from asgiref.sync import sync_to_async

    try:
        document = await Document.objects.aget(id=document_id)
        # Count the number of chunks for this document
        num_chunks = await sync_to_async(
            Chunk.objects.filter(document=document).count
        )()

        page_urls = [
            reverse(
                "pdf_page_image", kwargs={"document_id": document_id, "page_index": i}
            )
            for i in range(document.num_pages)
        ]

        return {
            "id": document.id,
            "relative_path": document.relative_path,
            "markdown": document.markdown,
            "table_of_contents": document.table_of_contents,
            "page_stats": document.page_stats,
            "num_pages": document.num_pages,
            "num_chunks": num_chunks,
            "created_at": document.created_at,
            "updated_at": document.updated_at,
            "page_urls": page_urls,
        }
    except Document.DoesNotExist:
        return {"error": "Document not found"}, 404


@api.get(
    "/documents/{document_id}/chunks/{chunk_idx}",
    response={200: ChunkDetail, 404: DocumentError},
)
async def get_document_chunk(request, document_id: int, chunk_idx: int):
    """Get a specific chunk from a document"""
    try:
        document = await Document.objects.aget(id=document_id)
        chunk = await Chunk.objects.aget(document=document, chunk_index=chunk_idx)
        return {
            "id": chunk.id,
            "document_id": document_id,
            "chunk_index": chunk.chunk_index,
            "text": chunk.text,
            "text_length": chunk.text_length,
            "page_metadata": chunk.page_metadata,
            "created_at": chunk.created_at,
            "updated_at": chunk.updated_at,
        }
    except Document.DoesNotExist:
        return {"error": "Document not found"}, 404
    except Chunk.DoesNotExist:
        return {"error": "Chunk not found"}, 404


@api.get("/chunks", response=ChunksResponse)
async def get_chunks(request, page: int = 1, page_size: int = 50, q: str = None):
    """Get chunks with pagination and optional search - returns list of chunks with document info"""
    from asgiref.sync import sync_to_async
    from haystack.query import SearchQuerySet
    import math

    # Validate pagination parameters
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 1000:  # Limit max page size
        page_size = 50

    # Calculate offset
    offset = (page - 1) * page_size

    if q:
        # Use Haystack search if query parameter is provided
        def search_chunks():
            sqs = SearchQuerySet().models(Chunk).filter(content=q)
            return [result.object for result in sqs if result.object]

        search_results = await sync_to_async(search_chunks)()
        total_chunks = len(search_results)

        # Apply pagination to search results
        chunks = search_results[offset : offset + page_size]
    else:
        # Get total count
        total_chunks = await sync_to_async(Chunk.objects.count)()

        # Get paginated chunks with document info
        chunks = await sync_to_async(list)(
            Chunk.objects.select_related("document")
            .all()
            .order_by("document__relative_path", "chunk_index")[
                offset : offset + page_size
            ]
        )

    # Calculate total pages
    total_pages = math.ceil(total_chunks / page_size) if total_chunks > 0 else 1

    return {
        "chunks": [
            {
                "id": chunk.id,
                "document_id": chunk.document.id,
                "document_path": chunk.document.relative_path,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "text_length": chunk.text_length,
                "page_metadata": chunk.page_metadata,
                "created_at": chunk.created_at,
                "updated_at": chunk.updated_at,
            }
            for chunk in chunks
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total_chunks,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_previous": page > 1,
        },
        "search": {
            "query": q,
            "is_search": q is not None,
        },
    }


class RAGAgent:
    def __init__(self, model: str, tools: dict):
        self.model = model
        self.tools = tools
        pass

    def chat(self, message: str):
        
        # ask 
        

        response: ChatResponse = chat(
            model=self.model,
            messages=messages,
            tools=self.tools.values(),  # Python SDK supports passing tools as functions
            stream=True,
        )

@api.post("/chat", response={200: None, 400: ChatError, 500: ChatError})
async def chat_stream_endpoint(request):
    """Streaming chat endpoint with tool calls support"""

    try:
        # Parse request body
        body = json.loads(request.body)
        if not body or "message" not in body:
            return JsonResponse({"error": "Missing 'message' field"}, status=400)

        message = body["message"]

        # Generate a unique chat request ID for this request
        chat_request_id = str(uuid.uuid4())

        # Prepare messages for Ollama
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]

        def generate_response():
            # Local counter for tool calls within this request
            local_call_counter = 0

            try:
                response: ChatResponse = chat(
                    model=MODEL,
                    messages=messages,
                    tools=TOOLS.values(),  # Python SDK supports passing tools as functions
                    stream=True,
                )

                for chunk in response:
                    # Prepare response data
                    reply = chunk.message.content or ""
                    yield f"reply: {json.dumps(reply)}\n"

                    # Add tool calls if present
                    if chunk.message.tool_calls:
                        for call in chunk.message.tool_calls:
                            # Generate unique call ID using chat_request_id + local counter
                            local_call_counter += 1
                            call_id = f"{chat_request_id}"

                            tool_call = {
                                "id": call_id,
                                "function": call.function.name,
                                "arguments": call.function.arguments,
                            }
                            yield f"tool_call_started: {json.dumps(tool_call)}\n"

                            # Execute tool call synchronously in generator
                            import asyncio

                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                tool_response_value = loop.run_until_complete(
                                    TOOLS[call.function.name](**call.function.arguments)
                                )
                            finally:
                                loop.close()

                            tool_response = {
                                "id": call_id,
                                "value": tool_response_value,
                            }
                            yield f"tool_call_response: {json.dumps(tool_response)}\n"

            except Exception as e:
                yield f"error: {str(e)}\n"

        return StreamingHttpResponse(
            generate_response(), content_type="text/event-stream"
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@api.get("/documents/{document_id}/marker", response=MarkerResponse)
async def get_document_marker(request, document_id: int):
    document = await Document.objects.aget(id=document_id)

    if document.markdown_chunks_openai:
        return document.markdown_chunks_openai

    from marker.converters.pdf import PdfConverter
    from marker.models import create_model_dict
    from marker.config.parser import ConfigParser

    config = {
        "output_format": "chunks",
        # "use_llm": True,
        # "ollama_model": "gpt-oss:20b",
        # "ollama_model": "qwen3:0.6b",
        # "llm_service": "marker.services.ollama.OllamaService",
        # "openai_api_key": "",
        # "llm_service": "marker.services.openai.OpenAIService",
    }
    config_parser = ConfigParser(config)

    converter = PdfConverter(
        config=config_parser.generate_config_dict(),
        artifact_dict=create_model_dict(),
        processor_list=config_parser.get_processors(),
        renderer=config_parser.get_renderer(),
        llm_service=config_parser.get_llm_service(),
    )
    rendered = converter(str(document.source_pdf_path))
    json_data = rendered.model_dump_json()
    d = json.loads(json_data)
    document.markdown_chunks_openai = d
    await document.asave()
    return d


def document_view(request, document_id):
    """Render a document as HTML with markdown conversion and navigation"""
    try:
        # Get the document
        document = get_object_or_404(Document, id=document_id)

        # Convert markdown to HTML
        md = markdown.Markdown(
            extensions=["toc", "codehilite", "fenced_code", "tables"]
        )
        html_content = md.convert(document.markdown)

        # Get table of contents if available
        toc = document.table_of_contents if document.table_of_contents else []

        # Get navigation (previous and next documents)
        all_docs = Document.objects.all().order_by("relative_path")
        doc_list = list(all_docs)

        try:
            current_index = doc_list.index(document)
            prev_doc = doc_list[current_index - 1] if current_index > 0 else None
            next_doc = (
                doc_list[current_index + 1]
                if current_index < len(doc_list) - 1
                else None
            )
        except ValueError:
            prev_doc = None
            next_doc = None

        chunks = Chunk.objects.filter(document=document).order_by("chunk_index")

        page_range = range(document.num_pages)

        context = {
            "document": document,
            "chunks": chunks,
            "html_content": html_content,
            "toc": toc,
            "prev_doc": prev_doc,
            "next_doc": next_doc,
            "page_range": page_range,
        }

        return render(request, "api/document.html", context)

    except Exception as e:
        raise Http404(f"Document not found: {str(e)}")


def document_list_view(request):
    """List all available documents"""
    documents = Document.objects.all().order_by("relative_path")
    context = {
        "documents": documents,
    }
    return render(request, "api/document_list.html", context)


def pdf_page_image_view(request, document_id, page_index):
    """
    Serve a PDF page as a JPEG image

    GET /documents/<id>/page/{index}.jpg?width=256

    Args:
        document_id: The document ID
        page_index: The page index (0-based)
        width: Optional query parameter for image width
    """
    try:
        # Get the document
        document = get_object_or_404(Document, id=document_id)

        # Construct PDF path
        pdf_path = settings.BASE_DIR / document.relative_path.replace(".md", ".pdf")

        # Check if PDF file exists
        if not pdf_path.exists():
            raise Http404("PDF file not found")

        # Get width parameter
        width = request.GET.get("width")
        if width:
            try:
                width = int(width)
                if width <= 0:
                    width = None
            except ValueError:
                width = None

        # Open PDF and get the specified page
        doc = fitz.open(str(pdf_path))

        try:
            # Check if page index is valid
            if page_index < 0 or page_index >= doc.page_count:
                raise Http404(
                    f"Page {page_index} not found. Document has {doc.page_count} pages."
                )

            # Load the page
            page = doc.load_page(page_index)

            # Get the pixmap
            if width:
                # Calculate scale factor for efficient resizing
                # Get original page dimensions
                rect = page.rect
                original_width = rect.width
                scale_factor = width / original_width

                # Create transformation matrix for scaling
                mat = fitz.Matrix(scale_factor, scale_factor)
                pix = page.get_pixmap(matrix=mat)
            else:
                # Use full resolution
                pix = page.get_pixmap()

            # Convert to PIL Image for JPEG conversion
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            # Convert to RGB if necessary (for JPEG compatibility)
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Save to bytes buffer as JPEG
            img_buffer = io.BytesIO()
            img.save(img_buffer, format="JPEG", quality=85, optimize=True)
            img_buffer.seek(0)

            # Create HTTP response
            response = HttpResponse(img_buffer.getvalue(), content_type="image/jpeg")
            response["Content-Disposition"] = (
                f'inline; filename="page_{page_index}.jpg"'
            )
            response["Cache-Control"] = "public, max-age=3600"  # Cache for 1 hour

            return response

        finally:
            doc.close()

    except Http404:
        raise
    except Exception as e:
        raise Http404(f"Error processing PDF page: {str(e)}")


def pdf_page_view(request, document_id, page_number):
    """
    Render a single PDF page with navigation buttons

    GET /pdf/<document_id>/<page_number>

    Args:
        document_id: The document ID
        page_number: The page number (1-based)
    """
    try:
        # Get the document
        document = get_object_or_404(Document, id=document_id)

        # Convert page_number to 0-based index for internal use
        page_index = page_number - 1

        # Validate page number
        if page_index < 0 or page_index >= document.num_pages:
            raise Http404(
                f"Page {page_number} not found. Document has {document.num_pages} pages."
            )

        # Get navigation (previous and next documents)
        all_docs = Document.objects.all().order_by("relative_path")
        # XXX Don't do this...
        doc_list = list(all_docs)

        try:
            current_doc_index = doc_list.index(document)
            prev_doc = (
                doc_list[current_doc_index - 1] if current_doc_index > 0 else None
            )
            next_doc = (
                doc_list[current_doc_index + 1]
                if current_doc_index < len(doc_list) - 1
                else None
            )
        except ValueError:
            prev_doc = None
            next_doc = None

        # Calculate previous and next pages
        prev_page = page_number - 1 if page_number > 1 else None
        next_page = page_number + 1 if page_number < document.num_pages else None

        context = {
            "document": document,
            "page_number": page_number,
            "page_index": page_index,
            "prev_doc": prev_doc,
            "next_doc": next_doc,
            "prev_page": prev_page,
            "next_page": next_page,
        }

        return render(request, "api/pdf_page.html", context)

    except Http404:
        raise
    except Exception as e:
        raise Http404(f"Error loading PDF page: {str(e)}")


def chunk_lengths_histogram(request):
    """
    Generate a histogram of chunk lengths as a PNG image

    GET /stats/chunk_lengths.png
    """
    try:
        # Get all chunk lengths from the database
        chunk_lengths = list(Chunk.objects.values_list("text_length", flat=True))

        if not chunk_lengths:
            raise Http404("No chunks found in database")

        # Create the histogram
        plt.figure(figsize=(12, 8))
        plt.hist(chunk_lengths, bins=50, alpha=0.7, color="skyblue", edgecolor="black")
        plt.xlabel("Chunk Length (characters)", fontsize=12)
        plt.ylabel("Frequency", fontsize=12)
        plt.title("Distribution of Chunk Lengths", fontsize=14, fontweight="bold")
        plt.grid(True, alpha=0.3)

        # Add statistics text
        mean_length = np.mean(chunk_lengths)
        median_length = np.median(chunk_lengths)
        std_length = np.std(chunk_lengths)
        min_length = np.min(chunk_lengths)
        max_length = np.max(chunk_lengths)

        stats_text = f"Mean: {mean_length:.1f}\nMedian: {median_length:.1f}\nStd: {std_length:.1f}\nMin: {min_length}\nMax: {max_length}"
        plt.text(
            0.02,
            0.98,
            stats_text,
            transform=plt.gca().transAxes,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

        # Save to bytes buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=150, bbox_inches="tight")
        buffer.seek(0)
        plt.close()  # Close the figure to free memory

        # Create HTTP response
        response = HttpResponse(buffer.getvalue(), content_type="image/png")
        response["Content-Disposition"] = (
            'inline; filename="chunk_lengths_histogram.png"'
        )
        response["Cache-Control"] = "public, max-age=3600"  # Cache for 1 hour

        return response

    except Exception as e:
        raise Http404(f"Error generating histogram: {str(e)}")


def marker_chunks_view(request, document_id: int):
    document = get_object_or_404(Document, id=document_id)
    print("---", document.markdown_chunks_openai.keys())

    page_chunks = []
    current_page = []
    for block in document.markdown_chunks_openai["blocks"]:
        if block["block_type"] == "PageFooter":
            # print("---////", block)
            if len(current_page) > 0:
                page_chunks.append(current_page)
            current_page = []
        elif block["block_type"] == "PageHeader":
            # print("---", block)
            continue
        else:
            current_page.append(block)
    page_chunks.append(current_page)
    print("---", len(page_chunks))
    # assert len(page_chunks) == document.num_pages, (
    #    f"Expected {document.num_pages} pages, got {len(page_chunks)}"
    # )

    if document.num_pages > len(page_chunks):
        page_chunks = page_chunks + [[]] * (document.num_pages - len(page_chunks))

    range_pages = range(document.num_pages)

    return render(
        request,
        "api/marker_chunks.html",
        {
            "document": document,
            "range_pages": range_pages,
            "page_chunks": page_chunks,
        },
    )
