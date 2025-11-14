from django.core.management.base import BaseCommand
from tqdm import tqdm
from api.models import Chunk
from graph.models import Node, Relationship


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
            '--reset',
            action='store_true',
            default=False,
            help='Reset all embeddings'
        )
        # device: str = cuda:0
    
    def _populate_chunks(self, chunks, llm, batch_size, limit):
        if limit is not None and limit <= 0:
            return 0

        if limit is not None and limit < chunks.count():
            chunks = chunks[:limit]

        total_chunks = chunks.count()
        if total_chunks == 0:
            self.stdout.write(
                self.style.WARNING("No chunks found to process")
            )
            return 0

        self.stdout.write(
            f"Processing {total_chunks} chunks in batches of {batch_size}"
        )

        for i in tqdm(range(0, total_chunks, batch_size), desc="Processing chunks"):
            batch_chunks = chunks[i:i + batch_size]

            texts = [chunk.text for chunk in batch_chunks]
            try:
                embeds = llm.embed_text(texts)
            except Exception as e:
                print('Error:', e)
                print('-'*25)
                continue

            updated_chunks = []
            for chunk, embed in zip(batch_chunks, embeds):
                chunk.embedding_model = llm.model_name
                chunk.embedding = embed
                updated_chunks.append(chunk)
            Chunk.objects.bulk_update(updated_chunks, ['embedding'])

        return total_chunks


    def _populate_nodes(self, nodes, llm, batch_size, limit):
        if limit is not None and limit <= 0:
            return 0

        if limit is not None and limit < nodes.count():
            nodes = nodes[:limit]

        total_nodes = nodes.count()
        if total_nodes == 0:
            self.stdout.write(
                self.style.WARNING("No nodes found to process")
            )
            return 0

        self.stdout.write(
            f"Processing {total_nodes} nodes in batches of {batch_size}"
        )

        for i in tqdm(range(0, total_nodes, batch_size), desc="Processing nodes"):
            batch_nodes = nodes[i:i + batch_size]

            texts = [node.name for node in batch_nodes]
            try:
                embeds = llm.embed_text(texts)
            except Exception as e:
                print('Error:', e)
                print('-'*25)
                continue
            updated_nodes = []
            for node, embed in zip(batch_nodes, embeds):
                node.embedding = embed
                updated_nodes.append(node)
            Node.objects.bulk_update(updated_nodes, ['embedding'])

        return total_nodes

    def _populate_relationships(self, relationships, llm, batch_size, limit):
        if limit is not None and limit <= 0:
            return 0

        if limit is not None and limit < relationships.count():
            relationships = relationships[:limit]

        total_relationships = relationships.count()
        if total_relationships == 0:
            self.stdout.write(
                self.style.WARNING("No relationships found to process")
            )
            return 0

        self.stdout.write(
            f"Processing {total_relationships} relationships in batches of {batch_size}"
        )

        for i in tqdm(range(0, total_relationships, batch_size), desc="Processing relationships"):
            batch_relationships = relationships[i:i + batch_size]

            texts = [f"({relationship.left_node.name}, {relationship.relationship_type}, {relationship.right_node.name})" for relationship in batch_relationships]
            try:
                embeds = llm.embed_text(texts)
            except Exception as e:
                print('Error:', e)
                print('-'*25)
                continue
            updated_relationships = []
            for relationship, embed in zip(batch_relationships, embeds):
                relationship.embedding = embed
                updated_relationships.append(relationship)
            Relationship.objects.bulk_update(updated_relationships, ['embedding'])

        return total_relationships


    def handle(self, *args, **options):
        batch_size = options.get('batch_size', 1)
        reset = options.get('reset')

        #from api.llm import QwenLLM
        #llm = QwenLLM(device='cuda:0')
        from api.llm import OpenAILLM
        #llm = OpenAILLM(model_name='openai/gpt-oss-20b')
        # For a realtime use case, we'll want to 
        # let the embed model use one gpu, then another
        # to use the chat model gpt-oss
        # NOTE must start LLM with this model ready
        llm = OpenAILLM(
            model_name='Qwen/Qwen3-Embedding-0.6B',
            timeout=120
        )

        task_budget = 10000000

        if reset:
            Chunk.objects.all().update(embedding=None)
            Node.objects.all().update(embedding=None)
            Relationship.objects.all().update(embedding=None)
            print('Reset embeddings')
        
        chunks = Chunk.objects.filter(
            is_active=True,
            embedding__isnull=True
        )
        task_budget -= self._populate_chunks(chunks, llm, batch_size, task_budget)

        nodes = Node.objects.filter(
            embedding__isnull=True
        )
        task_budget -= self._populate_nodes(nodes, llm, batch_size, task_budget)

        relationships = Relationship.objects.filter(
            embedding__isnull=True
        )
        task_budget -= self._populate_relationships(relationships, llm, batch_size, task_budget)