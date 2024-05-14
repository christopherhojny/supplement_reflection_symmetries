import math
import symmetry_handling_conss as shc

def generate_cip_file(N, D, symmetry_method, write_to="."):
    '''
    generates files in CIP format that model the problem to allocate N points
    in a hypercube such that the pairwise l1-distance is as large as possible.

    description of parameters:
    N               - number of l1-balls
    D               - dimesion of points
    symmetry_method - variant of symmetry handling inequalities encoded by an integer
    write_to        - path to the target directory
    '''
    name = f"{write_to}/packing_N{N}_D{D}_sym{symmetry_method}.cip"
    f = open(name, 'w')

    nvars = N*D + 1
    nconss = N*(N-1)/2 + shc.ub_number_conss(N,D)
    x = {(i,j): f"x{i}_{j}" for i in range(N) for j in range(D)}

    # header
    f.write("STATISTICS\n")
    f.write(f"  Problem name     : packing_N{N}_D{D}_sym{symmetry_method}\n")
    f.write(f"  Variables        : {nvars} (0 binary, 0 integer, 0 implicit integer, {nvars} continuous)\n")
    f.write(f"  Constraints      : 0 initial, {nconss} maximal\n")
    f.write("OBJECTIVE\n")
    f.write("  Sense            : maximize\n")
    f.write("VARIABLES\n")

    # variables
    for d in range(D):
        for i in range(N):
            f.write(f"  [continuous] <x{i}_{d}>: obj=0, original bounds=[-1,1]\n")
    f.write(f"  [continuous] <obj>: obj=1, original bounds=[0,{2*D}]\n")

    # constraints
    f.write("CONSTRAINTS\n")

    # all balls have sufficient l1-distance
    for i in range(N):
        for j in range(i+1, N):
            f.write(f"  [nonlinear] <dist{i}_{j}>: ")
            for d in range(D):
                f.write(f"abs(<{x[i,d]}> - <{x[j,d]}>)")
                if d == D - 1:
                    f.write(" - 2*<obj> >= 0;\n")
                else:
                    f.write(" + ")
                

    # potentially handle symmetries
    shc.add_symmetry_handling_conss(f, x, N, D, symmetry_method)

    f.write("END\n\n")

    f.close()

    return name
