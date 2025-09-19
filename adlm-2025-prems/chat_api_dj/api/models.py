from django.db import models
from django.conf import settings
from pathlib import Path
from django.core.files import File


class Labels(models.Model):
    label = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label


class Document(models.Model):
    relative_path = models.CharField(max_length=255, unique=True, db_index=True)
    markdown = models.TextField()
    markdown_chunks_openai = models.JSONField(null=True, blank=True)
    table_of_contents = models.JSONField()
    page_stats = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    num_pages = models.IntegerField()

    def __str__(self):
        return self.relative_path

    @property
    def source_pdf_path(self):
        return settings.BASE_DIR / self.relative_path.replace(".md", ".pdf")

    @property
    def source_pdf(self):
        return open(self.source_pdf_path, "rb")

    def run_marker(self):
        if self.markdown_chunks_openai is not None:
            return

        import json
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
        rendered = converter(str(self.source_pdf_path))
        json_data = rendered.model_dump_json()
        d = json.loads(json_data)
        self.markdown_chunks_openai = d
        self.save()


class Chunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    chunk_index = models.IntegerField()
    text = models.TextField()
    text_length = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    page_metadata = models.JSONField()

    def __str__(self):
        return self.text

    def html_text(self):
        import markdown

        md = markdown.Markdown(
            extensions=["toc", "codehilite", "fenced_code", "tables"]
        )
        html_text = md.convert(self.text)
        return html_text
