import os
from django.conf import settings
from django.core.management.base import BaseCommand
from tqdm import tqdm
from django.db import transaction
from django.db.models import Q

from api.llm import OpenAILLM
from api.models import Chunk

SYSTEM_PROMPT = """Laboratories generate vast amounts of documentation, ranging from protocols and package inserts to regulatory materials like 510K clearance documents and checklists. These critical resources require significant time and effort to navigate, presenting a challenge for efficient decision-making and compliance management.

Create a tool capable of quickly and accurately extracting and presenting user-requested information from these complex document stores. The proposed solution would ensure that laboratory professionals can focus on impactful work rather than time-intensive document searches.
""".strip()

def build_user_prompt_short(context_text: str, caption_text: str, footnote_text: str) -> str:
    parts = [
        "Please analyze the table in this image.",
        f"Context around the table:\n{context_text or 'Not provided.'}",
        f"Table caption:\n{caption_text or 'Not provided.'}",
        f"Table footnote:\n{footnote_text or 'Not provided.'}",
        'Provide a JSON response with the following structure: {"detailed_description": "...", "summary": "..."}',
        "Focus on extracting meaningful insights and relationships from the tabular data in the context of the surrounding content.",
    ]
    return "\n\n".join(parts)

def build_user_prompt_long(context_text: str, caption_text: str, footnote_text: str) -> str:
    parts = [
        "Please analyze the table in this image.",
        f"Context around the table:\n{context_text or 'Not provided.'}",
        f"Table caption:\n{caption_text or 'Not provided.'}",
        f"Table footnote:\n{footnote_text or 'Not provided.'}",
        (
            'Provide a JSON response with the following structure (valid JSON only; no markdown, no extra keys): '
            '{"detailed_description": "A comprehensive analysis of the table including (when applicable): '
            '- Table structure and organization '
            '- Column headers and their meanings '
            '- Key data points and patterns '
            '- Statistical insights and trends '
            '- Relationships between data elements '
            '- Significance of the data presented in relation to the surrounding context", '
            '"summary": "A concise summary of the table\'s purpose, key findings, and its relationship to the surrounding content."}'
        ),
        "Focus on extracting meaningful insights and relationships from the tabular data in the context of the surrounding content.",
    ]
    return "\n\n".join(parts)

def run_llm(
    llm,
    image_path: str,
    context_text: str = "",
    caption=None,
    footnote=None,
    user_prompt_type: str = "short",
):
    caption_text = "\n".join(caption) if isinstance(caption, (list, tuple)) else (caption or "")
    footnote_text = "\n".join(footnote) if isinstance(footnote, (list, tuple)) else (footnote or "")
    if user_prompt_type == "short":
        user_prompt = build_user_prompt_short(context_text=context_text.strip(),
                                    caption_text=caption_text.strip(),
                                    footnote_text=footnote_text.strip())
    else:
        user_prompt = build_user_prompt_long(context_text=context_text.strip(),
                                    caption_text=caption_text.strip(),
                                    footnote_text=footnote_text.strip())

    response = llm.vision(image_path=image_path, prompt=user_prompt, system_prompt=SYSTEM_PROMPT)
    return response

class Command(BaseCommand):
    help = "Run a vision model on the tables"

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', default=False)
        parser.add_argument('--user-prompt-type', type=str, default='long', choices=['short', 'long'])
        parser.add_argument('--prev-chunk-limit', type=int, default=2)
        parser.add_argument('--next-chunk-limit', type=int, default=1)

    def handle(self, *args, **options):
        print("Running a vision model on the tables")

        if options['reset']:
            print('Resetting all vision table chunks')
            print(Chunk.objects.filter(block_type='VisionTable').delete())

        llm = OpenAILLM()

        vision_tables = Chunk.objects.filter(
            block_type='VisionTable',
        )

        # find chunks from mineru that are tables (mineru creates images for any extracted tables)
        tables = Chunk.objects.filter(
            block_type='Table',
            page_metadata__parser='mineru',
        )
        print(f'Found {tables.count()} total tables')

        unprocessed_tables = tables.filter(
            ~Q(id__in=vision_tables.values_list('parent_chunk_id', flat=True))
        ).order_by("?")

        print(f'Found {unprocessed_tables.count()} unprocessed tables')

        for table_chunk in tqdm(unprocessed_tables):
            if 'img_path' not in table_chunk.page_metadata:
                print(f'Table chunk {table_chunk.id} has no image path, skipping')
                continue

            # remove leading slash so the abs path join works
            rel_img_path = table_chunk.image.url[1:]
            abs_img_path = settings.BASE_DIR / rel_img_path

            if not abs_img_path.exists():
                print(f'Table chunk {table_chunk.id} image path does not exist, skipping: {abs_img_path}')
                continue
            
            chunk_idx = table_chunk.chunk_index

            # Find prev & next chunks for context
            prev_chunks = Chunk.objects.filter(
                is_active=True,
                document=table_chunk.document,
                chunk_index__lt=chunk_idx,
                page_metadata__parser='mineru',
            ).order_by('-chunk_index')[:options['prev_chunk_limit']]
            prev_texts = [
                chunk.text for chunk in prev_chunks
            ]

            next_chunks = Chunk.objects.filter(
                is_active=True,
                document=table_chunk.document,
                chunk_index__gt=chunk_idx,
                page_metadata__parser='mineru',
            ).order_by('chunk_index')[:options['next_chunk_limit']]
            next_texts = [
                chunk.text for chunk in next_chunks
            ]

            context_chunks = []
            if prev_texts and len(prev_texts) > 0:
                context_chunks.append("Previous text:\n" + "\n\n".join(prev_texts))
            if next_texts and len(next_texts) > 0:
                context_chunks.append("Following text:\n" + "\n\n".join(next_texts))

            context_text = "\n\n".join(context_chunks)

            print(f'Context text length: {len(context_text)}')

            try:
                response_text = run_llm(
                    llm=llm,
                    image_path=abs_img_path,
                    context_text=context_text,
                    caption=table_chunk.page_metadata['table_caption'],
                    footnote=table_chunk.page_metadata['table_footnote'],
                    user_prompt_type=options['user_prompt_type'],
                )
            except Exception as e:
                # Timeouts for large requests, maybe rerun these on ml3 or something
                print(f'Error running LLM on table chunk {table_chunk.id}: {e}')
                continue
            
            with transaction.atomic():
                table_chunk.is_active = False
                table_chunk.save()

                new_table_chunk = Chunk.objects.create(
                    document=table_chunk.document,
                    chunk_index=table_chunk.chunk_index,
                    text=response_text,
                    text_length=len(response_text),
                    page_metadata=table_chunk.page_metadata,
                    bbox=table_chunk.bbox,
                    is_active=True,
                    block_type='VisionTable',
                    parent_chunk=table_chunk,
                    page_idx=table_chunk.page_idx,
                )
            