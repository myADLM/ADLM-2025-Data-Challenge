import spacy
from tqdm import tqdm
import django
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from api.models import Chunk
from graph.models import Node

class Command(BaseCommand):
    help = "Extract named entities from chunks using Spacy"

    def handle(self, *args, **options):
        print('Spacy NER Extraction')
        nlp = spacy.load("en_core_web_trf")
        print('Loaded Spacy model')

        limit = 600

        existing = 0
        new = 0

        queryset = Chunk.objects.filter(
            ~Q(node__extraction_model='spacy/en_core_web_trf')
        )

        if limit is not None and limit < queryset.count():
            print(f'Processing {limit} of {queryset.count()} chunks')
            queryset = queryset[:limit]

        for chunk in tqdm(queryset, desc="Processing chunks", total=queryset.count()):
            try:
                doc = nlp(chunk.text)
            except Exception as e:
                print('error parsing chunk, skipping:', chunk.id, e)
                print('--', chunk.text)
                continue
            with transaction.atomic():
                for ent in doc.ents:
                    try:
                        _n, _created = Node.objects.get_or_create(
                            name=ent.text,
                            chunk=chunk,
                            chunk_index=ent.start_char,
                            kind='entity',
                            label=ent.label_,
                            extraction_model='spacy/en_core_web_trf',
                        )
                        if _created:
                            new += 1
                        else:
                            existing += 1
                    except django.db.utils.DataError as e:
                        # probably a bad entity, too long, skip it
                        print('data error, skipping', ent.text, ent.label_)
                        continue
                    except Exception as e:
                        print('unknown error, failing', ent.text, ent.label_)
                        #print(f'Error creating node: {e}')
                        raise e
        print(f'Existing: {existing}, New: {new}')
        print('done')
