from django.core.management.base import BaseCommand
from tqdm import tqdm
from django.db import transaction
import spacy
from nltk.stem.porter import *


from graph.models import Entity, Node

class Command(BaseCommand):
    help = "Populate entities for all chunks"

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', default=False)

    def handle(self, *args, **options):
        n_batches = 1
        batch_size = 100

        reset = options.get('reset', False)
        if reset:
            reset_results = Entity.objects.all().delete()
            print('Deleted all entities', reset_results)

        nlp = spacy.load("en_core_web_trf")
        stemmer = PorterStemmer()

        nodes = Node.objects.filter(
            entity__isnull=True
        )
        total_nodes = nodes.count()
        for i in tqdm(range(0, total_nodes, batch_size), desc="Processing batches"):
            batch = nodes[i:i + batch_size]
            with transaction.atomic():
                node_updates = []
                for node in batch:
                    name = node.name.lower().strip()
                    nlpd_name = nlp(node.name)
                    lemmatized = [token.lemma_ for token in nlpd_name]
                    stemmed = " ".join([stemmer.stem(token) for token in lemmatized])
                    #print('name:', name, 'lemmatized:', lemmatized, 'stemmed:', stemmed)
                    entity, created = Entity.objects.get_or_create(name=stemmed)
                    node.entity = entity
                    node_updates.append(node)

                if node_updates:
                    Node.objects.bulk_update(node_updates, ['entity'])