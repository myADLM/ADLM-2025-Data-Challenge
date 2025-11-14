from django.db import models
from pgvector.django import VectorField

entity_kind_choices = [
    # An extracted entity
    ('entity', 'Entity'),

    # Represents a full chunk node akin to HippoRAG's Passage nodes
    ('chunk', 'Chunk'),
]

class NodeChunk(models.Model):
    node = models.ForeignKey('graph.Node', on_delete=models.CASCADE)
    chunk = models.ForeignKey('api.Chunk', on_delete=models.CASCADE)

    def __str__(self):
        return f'<NodeChunk: {self.node.name} - {self.chunk.id}>'

class Node(models.Model):
    """
    An instance of an entity in a chunk.
    """
    name = models.CharField(max_length=1536)
    kind = models.CharField(max_length=6, choices=entity_kind_choices)
    chunks = models.ManyToManyField('api.Chunk', related_name='nodes', through='NodeChunk')
    embedding = VectorField(dimensions=1024, null=True, blank=True)

    def __str__(self):
        return self.name

class Relationship(models.Model):
    left_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='left_node')
    right_node = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='right_node')
    relationship = models.CharField(max_length=1024)
    weight = models.IntegerField(default=1)
    embedding = VectorField(dimensions=1024, null=True, blank=True)

    def __str__(self):
        return f"{self.left_node.name} - {self.relationship} - {self.right_node.name}"