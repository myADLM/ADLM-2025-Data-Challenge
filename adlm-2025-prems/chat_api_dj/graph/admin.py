from django.contrib import admin

from graph.models import Node, Relationship

@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ("name", "kind",)
    search_fields = ("name",)
    list_filter = ("kind",)
    ordering = ("name",)
    raw_id_fields = ("chunks",)

@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ("left_node", "right_node", "relationship")
    raw_id_fields = ("left_node", "right_node")