import networkx as nx
import community as community_louvain  

def compute_centrality(G):
    """
    Compute centrality metrics for each node in the graph.
    Returns a dict of dicts with metrics.
    """
    centrality = {}
    centrality['pagerank'] = nx.pagerank(G, weight='weight')
    centrality['betweenness'] = nx.betweenness_centrality(G, weight='weight')
    centrality['eigenvector'] = nx.eigenvector_centrality(G, max_iter=1000, weight='weight')
    return centrality

def detect_communities(G):
    """
    Detect communities using Louvain algorithm.
    Returns a dict: node -> community_id
    """
    partition = community_louvain.best_partition(G.to_undirected(), weight='weight')
    return partition

def attach_metrics(G, centrality, communities):
    """
    Add centrality metrics and community info as node attributes.
    """
    for node in G.nodes():
        G.nodes[node]['pagerank'] = centrality['pagerank'].get(node, 0)
        G.nodes[node]['betweenness'] = centrality['betweenness'].get(node, 0)
        G.nodes[node]['eigenvector'] = centrality['eigenvector'].get(node, 0)
        G.nodes[node]['community'] = communities.get(node, -1)
    return G

if __name__ == "__main__":
    from etl import load_data, build_graph
    companies, edges = load_data('../data/companies.csv', '../data/supply_edges.csv')
    G = build_graph(companies, edges)
    
    centrality = compute_centrality(G)
    communities = detect_communities(G)
    G = attach_metrics(G, centrality, communities)
    
    sorted_pagerank = sorted(centrality['pagerank'].items(), key=lambda x: x[1], reverse=True)
    print("Top nodes by PageRank:")
    for node, score in sorted_pagerank:
        print(f"{node} ({G.nodes[node]['name']}): {score:.4f}")
    
    print("\nCommunities detected:")
    for comm_id in set(communities.values()):
        members = [node for node, cid in communities.items() if cid == comm_id]
        print(f"Community {comm_id}: {members}")
