import gc
import json
import uuid
import io
from typing import List, Optional, Dict, Any
from datetime import datetime
import math

from django.http import StreamingHttpResponse, JsonResponse, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from ninja import NinjaAPI, Schema
import markdown
import fitz  # PyMuPDF
from PIL import Image
import matplotlib
from asgiref.sync import sync_to_async
from haystack.query import SearchQuerySet
from pgvector.django import CosineDistance
import matplotlib.pyplot as plt
import numpy as np
from pydantic import BaseModel


from .models import Document, Chunk
from api.llm import ThinkingContent, OutputContent, OpenAILLM

matplotlib.use("Agg")  # Use non-interactive backend

# TODO just need one now each routed as it needs
embed_llm = OpenAILLM(
    model_name="Qwen/Qwen3-Embedding-0.6B",
)
chat_llm = OpenAILLM(
    model_name="openai/gpt-oss-20b",
    base_url="http://localhost:6380/v1",
)
rerank_llm = OpenAILLM(

)


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


class CitedResponse(BaseModel):
    response_text: str
    cited_chunk_ids: List[int]


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

    try:
        document = await Document.objects.aget(id=document_id)
        # Count the number of chunks for this document
        num_chunks = await sync_to_async(
            Chunk.objects.filter(
                document=document
            ).count
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
            "markdown": document.marker_markdown_plain,
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
    "/documents/{document_id}/chunks/{chunk_id}",
    response={200: ChunkDetail, 404: DocumentError},
)
async def get_document_chunk(request, document_id: int, chunk_id: int):
    """Get a specific chunk from a document"""
    try:
        document = await Document.objects.aget(id=document_id)
        chunk = await Chunk.objects.aget(
            document=document, 
            pk=chunk_id
        )
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
    def __init__(self):
        pass

    def chat(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None):

        search_query_prompt = f"""The user is asking a question. Can you create a search query to find the most 
relevant documents for this query? You may need to refer to the full conversation history to choose the 
most accurate set of documents. 

Respond with _only_ the search queries, no other text. This will be used for traditional and embedding search, don't hyphenate
(unless it's already in the user message) or do anything that will hinder the search. Return the keywords only.

Examples (user message -> search query):
- "What are some FDA approved tests relating to Von-willebrand disease?" -> "von-willebrand disease fda approved tests"

User content:
{message}
"""
        
        search_query_content = chat_llm.chat(search_query_prompt, stream=False, conversation_history=conversation_history)
        search_query_content = next(search_query_content).content
        print('LLM search query:', search_query_content)

        # embedding search
        embeddings = embed_llm.embed_text(search_query_content)
        embeddings = embeddings[0]
        embedding_search_chunks = Chunk.objects.filter(
            is_active=True
        ).order_by(CosineDistance('embedding', embeddings))[:25]
        embedding_search_chunks = [c for c in embedding_search_chunks] # convert to list
        print('Number of embedding search results:', len(embedding_search_chunks))

        # traditional search
        max_traditional_search_results = 25
        sqs = SearchQuerySet().models(Chunk).filter(
            content=search_query_content
        )[:max_traditional_search_results]
        print('Number of traditional search results:', len(sqs))
        traditional_search_chunks = [result.object for result in sqs if result.object]

        chunks = embedding_search_chunks + traditional_search_chunks

        # In-lieu of good chunking, we can just fetch the neighbors and concatenate the text.
        # Ideally we'd use a better chunking method, but this is a stopgap.
        fetch_neighbors = 3

        chunk_texts = []
        for chunk in chunks:
            text = ""
            prev_chunk = chunk
            for i in range(fetch_neighbors):
                if prev_chunk:
                    text += f"{prev_chunk.text} "
                    prev_chunk = prev_chunk.prev_chunk()
            text += f"{chunk.text} "
            next_chunk = chunk
            for i in range(fetch_neighbors):
                if next_chunk:
                    text += f"{next_chunk.text} "
                    next_chunk = next_chunk.next_chunk()
            chunk_texts.append(
                f"Chunk ID: {chunk.id}\n"
                f"Document: {chunk.document.relative_path}\n"
                f"Text:\n{text}\n"
            )
        chunk_scores = rerank_llm.rerank(search_query_content, chunk_texts)

        sorted_chunks = sorted(zip(chunk_texts, chunk_scores, chunks), key=lambda x: x[1], reverse=True)

        max_chunks = 10
        top_chunks = sorted_chunks[:max_chunks]
        top_chunk_texts = [chunk_text for chunk_text, _chunk_score, _chunk in top_chunks]

        chunk_context = "\n---\n".join(top_chunk_texts)

        # Build current user message with chunk context
        current_user_message = f"""{message}

Respond only with a proper JSON formatted response like the following:
{{
    "response_text": "The response text",
    "cited_chunk_ids": [1, 2, 3]
}}

- Don't wrap the json in any code blocks or other formatting.
- Only cite the chunks in the cited_chunk_ids list, don't cite in the response_text.

Use the chunks below to answer the question.
\n---\n
{chunk_context}
"""

        #print('-' * 100)
        #print('Final LLM conversation_history:', conversation_history)
        #print('Final LLM user message:', current_user_message)
        #print('-' * 100)

        #streaming_response = chat_llm.chat(prompt, structured_output=CitedResponse)
        # LLM will structure as: system prompt -> conversation_history -> new user message
        streaming_response = chat_llm.chat(
            prompts=current_user_message,
            conversation_history=conversation_history,
            # Structured output was causing really bad LLM output with VLLM and gpt-oss,
            # Just asking the llm to return valid json was better.
            #structured_output=CitedResponse,
            stream=False,
        )
        res = list(streaming_response)[0].content
        #print('Cited response:', res)

        cited_response = CitedResponse.model_validate_json(res)
        #print('Cited response:', cited_response)

        citation_responses = []

        for chunk in cited_response.cited_chunk_ids:
            chunk = Chunk.objects.get(id=chunk)
            citation_responses.append({
                'document_id': chunk.document.id,
                'document_path': chunk.document.relative_path,
                'page_index': chunk.page_idx,
                'bbox': chunk.bbox,
            })
        
        # Just to keep our interface consistent
        def generator():
            yield OutputContent(content=cited_response.response_text)

        return generator(), citation_responses

