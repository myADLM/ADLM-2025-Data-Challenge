# TODO

"""
For all the table chunks
- convert to dataframe
- rerender as a markdown KV

"""
from io import StringIO
from django.core.management.base import BaseCommand
import pandas as pd
from tqdm import tqdm
from django.db import transaction


from api.models import Chunk

class Command(BaseCommand):
    help = "Convert table chunks to markdown KV"

    def handle(self, *args, **options):
        print("Converting table chunks to markdown KV")

        rows = []

        for chunk in tqdm(Chunk.objects.filter(
            block_type='Table',
            is_active=True,
        )):
            try:
                df = pd.read_html(StringIO(chunk.text))[0]
            except Exception as e:
                print(f'Error reading HTML, skipping: {e} {chunk.text}')
                continue
            
            rows = []

            for idx, row in df.iterrows():
                row_str = [
                    f"# Row {idx}"
                ]

                for c in df.columns:
                    value = row[c]
                    if pd.isna(row[c]):
                        continue
                    if isinstance(c, tuple):
                        c_str = " - ".join([str(el) for el in c if not str(el).startswith('Unnamed:')])
                        row_str.append(f'- **{c_str}**: {value}')
                        continue
                    if str(c).startswith('Unnamed:'):
                        row_str.append(f'- **{value}**')
                        continue
                    row_str.append(f'- **{c}**: {value}')
                row_str = "\n".join(row_str)
                rows.append(row_str)
            
            markdownkv_block = '\n\n'.join(rows)

            with transaction.atomic():

                chunk.is_active = False
                chunk.save()

                Chunk.objects.create(
                    document=chunk.document,
                    chunk_index=chunk.chunk_index,
                    text=markdownkv_block,
                    text_length=len(markdownkv_block),
                    page_metadata=chunk.page_metadata,
                    bbox=chunk.bbox,
                    is_active=True,
                    parent_chunk=chunk,
                    block_type='MarkdownKVTable',
                )