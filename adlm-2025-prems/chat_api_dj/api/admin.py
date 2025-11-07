from django.contrib import admin
from .models import Document, Chunk, Labels


@admin.register(Labels)
class LabelsAdmin(admin.ModelAdmin):
    list_display = ("label", "created_at", "updated_at")
    search_fields = ("label", "description")
    list_filter = ("created_at", "updated_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("relative_path", "created_at", "updated_at")
    search_fields = ("relative_path",)
    list_filter = ("created_at", "updated_at")
    ordering = ("-created_at",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "source_pdf",
        "table_of_contents",
        "page_stats",
        "marker_markdown_plain",
        "marker_markdown_chunks_plain",
        "mineru_markdown",
        "mineru_json_content",
        "nougat_markdown",
    )


@admin.register(Chunk)
class ChunkAdmin(admin.ModelAdmin):
    list_display = (
        "document",
        "chunk_index",
        "text_length",
        "created_at",
        "updated_at",
    )
    search_fields = ("document__relative_path", "text")
    list_filter = ("created_at", "updated_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at", "text", "text_length")
    raw_id_fields = ("document",)
