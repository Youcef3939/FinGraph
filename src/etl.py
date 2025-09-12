# src/etl.py
import pandas as pd
import networkx as nx

def load_data(companies_file, edges_file):
    """
    Load companies and supply chain edges from CSV files.
    """
    companies = pd.read_csv(companies_file)
    edges = pd.read_csv(edges_file)
    return companies, edges

def build_graph(companies, edges):
    """
    Build a NetworkX directed graph from companies and edges.
    """
    G = nx.DiGraph()
    
    # Add nodes
    for _, row in companies.iterrows():
        G.add_node(row['ticker'],
                   name=row['name'],
                   sector=row['sector'],
                   country=row['country'],
                   market_cap=row['market_cap'])
    
    # Add edges
    for _, row in edges.iterrows():
        G.add_edge(row['supplier'], row['customer'], weight=row.get('weight', 1))
    
    return G
