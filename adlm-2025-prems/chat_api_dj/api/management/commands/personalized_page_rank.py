"""

This works, it's fast for usage real-time, but uniform results currently

I think the graph is too sparse, need to review the number of unique entities, nodes, rels, etc.

TODO use embeddings for reset probability search as well

"""
from django.core.management.base import BaseCommand
import igraph as ig
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import torch
from django.db.models import Count
from torch_ppr.utils import prepare_page_rank_adjacency, validate_adjacency, power_iteration, prepare_num_nodes, sparse_diagonal

from graph.models import Node, Relationship, Entity
from api.models import Chunk

def plot_pagerank(graph: ig.Graph, p_pagerank: list[float]):
    """Plots personalized PageRank values on a grid graph with a colorbar.

    Parameters
    ----------
    graph : ig.Graph
        graph to plot
    p_pagerank : list[float]
        calculated personalized PageRank values
    """
    # Create the axis for matplotlib
    _, ax = plt.subplots(figsize=(8, 8))

    # Create a matplotlib colormap
    # coolwarm goes from blue (lowest value) to red (highest value)
    cmap = cm.coolwarm

    # Normalize the PageRank values for colormap
    normalized_pagerank = ig.rescale(p_pagerank)

    graph.vs["color"] = [cmap(pr) for pr in normalized_pagerank]
    graph.vs["size"] = ig.rescale(p_pagerank, (20, 40))
    graph.es["color"] = "gray"
    graph.es["width"] = 1.5

    # Plot the graph
    ig.plot(graph, target=ax, layout=graph.layout_grid())

    # Add a colorbar
    sm = cm.ScalarMappable(
        norm=plt.Normalize(min(p_pagerank), max(p_pagerank)), cmap=cmap
    )
    plt.colorbar(sm, ax=ax, label="Personalized PageRank")

    plt.title("Graph with Personalized PageRank")
    plt.axis("equal")
    plt.savefig('personalized_page_rank_test.png')

def sparse_normalize(matrix: torch.Tensor, dim: int = 0) -> torch.Tensor:
    """
    From torch_ppr.utils main but not in 0.08
    https://github.com/mberr/torch-ppr/blob/main/src/torch_ppr/utils.py

    Normalize a sparse matrix to row/column sum of 1.

    :param matrix:
        the sparse matrix
    :param dim:
        the dimension along which to normalize, either 0 for rows or 1 for columns

    :return:
        the normalized sparse matrix
    """
    # calculate row/column sum
    row_or_column_sum = (
        torch.sparse.sum(matrix, dim=dim).to_dense().clamp_min(min=torch.finfo(matrix.dtype).eps)
    )
    # invert and create diagonal matrix
    scaling_matrix = sparse_diagonal(values=torch.reciprocal(row_or_column_sum))
    # multiply matrix
    if dim == 0:
        args = (matrix, scaling_matrix)
    else:
        args = (scaling_matrix, matrix)
    # note: we do not pass by keyword due to instable API
    return torch.sparse.mm(*args)


