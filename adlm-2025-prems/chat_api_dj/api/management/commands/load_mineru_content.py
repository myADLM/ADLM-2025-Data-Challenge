import json
from collections import defaultdict
from pprint import pprint
from pathlib import Path

from django.core.management.base import BaseCommand
import pandas as pd
from tqdm import tqdm
from django.db import transaction
from django.core.files import File
import django.db.utils

from api.models import Document, Chunk

BLOCK_TYPE_MAP = {
    'table': 'Table',
    'text': 'Text',
    'image': 'Picture',
    'equation': 'Equation',
}

class Command(BaseCommand):
    help = "One-off; Load the mineru content into the database"

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', default=False)

    def handle(self, *args, **options):
        limit = 100

        df = pd.read_parquet('/mnt/ri_share/Data/31623/hf/adlm25/data/documents.parquet')
        #print(df.columns)
        #print(df.shape)

        reset = options.get('reset')

        mineru_root_dir = Path('/mnt/ri_share/Data/31623/adlm25-LabDocs-mineru')

        # for now just delete chunks that have mineru content (they'll get regenerated)
        if reset:
            print('Deleting all mineru chunks')
            print(Chunk.objects.filter(page_metadata__parser='mineru').delete())

        existing_mineru_docs = Document.objects.filter(mineru_markdown__isnull=False)
        existing_mineru_docs_ids = existing_mineru_docs.values_list('id', flat=True)

        print(f'Found {df.shape[0]} total mineru documents, {len(existing_mineru_docs_ids)} already loaded')
        print(f'`{df.shape[0]} total - {len(existing_mineru_docs_ids)} existing` new mineru documents to load')
        df = df[~df['id'].isin(existing_mineru_docs_ids)]
        print(f'Starting to load {len(df)} new mineru documents')

        if limit is not None and limit < df.shape[0]:
            print(f'Loading {limit} of {df.shape[0]} new mineru documents')
            df = df[:limit]

        new_chunks = 0
        with tqdm(total=df.shape[0]) as pbar:
            for idx, row in df.iterrows():
                #print('--row', row['relative_path'])
                doc = Document.objects.get(
                    relative_path=row['relative_path']
                )

                mineru_markdown = row['mineru_markdown']
                mineru_markdown = mineru_markdown.replace("\00", " ")
                mineru_markdown = mineru_markdown.replace("\x00", " ")

                mineru_content = row['mineru_content']
                mineru_content = mineru_content.replace("\00", " ")
                mineru_content = mineru_content.replace("\x00", " ")
                mineru_content = mineru_content.replace("\u0000", " ")
                mineru_content = json.loads(mineru_content)

                doc.mineru_markdown = mineru_markdown
                doc.mineru_json_content = mineru_content
                try:
                    doc.save()
                except Exception as e:
                    print('Error saving mineru content', row['relative_path'], e)
                    with open(f'mineru_content_error.json', 'w') as f:
                        json.dump(mineru_content, f)
                    doc.mineru_json_content = []
                    doc.save()
                    continue

                mineru_path_name = row['relative_path'] \
                    .replace('.pdf', '') \
                    .replace('LabDocs/', '')
                doc_name = Path(mineru_path_name).stem

                mineru_doc_dir = mineru_root_dir / mineru_path_name / doc_name / 'auto'

                if not mineru_doc_dir.exists():
                    raise ValueError(f'Mineru directory does not exist: {mineru_doc_dir}')

                for chunk_idx, block in enumerate(mineru_content):

                    chunk_type = BLOCK_TYPE_MAP[block['type']]
                    chunk_text = None
                    page_metadata = {
                        'parser': 'mineru',
                    }

                    #print('--block', block)
                    if chunk_type == 'Text':
                        chunk_text = block['text']
                        if 'text_level' in block:
                            page_metadata['text_level'] = block['text_level']
                    elif chunk_type == 'Equation':
                        chunk_text = block['text']
                        page_metadata['img_path'] = block['img_path']
                        page_metadata['text_format'] = block['text_format']
                    elif chunk_type == 'Table':
                        if 'table_body' not in block:
                            continue
                        chunk_text = block['table_body']
                        page_metadata['img_path'] = block['img_path']
                        page_metadata['table_caption'] = block['table_caption']
                        page_metadata['table_footnote'] = block['table_footnote']
                    elif chunk_type == 'Picture':
                        chunk_text = ''
                        page_metadata['img_path'] = block['img_path']
                        page_metadata['image_caption'] = block['image_caption']
                        page_metadata['image_footnote'] = block['image_footnote']
                    else:
                        raise ValueError('Unreachable')

                    #print('---image path', page_metadata.get('img_path', None))

                    chunk, created = Chunk.objects.get_or_create(
                        document=doc,
                        chunk_index=chunk_idx,
                        text=chunk_text,
                        text_length=len(chunk_text),
                        page_metadata=page_metadata,
                        bbox=block.get('bbox', []),
                        is_active=True,
                        block_type=chunk_type,
                        page_idx=block['page_idx'],
                    )

                    chunk_image_path = None
                    if 'img_path' in page_metadata and page_metadata['img_path'] is not None and page_metadata['img_path'] != '':
                        chunk_image_path = mineru_doc_dir / page_metadata['img_path']
                        if not chunk_image_path.exists():
                            raise ValueError(f'Chunk image path does not exist: {chunk_image_path}')
                    if chunk_image_path:
                        with open(chunk_image_path, 'rb') as f:
                            djangofile = File(f)
                            chunk.image.save(chunk_image_path.name, djangofile)

                    new_chunks += 1

                pbar.update(1)
                pbar.set_description(f'New chunks: {new_chunks}')


