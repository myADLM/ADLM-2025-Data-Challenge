from django.core.management.base import BaseCommand
from tqdm import tqdm

from api.models import Document


class Command(BaseCommand):
    help = "Link review to letter"

    def handle(self, *args, **options):
        print("Linking review to letter")

        for document in tqdm(Document.objects.filter(
            relative_path__contains='_REVIEW'
        )):
            letter_path = document.relative_path.replace('_REVIEW', '')
            try:
                letter_document = Document.objects.get(
                    relative_path=letter_path
                )
            except Document.DoesNotExist:
                print(f"Letter document not found for {document.relative_path}, skipping")
                continue

            letter_document.fda_review_letter = document
            letter_document.save()