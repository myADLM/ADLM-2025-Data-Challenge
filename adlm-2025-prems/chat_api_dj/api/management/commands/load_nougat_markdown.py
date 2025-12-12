from pathlib import Path

from django.core.management.base import BaseCommand

from api.models import Document
from tqdm import tqdm

class Command(BaseCommand):
    help = "Load nougat markdown into the database"

    def handle(self, *args, **options):
        print("Loading nougat markdown into the database")

        base_dir = Path('/mnt/ri_share/Data/31623/adlm25/markdown/nougat')

        for file in tqdm(base_dir.rglob('*.mmd')):
            relative_mmd_path = file.relative_to(base_dir)

            relative_pdf_path = relative_mmd_path.with_suffix('.pdf')
            relative_pdf_path = Path('LabDocs') / relative_pdf_path

            doc = Document.objects.get(relative_path=relative_pdf_path)
            doc.nougat_markdown = file.read_text()
            doc.save()

        print("Done")