from django.db import models
from pgvector.django import VectorField

entity_kind_choices = [
    # An extracted entity
    ('entity', 'Entity'),

    # Represents a full chunk node akin to HippoRAG's Passage nodes
    ('chunk', 'Chunk'),
]

class Entity(models.Model):
    """
    More general than a node, unique on name rather
    than an instance of an entity in a chunk.
    """
    name = models.CharField(max_length=512, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    label = models.ForeignKey('graph.Label', on_delete=models.SET_NULL, null=True, blank=True)

    embedding = VectorField(dimensions=1024, null=True, blank=True)

    def __str__(self):
        return self.name

class Label(models.Model):
    """
    A label is a category of entities.

    We only have these for the spacy ner right now.
    """
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Node(models.Model):
    """
    An instance of an entity in a chunk.
    """
    name = models.CharField(max_length=255)
    chunk_index = models.IntegerField(help_text="The character index of the entity in the chunk.")
    kind = models.CharField(max_length=6, choices=entity_kind_choices)
    # XXX deprecate in favor of entity.label
    label = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    entity = models.ForeignKey(Entity, on_delete=models.SET_NULL, null=True, blank=True)

    extraction_model = models.CharField(max_length=255, help_text="The model used to extract the entity.", null=True, blank=True)

    chunk = models.ForeignKey('api.Chunk', on_delete=models.CASCADE)

    embedding = VectorField(dimensions=1024, null=True, blank=True)

    def __str__(self):
        return self.name

# TODO we need synonym entities relationships, e.g. "FDA" "is synonymous with" "Food and Drug Administration"

# TODO "Concept" that represents the label for a relationship type (normalize & stemming)
# want these cleaned up

class Relationship(models.Model):
    left_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='left_node')
    right_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='right_node')
    relationship_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    extraction_model = models.CharField(max_length=255, help_text="The model used to extract the relationship.", null=True, blank=True)

    embedding = VectorField(dimensions=1024, null=True, blank=True)

    def __str__(self):
        return f"{self.left_node.name} - {self.relationship_type} - {self.right_node.name}"