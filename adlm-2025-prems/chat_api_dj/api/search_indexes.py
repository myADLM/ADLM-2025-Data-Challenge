from haystack import indexes
from .models import Document, Chunk


class DocumentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    relative_path = indexes.CharField(model_attr="relative_path")
    marker_markdown_plain = indexes.CharField(model_attr="marker_markdown_plain")
    mineru_markdown = indexes.CharField(model_attr="mineru_markdown")
    nougat_markdown = indexes.CharField(model_attr="nougat_markdown")
    num_pages = indexes.IntegerField(model_attr="num_pages")
    created_at = indexes.DateTimeField(model_attr="created_at")
    updated_at = indexes.DateTimeField(model_attr="updated_at")

    def get_model(self):
        return Document

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()


class ChunkIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    chunk_index = indexes.IntegerField(model_attr="chunk_index")
    chunk_text = indexes.CharField(model_attr="text")
    text_length = indexes.IntegerField(model_attr="text_length")
    document_path = indexes.CharField(model_attr="document__relative_path")
    document_id = indexes.IntegerField(model_attr="document__id")
    created_at = indexes.DateTimeField(model_attr="created_at")
    updated_at = indexes.DateTimeField(model_attr="updated_at")

    def get_model(self):
        return Chunk

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(is_active=True).select_related("document")
