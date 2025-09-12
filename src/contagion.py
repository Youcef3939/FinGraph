import networkx as nx

def simulate_contagion(G, initial_nodes, steps=5, decay=0.5):
    """
    Simulate a financial shock propagating through the network.

    Parameters:
    - G: networkx.DiGraph
    - initial_nodes: list of node tickers where shock starts
    - steps: number of propagation steps
    - decay: factor by which shock weakens per step (0 < decay <= 1)

    Returns:
    - G: updated graph with 'risk' attribute on nodes
    """

    # Initialize risk scores
    for node in G.nodes():
        G.nodes[node]['risk'] = 0.0

    # Set initial nodes to maximum risk
    for node in initial_nodes:
        if node in G.nodes():
            G.nodes[node]['risk'] = 1.0

    # Propagate shock over multiple steps
    for step in range(steps):
        new_risk = {}
        for node in G.nodes():
            risk_contrib = 0.0
            for neighbor in G.predecessors(node):
                # Contribution from incoming edges weighted by neighbor's risk and edge weight
                weight = G.edges[neighbor, node].get('weight', 1)
                risk_contrib += G.nodes[neighbor]['risk'] * weight * decay
            # Update node risk (take max to avoid overwriting stronger shocks)
            new_risk[node] = max(G.nodes[node]['risk'], min(risk_contrib, 1.0))
        # Apply new risk values
        for node, r in new_risk.items():
            G.nodes[node]['risk'] = r

    return G

def top_risk_nodes(G, top_n=5):
    """
    Return top N nodes with highest risk scores.
    """
    return sorted(G.nodes(data=True), key=lambda x: x[1].get('risk', 0), reverse=True)[:top_n]

if __name__ == "__main__":
    # Example usage
    from etl import load_data, build_graph

    companies, edges = load_data('../data/companies.csv', '../data/supply_edges.csv')
    G = build_graph(companies, edges)

    # Simulate contagion starting from 'TSLA' and 'JPM'
    G = simulate_contagion(G, initial_nodes=['TSLA', 'JPM'], steps=5, decay=0.5)

    # Print top risk nodes
    print("Top nodes by simulated risk:")
    for node, data in top_risk_nodes(G):
        print(f"{node} ({data['name']}): {data['risk']:.3f}")
