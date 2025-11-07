from django.contrib import admin

from graph.models import Node, Relationship

@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ("name", "chunk", "chunk_index", "kind", "created_at", "updated_at")
    search_fields = ("name", "chunk__text")
    list_filter = ("kind", "created_at", "updated_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("chunk",)

@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ("left_node", "right_node", "relationship_type", "created_at", "updated_at")
    raw_id_fields = ("left_node", "right_node")