from django.core.management.base import BaseCommand
from tqdm import tqdm

from graph.models import Label

class Command(BaseCommand):
    help = "Populate labels for all entities"

    def handle(self, *args, **options):
        nodes = Node.objects.filter(
            label__isnull=True
        )
        for node in tqdm(nodes):
            print(node.name)
            entity = node.entity
            print(entity.name)
            label, created = Label.objects.get_or_create(name=entity.label)
            entity.label = label
            entity.save()
            