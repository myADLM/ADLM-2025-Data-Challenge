import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

from django.core.management.base import BaseCommand
from tqdm import tqdm
from datasets import load_dataset
from api.models import Document, Chunk
from django.conf import settings
from django.contrib.auth.models import User
import fitz
import markdown


def load_document(row):
    meta = json.loads(row["marker_metadata"])
    source_file = row["relative_path"]
    with fitz.open(source_file) as doc:
        num_pages = doc.page_count
    document = Document(
        relative_path=row["relative_path"],
        markdown=row["markdown_content"],
        table_of_contents=meta["table_of_contents"],
        page_stats=meta["page_stats"],
        num_pages=num_pages,
    )
    return document


class Command(BaseCommand):
    help = "build database from source documents and marker dataset on huggingface"

    def handle(self, *args, **options):
        # Check that LabDocs directory exists
        if not Path(settings.LABDOCS_DIR).exists():
            raise FileNotFoundError(
                f"LabDocs directory {settings.LABDOCS_DIR} does not exist. Fetch the zip file and unarchive it into the python project directory."
            )

        User.objects.create_superuser(username="admin", password="admin")

        print("Loading source documents")
        marker_dataset = load_dataset("paul-english/adlm25-marker")
        train_data = marker_dataset["train"]
        n_rows = len(train_data)
        print(f"Loading {n_rows} source documents")
        with tqdm(total=n_rows) as pbar:
            all_documents = []
            with ProcessPoolExecutor(max_workers=settings.N_WORKERS) as executor:
                results = executor.map(load_document, train_data)
                for result in results:
                    all_documents.append(result)
                    pbar.update(1)
        Document.objects.bulk_create(all_documents)

        print("Building chunks from headers")
        db_chunks = []

        for document in tqdm(Document.objects.all()):
            md = markdown.Markdown(
                extensions=["toc", "codehilite", "fenced_code", "tables"]
            )
            md_doc = md.convert(document.markdown)

            # split into chunks by headers
            # [header1, text1, header2, text2, ...]
            chunks = []
            current_chunk = ""
            for line in md_doc.split("\n"):
                if line.startswith("#"):
                    chunks.append(current_chunk)
                    current_chunk = line
                else:
                    current_chunk += line
            chunks.append(current_chunk)

            for i, chunk in enumerate(chunks):
                db_chunks.append(
                    Chunk(
                        document=document,
                        text=chunk,
                        text_length=len(chunk),
                        page_metadata={},
                        chunk_index=i,
                    )
                )

        Chunk.objects.bulk_create(db_chunks)

        # Run marker with json chunks output (slow)
        for document in tqdm(Document.objects.all()):
            document.run_marker()
