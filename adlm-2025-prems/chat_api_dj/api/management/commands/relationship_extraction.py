import json

from django.core.management.base import BaseCommand
from django.utils import timezone
from tqdm import tqdm

from api.llm import QwenLLM, OllamaLLM, OpenAILLM
from api.models import Chunk
from graph.models import Node, Relationship


RELATIONSHIP_SYSTEM_PROMPT = """
You ar an expert linguist that extracts relationships between named
entities from text. You will be given a chunk of text as well as the 
entities that were extracted from it and you will need to connect the
entities to each other by their relationships.

Respond with a JSON list of triples, with each triple representing a relationship in the RDF graph.
Pay attention to the following requirements:
- Each triple should contain at least one, but preferably two, of the named entities in the list for each
passage.
- Clearly resolve pronouns to their specific names to maintain clarity.

Examples:

Chunk: ```
Note: The table only includes results with detectable analyte. SD = standard deviation. CV(%) = percent coefficient of variation
```
Entities: ['table', 'detectable analyte', 'standard deviation', 'percent coefficient of variation', 'detectable analyte', 'SD', 'CV(%)']

[
    ["detectable analyte", "is in", "table"],
    ["SD", "equals", "standard deviation"],
    ["CV(%)", "equals", "percent coefficient of variation"],
    ["percent coefficient of variation", "is in", "table"],
    ["standard deviation", "is in", "table"],
]

Chunk: ```
A stock solution is prepared for the new commercial calibrator lot by gravimetrically adding 
Methylenedioxymethamphetamine to stock solution at target concentration. The stock solution 
concentration is verified by comparing them to the Master Pool assigned bottle values.
```
Entities: ['stock solution', 'Methylenedioxymethamphetamine', 'target concentration', 'Master Pool assigned bottle values']

[
    ["stock solution", "is prepared for", "new commercial calibrator lot"],
    ["Methylenedioxymethamphetamine", "is added to", "stock solution"],
    ["Methylenedioxymethamphetamine", "is a", "stimulant"],
    ["Methylenedioxymethamphetamine", "is a", "drug"],
    ["target concentration", "is verified by", "comparison"],
    ["target concentration", "is compared to", "Master Pool assigned bottle values"],
]

Chunk: ```
Specimens that are hemolyzed, lipemic, or icteric. •Specimens collected in anticoagulants other than heparin or EDTA. 
•Specimens that are not labeled appropriately with patient identification. •  EQUIPMENT, REAGENTS, AND SUPPLIES 1.ELISA 
reader and washer •Pipettes and tips •Plate shaker •Incubator •Appropriate ELISA kit for Anti-Phosphatidylcholine Antibodies 
(commercially available, e.g., from a certified supplier) •Positive and negative control sera •Deionized or distilled water 
•Laboratory tubes and racks •Personal protective equipment (PPE) •
```
Entities: ['ELISA reader and washer', 'Pipettes and tips', 'Plate shaker', 'Incubator', 
'ELISA kit for Anti-Phosphatidylcholine Antibodies', 'Positive and negative control sera', 
'Deionized or distilled water', 'Laboratory tubes and racks', 'Personal protective equipment (PPE)']

[
    ["Specimens", "if conditionally", "hemolyzed"],
    ["Specimens", "if conditionally", "lipemic"],
    ["Specimens", "if conditionally", "icteric"],
    ["Specimens", "collected in", "anticoagulants other than heparin or EDTA"],
    ["Specimens", "not labeled appropriately with", "patient identification"],
    ["ELISA", "is a", "reader"],
    ["ELISA", "is a", "washer"],
    ["ELISA", "is a", "kit"],
    ["ELISA", "tests for", "Anti-Phosphatidylcholine Antibodies"],
    ["PPE", "is an initialism of", "personal protective equipment"],
]

Chunk: ```
The Xpert vanA test is an automated in vitro diagnostic test for the qualitative detection of the 
vanA gene sequence associated with vancomycin resistance in bacteria obtained directly from rectal 
swab specimens. The specimen is collected on a double swab, one of which is placed in a tube 
containing sample reagent. Following brief vortexing, the content of the sample reagent is  
transferred to the uniquely labeled Sample Chamber of a disposable fluidic cartridge (the Xpert  
vanA cartridge). The user initiates a test from the user interface of the GeneXpert® instrument  
system platform and places the cartridge with sample into the GeneXpert® instrument system  
which performs hands-off real-time, multiplex polymerase chain reaction (PCR) for the detection  
of vanA DNA.
```

Entities: ['Xpert vanA test', 'automated in vitro diagnostic test', 'vanA gene sequence', 
'vancomycin resistance', 'rectal swab specimens', 'disposable fluidic cartridge', 
'GeneXpert® instrument system platform', 'PCR for vanA DNA', 'real-time, multiplex polymerase chain reaction', 
'user interface']

[
    ["Xpert vanA test", "is an", "automated in vitro diagnostic test"],
    ["Xpert vanA test", "detects", "the vanA gene sequence"],
    ["Xpert vanA test", "detects", "the gene sequence associated with vancomycin resistance"],
    ["Xpert vanA test", "tests specimens of", "bacteria"]
    ["Xpert vanA test", "uses", "rectal swab specimens"],
    ["specimens", "are collected on a", "double swab"],
    ["the tube", "contains", "sample reagent"],
    ["sample reagent", "is briefly", "vortexed"],
    ["sample reagent", "is transferred", "the uniquely labeled Sample Chamber of a disposable fluidic cartridge"],
    ["the vanA cartridge", "is a", "disposable fluidic cartridge"],
    ["the user", "initiates", "the GeneXpert® instrument system"],
    ["the GeneXpert® instrument system", "performs", "PCR"],
    ["PCR", "is an initialism of", "polymerase chain reaction"],
    ["the GeneXpert® instrument system", "detects", "vanA DNA"],
    ["vanA DNA", "is detected by", "multiplex polymerase chain reaction"],
]

"""