@api.post("/chat", response={200: None, 400: ChatError, 500: ChatError})
async def chat_stream_endpoint(request):
    """Streaming chat endpoint with tool calls support"""

    agent = RAGAgent()

    try:
        # Parse request body
        body = json.loads(request.body)
        if not body or "message" not in body:
            return JsonResponse({"error": "Missing 'message' field"}, status=400)

        message = body["message"]
        conversation_history = body.get("conversation_history", [])

        # Validate conversation_history format
        if conversation_history:
            if not isinstance(conversation_history, list):
                return JsonResponse({"error": "conversation_history must be a list"}, status=400)
            # Validate each message has role and content
            for msg in conversation_history:
                if not isinstance(msg, dict) or "role" not in msg or "content" not in msg:
                    return JsonResponse({"error": "Each message in conversation_history must have 'role' and 'content' fields"}, status=400)

        # Keep only last 6 messages (3 user + 3 assistant pairs)
        if conversation_history:
            conversation_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history

        # Generate a unique chat request ID for this request
        chat_request_id = str(uuid.uuid4())

        def generate_response():
            # Local counter for tool calls within this request
            local_call_counter = 0

            try:
                # Pass conversation_history to RAGAgent
                # The LLM will structure as: system_prompt -> conversation_history -> new user message
                response, cited_chunks = agent.chat(message, conversation_history=conversation_history)
                print('Cited chunks:', cited_chunks)

                for citation in cited_chunks:
                    yield f'cited_document: {json.dumps(citation)}\n'

                for chunk in response:
                    if isinstance(chunk, ThinkingContent):
                        #print('Thinking:', chunk.content)
                        yield f'thinking: {json.dumps(chunk.content)}\n'
                    elif isinstance(chunk, OutputContent):
                        #print('Reply:', chunk.content)
                        yield f'reply: {json.dumps(chunk.content)}\n'

            except Exception as e:
                print('Error in generate_response:', e)
                import traceback
                traceback.print_exc()
                yield f"error: {str(e)}\n"

        return StreamingHttpResponse(
            generate_response(), content_type="text/event-stream"
        )

    except Exception as e:
        print('Error in chat_stream_endpoint:', e)
        import traceback
        traceback.print_exc()
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
        html_content = md.convert(document.marker_markdown_plain)

        # Get table of contents if available
        toc = document.table_of_contents if document.table_of_contents else []

        # Get navigation (previous and next documents) - efficient query
        prev_doc = (
            Document.objects.filter(relative_path__lt=document.relative_path)
            .order_by("-relative_path")
            .first()
        )
        next_doc = (
            Document.objects.filter(relative_path__gt=document.relative_path)
            .order_by("relative_path")
            .first()
        )

        chunks = Chunk.objects.filter(
            page_metadata__parser="marker-chunks",
            document=document
        ).order_by("chunk_index")

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
    """List all available documents with pagination"""
    documents_list = Document.objects.all().order_by("relative_path")
    
    # Paginate with 25 documents per page
    paginator = Paginator(documents_list, 25)
    page = request.GET.get('page', 1)
    
    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        documents = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        documents = paginator.page(paginator.num_pages)
    
    context = {
        "documents": documents,
        "paginator": paginator,
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

        # Get navigation (previous and next documents) - efficient query
        prev_doc = (
            Document.objects.filter(relative_path__lt=document.relative_path)
            .order_by("-relative_path")
            .first()
        )
        next_doc = (
            Document.objects.filter(relative_path__gt=document.relative_path)
            .order_by("relative_path")
            .first()
        )

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

    page_chunks = []
    current_page = []
    for block in document.markdown_chunks_openai["blocks"]:
        if block["block_type"] == "PageFooter":
            if len(current_page) > 0:
                page_chunks.append(current_page)
            current_page = []
        elif block["block_type"] == "PageHeader":
            continue
        else:
            current_page.append(block)
    page_chunks.append(current_page)

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
