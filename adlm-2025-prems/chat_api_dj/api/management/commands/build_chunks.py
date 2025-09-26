import json

from django.core.management.base import BaseCommand
from tqdm import tqdm
from bs4 import BeautifulSoup

from api.models import Document, Chunk

class Command(BaseCommand):
    help = "Build chunks from documents"

    def handle(self, *args, **options):
        print("Building chunks from documents")

        Chunk.objects.all().delete()
        print("Deleted all chunks")


        for document in tqdm(Document.objects.all()):
            db_chunks = []
            marker_chunks = document.markdown_chunks_openai
            for idx, chunk in enumerate(marker_chunks['blocks']):
                html_text = chunk['html']

                if chunk['block_type'] == "Table":
                    # Leave tables undisturbed for now
                    text = html_text
                else:
                    soup = BeautifulSoup(html_text)
                    text = soup.get_text()

                db_chunks.append(
                    Chunk(
                        document=document,
                        text=text,
                        text_length=len(text),
                        page_metadata={
                            "parser": "marker-chunks",
                            "block_type": chunk['block_type'],
                            "section_hierarchy": chunk['section_hierarchy'],
                        },
                        chunk_index=idx,
                        bbox=chunk['bbox'],
                    )
                )
            Chunk.objects.bulk_create(db_chunks)
