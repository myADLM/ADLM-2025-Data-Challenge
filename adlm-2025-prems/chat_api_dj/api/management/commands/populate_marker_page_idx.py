from django.core.management.base import BaseCommand
from tqdm import tqdm

from api.models import Chunk

def get_page_idx(chunk):
    page_metadata = chunk.page_metadata
    section_hierarchy = page_metadata['section_hierarchy']
    values = list(section_hierarchy.values())
    if len(values) == 0:
        return None
    section_hierarchy_parts = values[0].split('/')
    page_idx = section_hierarchy_parts[2]
    return int(page_idx)

class Command(BaseCommand):
    help = 'Populate the page_idx field for all markers'

    def handle(self, *args, **options):
        chunks = Chunk.objects.filter(
            page_metadata__parser='marker-chunks',
            page_idx__isnull=True,
        ).only('id', 'page_metadata')
        for chunk in tqdm(chunks):
            try:
                chunk.page_idx = get_page_idx(chunk)
                chunk.save()
            except Exception as e:
                print(f'Error getting page idx for chunk {chunk.id}: {e}')