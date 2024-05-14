import math
import symmetry_handling_conss as shc

def generate_cip_file(N, D, symmetry_method, write_to="."):
    '''
    generates files in CIP format that model the detection of Fekete points

    E.B. Saff and A.B.J. Kuijlaars. Distributing Many Points on a Sphere.
    The Mathematical Intelligencer 19(1), pp. 5-11. 1997

    description of parameters:
    N                 - number of points
    D                 - dimension of points
    symmetry_method   - variant of symmetry handling inequalities encoded by an integer
    write_to          - path to the target directory
   '''
    name = f"{write_to}/elec_N{N}_D{D}_sym{symmetry_method}.cip"
    f = open(name, 'w')

    nvars = 1 + N*D
    nconss = N + 1 + shc.ub_number_conss(N,D)
    x = {(i,j): f"x{i}_{j}" for i in range(N) for j in range(D)}

    # header
    f.write("STATISTICS\n")
    f.write(f"  Problem name     : elec_N{N}_D{D}\n")
    f.write(f"  Variables        : {nvars} (0 binary, 0 integer, 0 implicit integer, {nvars} continuous)\n")
    f.write(f"  Constraints      : 0 initial, {nconss} maximal\n")
    f.write("OBJECTIVE\n")
    f.write("  Sense            : minimize\n")
    f.write("VARIABLES\n")

    # variables
    for d in range(D):
        for i in range(N):
            f.write(f"  [continuous] <x{i}_{d}>: obj=0, original bounds=[-1.0,1.0]\n")
    f.write(f"  [continuous] <obj>: obj=1, original bounds=[0,Inf]\n")

    # constraints
    f.write("CONSTRAINTS\n")

    # every point has squared norm 1
    for i in range(N):
        f.write(f"  [nonlinear] <normcons{i}>: ")

        for d in range(D):
            f.write(f"<x{i}_{d}>^2")
            if d == D-1:
                f.write(" == 1;\n")
            else:
                f.write(" + ")

    # the objective
    f.write("  [nonlinear] <objcons>: ")
    for i in range(N):
        for j in range(i+1, N):
            f.write("1/(")
            for d in range(D):
                f.write(f"(<x{i}_{d}> - <x{j}_{d}>)^2")
                if d == D-1:
                    f.write(")^(0.5)")
                else:
                    f.write(" + ")

            if i == N-2 and j == N-1:
                f.write(" - <obj> <= 0;\n")
            else:
                f.write(" + ")

    # potentially handle symmetries
    shc.add_symmetry_handling_conss(f, x, N, D, symmetry_method)

    f.write("END\n\n")

    f.close()

    return name
