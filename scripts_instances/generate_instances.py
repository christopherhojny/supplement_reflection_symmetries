import generate_instances_elec as g1
import generate_instances_kissingnumber as g2
import generate_instances_packing as g3
import generate_instances_maxcut as g4

# generate instances of elec problem
for D in range(2,4):
    for N in range(3,15):
        for S in range(7):
            g1.generate_cip_file(N, D, S, write_to="instances")

# generate instances of kissingnumber problem
for D in range(2,4):
    for N in range(3,15):
        for S in range(7):
            g2.generate_cip_file(N, D, True, S, write_to="instances")

# generate instances of packing problem
for D in range(2,4):
    for N in range(3,15):
        for S in range(7):
            g3.generate_cip_file(N, D, S, write_to="instances")

# generate instances of maxcut problem
g4.generate_instances_color02(color02path, "instances")
