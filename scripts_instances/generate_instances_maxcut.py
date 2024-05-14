import networkx as nx
import random

def read_graph(graphfile):
    '''
    reads a graph from a file in DIMACS format

    graphfile - the graph in DIMACS format
    '''

    nodes = set()
    edges = set()

    f = open(graphfile, 'r')

    for line in f:
        if line.startswith('e'):
            info = line.split()
            u = int(info[1])
            v = int(info[2])
            edge = (u,v)
            if v < u:
                edge = (v,u)

            nodes.add(u)
            nodes.add(v)
            edges.add(edge)

    f.close()

    return list(nodes), list(edges)

def generate_cip_file(graphfile, write_to, weighted, filetype, seed=0):
    '''
    generates a max-cut problem for an undirected graph

    graphfile - file encoding the graph in DIMACS format
    write_to  - path to the target directory
    weighted  - whether a weighted graph shall be created
    filetype  - type of file, e.g., ".col" or ".dimacs"
    seed      - random seed used to generate weights
    '''

    assert graphfile.endswith(filetype)

    nodes, edges = read_graph(graphfile)
    graphname = graphfile.split('/')[-1][:-len(filetype)]

    # possibly generate signs for each edge (needed to create weights)
    signs = []
    if weighted:
        random.seed(a=seed)
        signs = [random.randint(0,1) for e in edges]

    name = f"{write_to}/maxcut_{graphname}.cip"
    if not weighted:
        name = f"{write_to}/unweighted_maxcut_{graphname}.cip"
    f = open(name, 'w')

    nvars = len(nodes) + len(edges)
    nconss = 2 * len(edges)
    nodevars = {v: f"s{v}" for v in nodes}
    edgevars = {(u,v): f"c{u}_{v}" for (u,v) in edges}

    # header
    f.write("STATISTICS\n")
    f.write(f"  Problem name     : maxcut_{graphname}\n")
    f.write(f"  Variables        : {nvars} ({nvars} binary, 0 integer, 0 implicit integer, 0 continuous)\n")
    f.write(f"  Constraints      : 0 initial, {nconss} maximal\n")
    f.write("OBJECTIVE\n")
    f.write("  Sense            : maximize\n")
    f.write("VARIABLES\n")

    # variables
    for e in range(len(edges)):
        obj = 1
        # possibly compute an edge weight
        if weighted:
            -1 + 2*signs[e]
        f.write(f"  [binary] <{edgevars[edges[e]]}>: obj={obj}, original bounds=[0,1]\n")
    for v in nodes:
        f.write(f"  [binary] <{nodevars[v]}>: obj=0, original bounds=[0,1]\n")

    # constraints
    f.write("CONSTRAINTS\n")

    # constraints for edges
    for e in range(len(edges)):
        (u,v) = edges[e]
        f.write(f"  [linear] <edgecons{e}_A>: +<{nodevars[u]}> +<{nodevars[v]}> +<{edgevars[(u,v)]}> <= 2;\n")
        f.write(f"  [linear] <edgecons{e}_B>: -<{nodevars[u]}> -<{nodevars[v]}> +<{edgevars[(u,v)]}> <= 0;\n")

    f.write("END\n\n")

    f.close()

def generate_instances_color02(color02path, write_to):
    '''
    generates max-cut problems for graphs from the DIMACS Color02 test set

    color02path - path to directory containing the graphs
    write_to    - path to the target directory where max-cut problems are stored
    '''

    # graphs from the test set
    instances = ["1-FullIns_3.col", "1-FullIns_4.col", "1-FullIns_5.col", "1-Insertions_4.col", "1-Insertions_5.col",
                 "1-Insertions_6.col", "2-FullIns_3.col", "2-FullIns_4.col", "2-FullIns_5.col", "2-Insertions_3.col",
                 "2-Insertions_4.col", "2-Insertions_5.col", "3-FullIns_3.col", "3-FullIns_4.col", "3-FullIns_5.col",
                 "3-Insertions_3.col", "3-Insertions_4.col", "3-Insertions_5.col", "4-FullIns_3.col", "4-FullIns_4.col",
                 "4-FullIns_5.col", "4-Insertions_3.col", "4-Insertions_4.col", "5-FullIns_3.col", "5-FullIns_4.col",
                 "abb313GPIA.col", "anna.col", "ash331GPIA.col", "ash608GPIA.col", "ash958GPIA.col", "david.col",
                 "DSJC1000.1.col", "DSJC1000.5.col", "DSJC1000.9.col", "DSJC125.1.col", "DSJC125.5.col", "DSJC125.9.col",
                 "DSJC250.1.col", "DSJC250.5.col", "DSJC250.9.col", "DSJC500.1.col", "DSJC500.5.col", "DSJC500.9.col",
                 "DSJR500.1c.col", "DSJR500.1.col", "DSJR500.5.col", "fpsol2.i.1.col", "fpsol2.i.2.col", "fpsol2.i.3.col",
                 "games120.col", "homer.col", "huck.col", "inithx.i.1.col", "inithx.i.2.col", "inithx.i.3.col", "jean.col",
                 "latin_square_10.col", "le450_15a.col", "le450_15b.col", "le450_15c.col", "le450_15d.col", "le450_25a.col",
                 "le450_25b.col", "le450_25c.col", "le450_25d.col", "le450_5a.col", "le450_5b.col", "le450_5c.col",
                 "le450_5d.col", "miles1000.col", "miles1500.col", "miles250.col", "miles500.col", "miles750.col",
                 "mug100_1.col", "mug100_25.col", "mug88_1.col", "mug88_25.col", "mulsol.i.1.col", "mulsol.i.2.col",
                 "mulsol.i.3.col", "mulsol.i.4.col", "mulsol.i.5.col", "myciel3.col", "myciel4.col", "myciel5.col",
                 "myciel6.col", "myciel7.col", "qg.order100.col", "qg.order30.col", "qg.order40.col", "qg.order60.col",
                 "queen10_10.col", "queen11_11.col", "queen12_12.col", "queen13_13.col", "queen14_14.col", "queen15_15.col",
                 "queen16_16.col", "queen5_5.col", "queen6_6.col", "queen7_7.col", "queen8_12.col", "queen8_8.col",
                 "queen9_9.col", "school1.col", "school1_nsh.col", "wap01a.col", "wap02a.col", "wap03a.col", "wap04a.col",
                 "wap05a.col", "wap06a.col", "wap07a.col", "wap08a.col", "will199GPIA.col", "zeroin.i.1.col", "zeroin.i.2.col",
                 "zeroin.i.3.col"]

    for inst in instances:
        generate_cip_file(f"{color02path}/{inst}", write_to, False, seed=0, filetype=".col")
