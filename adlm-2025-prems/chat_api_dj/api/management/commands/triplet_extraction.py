import spacy
from triplet_extract import OpenIEExtractor
from django.core.management.base import BaseCommand
from django.db import transaction
from tqdm import tqdm

from api.models import Chunk
from graph.models import Node, NodeChunk, Relationship


class Command(BaseCommand):
    help = "Extract triplets from chunks"

    def handle(self, *args, **options):
        nlp = spacy.load("en_core_web_trf")

        extractor = OpenIEExtractor(
            nlp=nlp,
            enable_clause_split=True,
            enable_entailment=True,
            min_confidence=0.5,
            # deepsearch features would be nice but with spacy it requires
            # an older cupy-cuda12 which has some conflicting
            # dependencies. It's fast enough as is.
            #deep_search=True,
            #gpu_batch_size=128
        )

        chunks = Chunk.objects.filter(
            is_active=True,
            page_metadata__parser='marker-chunks'
        )
        print(f'Found {chunks.count()} total chunks')

        processed_chunks = Chunk.objects.filter(
            is_active=True,
            nodes__isnull=False,
        ).distinct()
        print(f'Found {processed_chunks.count()} processed chunks')

        unprocessed_chunks = chunks.difference(processed_chunks)
        print(f'Found {unprocessed_chunks.count()} unprocessed chunks')

        for chunk in tqdm(unprocessed_chunks, desc="Processing chunks"):
            doc = nlp(chunk.text.strip())
            for sent in doc.sents:
                if sent.text.strip() == '':
                    continue

                try:
                    triplets = extractor.extract_triplet_objects(sent.text)
                except Exception as e:
                    print(f'Error extracting triplets: {e}')
                    print(f'Text: {sent.text}')
                    continue

                with transaction.atomic():

                    prepared_triplets = []
                    for triplet in triplets:
                        left_name = ' '.join(triplet.subject.split()).lower()
                        right_name = ' '.join(triplet.object.split()).lower()
                        relation_name = ' '.join(triplet.relation.split()).lower()
                        prepared_triplets.append((left_name, relation_name, right_name))

                    # Need some deduplication, since the name normalization above may lead to duplicates within a sentence
                    prepared_triplets = list(set(prepared_triplets))

                    for left_name, relation_name, right_name in prepared_triplets:
                        #print(f'({repr(left_name)}, {repr(relation_name)}, {repr(right_name)})')

                        left_node, created = Node.objects.get_or_create(
                            name=triplet.subject,
                            kind='entity',
                        )
                        left_node_chunk, created = NodeChunk.objects.get_or_create(
                            node=left_node,
                            chunk=chunk,
                        )
                        right_node, created = Node.objects.get_or_create(
                            name=triplet.object,
                            kind='entity',
                        )
                        right_node_chunk, created = NodeChunk.objects.get_or_create(
                            node=right_node,
                            chunk=chunk,
                        )

                        relationship, rel_created = Relationship.objects.get_or_create(
                            left_node=left_node,
                            right_node=right_node,
                            relationship=triplet.relation,
                        )
                        if not rel_created:
                            relationship.weight += 1
                            relationship.save()
