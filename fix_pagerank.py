import sys
import networkx as nx
g = nx.DiGraph()
g.add_node("models/orders.sql")
g.add_edge("models/stg_orders.sql", "models/orders.sql")
try:
    pr = nx.pagerank(g)
    print("PageRank Success:", pr)
except Exception as e:
    print("Error:", e)