def extract_relationships(text: str, entities: list, llm: QwenLLM):
    prompt = f"""
    Chunk: ```{text}```
    Entities: {entities}
    """
    response_text = llm.chat(
        prompt, 
        stream=False, 
        system_prompt=RELATIONSHIP_SYSTEM_PROMPT
    )
    response_text = next(response_text).content
    print('---response_text', response_text)
    if response_text.startswith('```json'):
        response_text = response_text[7:]
    if response_text.startswith('```'):
        response_text = response_text[3:]
    if response_text.endswith('```'):
        response_text = response_text[:-3]
    response_list = json.loads(response_text)
    return response_list

class Command(BaseCommand):
    help = "Extract relationships between named entities from chunks"

    def add_arguments(self, parser):
        parser.add_argument('--device', type=str, default='cuda:0')
        parser.add_argument('--model', type=str, default='qwen')

    def handle(self, *args, **options):
        print("Extracting relationships between named entities from chunks")

        llm = OpenAILLM(model_name='openai/gpt-oss-20b')
        extraction_model = 'openai/gpt-oss-20b'
        #if options['model'] == 'qwen':
        #    llm = QwenLLM(device=options['device'])
        #    extraction_model = 'Qwen/Qwen-0.6B'
        #elif options['model'] == 'gpt-oss':
        #    llm = OllamaLLM(model_name='gpt-oss:20b')
        #    extraction_model = 'ollama/gpt-oss:20b'
        #else:
        #    raise ValueError(f'Invalid model: {options["model"]}')

        # filter only to those we haven't parsed relationships for yet
        queryset = Chunk.objects.filter(
            node__isnull=False,
            relationships_parse_failed_at__isnull=True,
            relationships_parsed_at__isnull=True,
        )
        print('---', queryset.count(), 'total chunks to process')
        queryset = queryset.order_by('?')[:10000]
        for chunk in tqdm(queryset):
            #print('---', chunk.text)
            try:
                entities = Node.objects.filter(chunk=chunk).values_list('name', flat=True)
                print('Entities:', entities)

                relationships = extract_relationships(chunk.text, entities, llm)
                print('Relationships:', relationships)
                print('-'*25)

                for triple in relationships:
                    if len(triple) != 3:
                        print('Triple is not valid:', triple)
                        print('compressing middle')
                        new_triple = [
                            triple[0], 
                            " ".join(triple[1:-1]),
                            triple[-1]
                        ]
                        triple = new_triple

                    if triple[0].lower() not in chunk.text.lower():
                        print('Left entity not in chunk:', triple)
                        continue
                    if triple[2].lower() not in chunk.text.lower():
                        print('Right entity not in chunk:', triple)
                        continue

                    left_entity, left_created = Node.objects.get_or_create(
                        name=triple[0], 
                        chunk=chunk,
                        chunk_index=chunk.text.index(triple[0]),
                        kind='entity',
                        )
                    right_entity, right_created = Node.objects.get_or_create(
                        name=triple[2], 
                        chunk=chunk,
                        chunk_index=chunk.text.index(triple[2]),
                        kind='entity',
                    )
                    Relationship.objects.create(
                        left_node=left_entity,
                        right_node=right_entity,
                        relationship_type=triple[1],
                        extraction_model=extraction_model,
                    )

                chunk.relationships_parsed_at = timezone.now()
                chunk.save()
            except Exception as e:
                print('Error:', e)
                print('-'*25)
                chunk.relationships_parse_failed_at = timezone.now()
                chunk.relationships_parse_failed_message = str(e)
                chunk.save()
                continue


