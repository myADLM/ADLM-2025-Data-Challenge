from django.core.management.base import BaseCommand
from tqdm import tqdm
import ollama
from sentence_transformers import SentenceTransformer

from api.models import Chunk


class Command(BaseCommand):
    help = "Populate embeddings for all chunks"

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            type=int,
            default=16,
            help='Number of chunks to process in each batch'
        )
        parser.add_argument(
            '--model',
            type=str,
            #default='bge-m3', # 1024 (use with ollama API, slow)
            #default='Qwen/Qwen3-Embedding-8B', # 4096
            default='Qwen/Qwen3-Embedding-0.6B', # 1024 shape
            help='Model to use for embeddings'
        )
        parser.add_argument(
            '--rebuild',
            action='store_true',
            default=False,
            help='Rebuild all embeddings'
        )
        # device: str = cuda:0
    
    def handle(self, *args, **options):
        batch_size = options['batch_size']
        model_name = options['model']
        rebuild = options['rebuild']

        model = SentenceTransformer(model_name)
        print('model:', model)

        if rebuild:
            chunks = Chunk.objects.all()
        else:
            chunks = Chunk.objects.filter(
                embedding__isnull=True
            )

        total_chunks = chunks.count()
        if total_chunks == 0:
            self.stdout.write(
                self.style.WARNING("No chunks found to process")
            )
            return

        self.stdout.write(
            f"Processing {total_chunks} chunks in batches of {batch_size}"
        )

        for i in tqdm(range(0, total_chunks, batch_size), desc="Processing batches"):
            batch_chunks = chunks[i:i + batch_size]

            texts = [chunk.text for chunk in batch_chunks]
            embeds = model.encode(texts)

            updated_chunks = []
            for chunk, embed in zip(batch_chunks, embeds):
                chunk.embedding_model = model_name
                chunk.embedding = embed
                updated_chunks.append(chunk)
            Chunk.objects.bulk_update(updated_chunks, ['embedding'])

            del embeds
