from django.core.management.base import BaseCommand
from tqdm import tqdm

from api.models import Document, category_choices

class Command(BaseCommand):
    help = "Get the categories of the documents"

    def handle(self, *args, **options):
        print("Getting the categories of the documents")

        for document in tqdm(Document.objects.all()):
            #print(document.relative_path)

            category = None
            if 'Synthetic_Procedures' in document.relative_path:
                category = 'sop'
            elif 'Cardiovascular' in document.relative_path:
                category = 'cardiovascular'
            elif 'Clinical Chemistry' in document.relative_path:
                category = 'clinical_chemistry'
            elif 'Hematology' in document.relative_path:
                category = 'hematology'
            elif 'Immunology' in document.relative_path:
                category = 'immunology'
            elif 'Microbiology' in document.relative_path:
                category = 'microbiology'
            elif 'Molecular Genetics' in document.relative_path:
                category = 'molecular_genetics'
            elif 'Obstetrics/Gynecology' in document.relative_path:
                category = 'obstetrics_gynecology'
            elif 'Pathology' in document.relative_path:
                category = 'pathology'
            elif 'Toxicology' in document.relative_path:
                category = 'toxicology'
            else:
                raise ValueError('Unreachable')

            document.category = category
            document.save()
