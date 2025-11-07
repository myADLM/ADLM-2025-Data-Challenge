import json

from django.core.management.base import BaseCommand
from tqdm import tqdm

from api.llm import OpenAILLM
from api.models import Chunk
from graph.models import Node

LABELS= [
    'ACRONYM',
    'ADDRESS',
    'ANATOMY',
    'ANALYTICAL_METRIC',
    'ASSAY',
    'CARDINAL', 
    'CHEMICAL',
    'DATE', 
    'EMAIL',
    'EVENT', 
    'FAC', # facility
    'GPE', # geopolitical entity
    'EQUIPMENT',
    'LANGUAGE', 
    'LAW', 
    'LOC', 
    'MOLECULE',
    'MONEY', 
    'ORDINAL', 
    'ORG', 
    'PARAMETER',
    'PERCENT', 
    'PERSON', 
    'PHONE',
    'PROCEDURE',
    'PRODUCT', 
    'QUANTITY', 
    'ROLE',
    'SPECIMEN_TYPE',
    'TIME', 
    'WORK_OF_ART',
]

SYSTEM_PROMPT = f"""You're an expert computational linguist helping to label extracted
entities from text. You will be given a chunk of text and a list of
entities that were extracted from it. You will need to label each entity
with the most appropriate label. We'll provide a list of possible
labels, but you're welcome to use a label that is not in the list if it's
more appropriate.

Here are the possible labels:
{",".join(sorted(LABELS))}

Return only the JSON list of labels in the following format after the "Response:" line:
["Label 1", "Label 2", "Label 3", ...]

Return only the valid json response. Do not include any other text or commentary.

Example:
Chunk: ```
The LOB (limit of the blank), the LOD (limit of detection) and the LOQ (limit of quantitation) were determined in accordance with CLSI EP 17-A guideline, Protocols for Determina
tion of Limits of Detection).```
Entities: ['LOB', 'limit of the blank', 'LOD', 'limit of detection', 'LOQ', 'limit of quantitation', 'CLSI EP 17-A guideline', 'Protocols for Determination of Limits of Detection']

Response:

["ANALYTICAL_METRIC", "ANALYTICAL_METRIC", "ANALYTICAL_METRIC", "ANALYTICAL_METRIC", "ANALYTICAL_METRIC", "ANALYTICAL_METRIC", "STANDARD_DOCUMENT", "DOCUMENT_TITLE"]
"""

class Command(BaseCommand):
    help = "Label (name) all the entities for chunks"

    def handle(self, *args, **options):
        self.stdout.write("Labeling NER for all chunks")

        llm = OpenAILLM(model_name='openai/gpt-oss-20b')

        #unique_labels = Node.objects.values_list('label', flat=True).distinct()
        #print(f"Unique labels: {unique_labels}")

        chunks = Chunk.objects.filter(
            is_active=True,
            node__isnull=False,
            node__label__isnull=True
        ).order_by('?')
        print(f"Chunks: {chunks.count()}")
        for chunk in tqdm(chunks[:10000]):
            print(f"Chunk: {chunk.id}")
            #print(f"Chunk text: {chunk.text}")
            print(f"Chunk entities: {chunk.node_set.count()}")
            print("-"*25)

            entities = [node.name for node in chunk.node_set.all()]

            prompt = f"""Chunk: ```{chunk.text}```
Entities: [{", ".join([f"'{entity}'" for entity in entities])}]

Response:
"""
            #print(f"Prompt: {prompt}")

            responses = llm.chat(
                prompt,
                stream=False,
                system_prompt=SYSTEM_PROMPT
            )
            response = next(responses).content
            try:
                response_list = json.loads(response)
            except Exception as e:
                print(f"ERROR: {e}")
                print(f"Response: {response}")
                continue

            print(f"Entities: {entities}")
            print(f"Response: {response_list}")

            #print('-', chunk.node_set.count())
            #print('-', len(response_list))

            if chunk.node_set.count() != len(response_list):
                print('ERROR: number of entities does not match')
                continue

            for node, label in zip(chunk.node_set.all(), response_list):
                node.label = label.upper()
                node.save()