class Command(BaseCommand):
    help = "Test the personalized page rank"

    def handle(self, *args, **options):
        print('Personalized page rank test')

        print('Number of entities:', Entity.objects.count())
        print('Number of nodes:', Node.objects.count())
        print('Number of relationships:', Relationship.objects.count())
        print('Number of relationship_types:', Relationship.objects.values('relationship_type').distinct().count())

        entity_sample = Entity.objects.order_by('?').values('name')[:25]
        print('Sample of entities:', entity_sample)

        top_node_by_count = Node.objects.annotate(count=Count('name')).order_by('-count').values('name', 'count')[:25]
        print('Top nodes by count:', top_node_by_count)
        
        relationship_type_sample = Relationship.objects.values('relationship_type').distinct().order_by('?')[:25]
        print('Sample of relationship_types:', relationship_type_sample)

        top_relationship_type_sample = Relationship.objects.annotate(count=Count('relationship_type')).order_by('-count').values('relationship_type', 'count')[:25]
        print('Top relationship_types:', top_relationship_type_sample)

        print('Fetching edges...')
        edges = Relationship.objects.filter(
            left_node__entity__isnull=False,
            right_node__entity__isnull=False
        ).annotate(count=Count('relationship_type')).order_by('-count').values_list('left_node__entity_id', 'right_node__entity_id', 'count')
        print('Edges:', edges.count())
        edge_index = torch.as_tensor(data=[(left_node_id, right_node_id) for left_node_id, right_node_id, count in edges]).t()
        #edge_index = torch.as_tensor(data=[(0, 1), (1, 2), (1, 3), (2, 4)]).t()
        from torch_ppr import personalized_page_rank
        print('Running PPR...')
        # in order to customize the reset vector we use power iteration directly
        num_nodes = edge_index.max() + 1
        #num_nodes = len(list(set(edge_index.flatten().tolist())))
        print('Num nodes:', num_nodes)
        # TODO set to zero any of the ones not in the edge_index
        num_unique_nodes = len(list(set(edge_index.flatten().tolist())))
        x0 = torch.full((num_nodes,), 1.0 / num_unique_nodes)
        x0[torch.tensor(list(set(edge_index.flatten().tolist())))] = 0.0

        # TODO reset_vector "x0" based on nearby embedding nodes, softmax of top 100 or whatever
        print('X0:', x0.shape)
        device = 'cuda:3'
        num_nodes = prepare_num_nodes(edge_index=edge_index, num_nodes=num_nodes)
        edge_counts = [count for _, _, count in edges]
        adj = torch.sparse_coo_tensor(
            indices=edge_index,
            values=torch.tensor(edge_counts, dtype=torch.get_default_dtype()),
            size=(num_nodes, num_nodes),
        )
        # symmetrize
        adj = adj + adj.t()
        # add identity matrix
        adj = adj + sparse_diagonal(torch.ones(adj.shape[0], dtype=adj.dtype, device=adj.device))
        # normalize
        adj = sparse_normalize(matrix=adj, dim=0)
        print('Adjacency:', adj, adj.shape)
        validate_adjacency(adj=adj)
        print('Power iteration...')
        ppr = power_iteration(
            adj=adj, 
            x0=x0, 
            device=device, 
            use_tqdm=True,
            alpha=0.05,
            max_iter=100000,
        )
        #ppr = personalized_page_rank(edge_index=edge_index)
        #ppr = personalized_page_rank(edge_index=edge_index, indices=[0,1,2])
        print('PPR:', ppr)
        softmax_ppr = torch.softmax(ppr, dim=0)
        print('Softmax PPR:', softmax_ppr)
        print('min & max:', softmax_ppr.min().item(), softmax_ppr.max().item())

        # histogram
        #plt.hist(softmax_ppr.cpu().numpy(), bins=100)
        #plt.savefig('softmax_ppr_histogram.png')

        top_k = torch.topk(softmax_ppr, k=100, dim=0)
        #print('Top K:', top_k)
        top_k_list = top_k.indices.tolist()
        #print('Top K list:', top_k_list)

        top_entities = Entity.objects.filter(id__in=top_k_list).values_list('id', 'name')
        #print('Top Entities:', top_entities.count(), top_entities)

        top_entities_sorted = sorted(
            [
                (id, name, softmax_ppr[id].item())
                for id, name in top_entities
            ],
            key=lambda x: top_k_list.index(x[0])
        )
        #print('Top Entities sorted:', top_entities_sorted)

        import pandas as pd
        top_entities_df = pd.DataFrame(top_entities_sorted, columns=['id', 'name', 'ppr'])
        print('Top Entities DataFrame:', top_entities_df)

        # TODO prioritize around the following
        [
            'von-willebrand disease',
            '510(k)',
        ]

        return
