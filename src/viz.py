from pyvis.network import Network
from etl import load_data, build_graph
from analytics import compute_centrality, detect_communities, attach_metrics
from contagion import simulate_contagion
import webbrowser
import os

def risk_to_color(risk):
    """
    Map risk score [0,1] to color gradient green->yellow->red
    """
    if risk <= 0.33:
        return "#2ecc71"  
    elif risk <= 0.66:
        return "#f1c40f"  
    else:
        return "#e74c3c"  

def visualize_graph(G):
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        notebook=False,
        bgcolor="#ffffff",
        cdn_resources='in_line'
    )

    node_colors = ["#3498db", "#9b59b6", "#e67e22", "#1abc9c", "#f39c12", "#8e44ad"]

    for i, (node, data) in enumerate(G.nodes(data=True)):
        title = f"<b>{data['name']}</b><br>Sector: {data['sector']}<br>Market Cap: {data['market_cap']}<br>Risk: {data.get('risk',0):.2f}"
        size = 20 + data.get('pagerank', 0) * 500
        color = risk_to_color(data.get('risk', 0)) if 'risk' in data else node_colors[i % len(node_colors)]
        net.add_node(
            node,
            label=node,
            title=title,
            value=size,
            color=color,
            borderWidth=2,
            borderColor="#555555"
        )

    for source, target, data in G.edges(data=True):
        weight = data.get('weight', 1)
        net.add_edge(
            source,
            target,
            value=weight,
            color="#ffffff", 
            width=weight,
            arrows="to"
        )

    net.set_options("""
    var options = {
      "nodes": {
        "font": {"color": "#222222", "size": 18, "face": "Arial", "strokeWidth": 2, "strokeColor": "#ffffff"},
        "borderWidth": 2
      },
      "edges": {"width": 2},
      "physics": {
        "forceAtlas2Based": {"gravitationalConstant": -50,"centralGravity":0.01,"springLength":150,"springConstant":0.08,"damping":0.4},
        "minVelocity": 0.75
      },
      "interaction": {"hover": true},
      "layout": {"improvedLayout": true}
    }
    """)

    output_file = "graph.html"
    html_content = net.generate_html()
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"🔥 interactive graph saved to {output_file}!")

    webbrowser.open('file://' + os.path.realpath(output_file))

if __name__ == "__main__":
    companies, edges = load_data('../data/companies.csv', '../data/supply_edges.csv')
    G = build_graph(companies, edges)

    centrality = compute_centrality(G)
    communities = detect_communities(G)
    G = attach_metrics(G, centrality, communities)

    G = simulate_contagion(G, initial_nodes=['TSLA', 'JPM'], steps=5, decay=0.5)

    visualize_graph(G)
