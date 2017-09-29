
# Make graph
def makeGraph(corexes, column_label):
    weights = [corex.alpha[:, :, 0].clip(0, 1) * corex.mis for corex in corexes]
    node_weights = [corex.tcs for corex in corexes]

    g = nx.DiGraph()
    max_node_weight = max([max(w) for w in node_weights])
    for layer, weight in enumerate(weights):
        m, n = weight.shape
        for j in range(m):
            g.add_node((layer + 1, j))
            g.node[(layer + 1, j)]['weight'] = 0.3 * node_weights[layer][j] / max_node_weight
            for i in range(n):
                g.add_weighted_edges_from([( (layer, i), (layer + 1, j), 10 * weight[j, i])])
    # Label layer 0
    for i, lab in enumerate(column_label):
        g.add_node((0, i))
        g.node[(0, i)]['label'] = lab
        g.node[(0, i)]['name'] = lab  # JSON uses this field
        g.node[(0, i)]['weight'] = 1
    return g

G = makeGraph(layers, labels)
nx.drawing.nx_agraph.write_dot(G, 'graph.dot')
