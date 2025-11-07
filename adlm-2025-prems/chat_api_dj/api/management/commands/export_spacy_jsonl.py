import json
from pathlib import Path

from django.core.management.base import BaseCommand
from tqdm import tqdm
from django.db.models import Q

from api.models import Chunk

class Command(BaseCommand):
    help = "Export Spacy JSONL for all chunks"

    def handle(self, *args, **options):
        chunks = Chunk.objects.filter(
            Q(
                is_active=True,
                node__isnull=False,
                node__label__isnull=False,
            ),
            ~Q(node__extraction_model='spacy/en_core_web_trf'),
        )
        print(f'Processing {chunks.count()} chunks')

        output_file = Path("spacy_ner_jsonl.jsonl")
        # remove file if it exists
        if output_file.exists():
            output_file.unlink()
        output_file.touch()

        all_labels = set()

        for chunk in tqdm(chunks):
            #print(chunk.id)
            #print(chunk.text)
            #print("-"*25)

            tokens = chunk.text.split(" ")

            chunk_labeled_nodes = chunk.node_set.filter(label__isnull=False)

            if chunk_labeled_nodes.count() == 0:
                continue

            all_spans = []
            for node in chunk_labeled_nodes:
                all_spans.append({
                    "start": node.chunk_index,
                    "end": node.chunk_index + len(node.name),
                    "label": node.label,
                })
                all_labels.add(node.label)

            output = {
                "text": chunk.text,
                "spans": all_spans,
            }
            with open(output_file, "a") as f:
                f.write(json.dumps(output) + "\n")

            #from pprint import pprint
            #pprint(output)
        print(f'All labels: {all_labels}')
