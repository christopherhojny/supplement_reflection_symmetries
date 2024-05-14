import math
import symmetry_handling_conss as shc

def generate_cip_file(N, D, use_reformulation, symmetry_method, write_to="."):
    '''
    generates files in CIP format that model the kissing number problem as described in

    L. Liberti. Symmetry in Mathematical Programming. Combinatorial optimization and applications.
    LNCS 5165, pp. 328-338, Springer. 2008

    description of parameters:
    N                 - number of spheres
    D                 - dimension in which spheres live
    use_reformulation - whether sum_d (x^i_d - x^j_d)^2 shall be replaced by 8 - 2 * sum_d x^i_d * x^j_d
    symmetry_method   - variant of symmetry handling inequalities encoded by an integer
    write_to          - path to the target directory
    '''
    name = f"{write_to}/kissingnumber_N{N}_D{D}_reform{use_reformulation}_sym{symmetry_method}.cip"
    f = open(name, 'w')

    nvars = 1 + N*D
    nconss = N + N*(N-1)/2 + shc.ub_number_conss(N,D)
    x = {(i,j): f"x{i}_{j}" for i in range(N) for j in range(D)}

    # header
    f.write("STATISTICS\n")
    f.write(f"  Problem name     : kissingnumber_N{N}_D{D}\n")
    f.write(f"  Variables        : {nvars} (0 binary, 0 integer, 0 implicit integer, {nvars} continuous)\n")
    f.write(f"  Constraints      : 0 initial, {nconss} maximal\n")
    f.write("OBJECTIVE\n")
    f.write("  Sense            : maximize\n")
    f.write("VARIABLES\n")

    # variables
    for d in range(D):
        for i in range(N):
            f.write(f"  [continuous] <x{i}_{d}>: obj=0, original bounds=[-2.0,2.0]\n")
    f.write(f"  [continuous] <obj>: obj=1, original bounds=[0,1]\n")

    # constraints
    f.write("CONSTRAINTS\n")

    # every point has squared norm 4
    for i in range(N):
        f.write(f"  [nonlinear] <normcons{i}>: ")

        for d in range(D):
            f.write(f"<x{i}_{d}>^2")
            if d == D-1:
                f.write(" == 4;\n")
            else:
                f.write(" + ")

    # all points have distance at least 4*objective
    for i in range(N):
        for j in range(i+1, N):
            f.write(f"  [nonlinear] <dist{i}_{j}>: ")
                
            if use_reformulation:
                # 8 - 2 * sum_d x^i_d * x^j_d >= 4*obj
                f.write("8 - ")
                for d in range(D):
                    f.write(f"2 * <x{i}_{d}> * <x{j}_{d}>")
                    if d == D-1:
                        f.write(" - 4*<obj> >= 0;\n")
                    else:
                        f.write(" - ")
            else:
                # sum_d (x^i_d - x^j_d)^2 >= 4*obj
                for d in range(D):
                    f.write(f"(<x{i}_{d}> - <x{j}_{d}>)^2")
                    if d == D-1:
                        f.write(" - 4*<obj> >= 0;\n")
                    else:
                        f.write(" + ")

    # potentially handle symmetries
    shc.add_symmetry_handling_conss(f, x, N, D, symmetry_method)

    f.write("END\n\n")

    f.close()

    return name
