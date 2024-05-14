#!/usr/bin/env python3

import argparse

ENDINGS = [".mps.gz", ".cip", ".osil.gz", ".cnf"]

def display_aggregated_results(statistics, testset_name):
    '''
    from statistics of SCIP experiments, displays aggregated symmetry information of a test set

    statistics   - dictionary containing statistics of entire test set
    testset_name - name of the test set
    '''

    # find the number of instances in the test set that allow for a specific symmetry handling method
    n_symmetric = 0
    n_perm = 0
    n_sperm = 0
    n_sdoublelex = 0
    n_orbitope = 0
    n_doublelex = 0
    n_sorbitope = 0
    n_simple = 0
    for instance in statistics:
        stats = statistics[instance]

        if stats["nperms"] > 0 or stats["nsperms"] > 0:
            n_symmetric += 1
        if stats["nperms"] > 0:
            n_perm += 1
        if stats["nsperms"] > 0:
            n_sperm += 1
        if stats["nsdoublelex"] > 0:
            n_sdoublelex += 1
        if stats["norbitope"] > 0:
            n_orbitope += 1
        if stats["ndoublelex"] > 0:
            n_doublelex += 1
        if stats["nsorbitope"] > 0:
            n_sorbitope += 1
        if stats["nsimple"] > 0:
            n_simple += 1

    print("  %20s & %4d & %4d & %4d & %4d & %4d & %4d & %4d & %4d & %4d\\\\"
          % (latexify(testset_name), len(statistics.keys()), n_symmetric, n_sperm, n_perm,
             n_sdoublelex, n_doublelex, n_sorbitope, n_orbitope, n_simple))

def latexify(string):
    '''
    makes a string LaTeX compatible

    string -- string to be modified
    '''

    string = string.replace('_', "\_")

    return string

def remove_ending(string):
    '''
    tried to remove known file endings from a string and returns the result

    string - string to be trimmed
    '''

    for ending in ENDINGS:
        if string.endswith(ending):
            return string.rstrip(ending)

    return string

def display_full_line(statistics, instance_name):
    '''
    displays detailed information about symmetries present in a single instance

    statistics - dictionary containing statistics of a single instance
    instance   - name of the instance for which results shall be shown
    '''

    name = remove_ending(instance_name)
    name = latexify(name)

    # extract information about different symmetry types
    signed_row_column_sym = dict()
    for key in statistics["sdoublelex"]:
        signed_row_column_sym.setdefault(key, 0)
        signed_row_column_sym[key] += 1

    row_column_sym = dict()
    for key in statistics["doublelex"]:
        row_column_sym.setdefault(key, 0)
        row_column_sym[key] += 1

    signed_row_sym = dict()
    for key in statistics["sorbitope"]:
        signed_row_sym.setdefault(key, 0)
        signed_row_sym[key] += 1

    row_sym = dict()
    for key in statistics["orbitope"]:
        row_sym.setdefault(key, 0)
        row_sym[key] += 1

    # print information
    found = False
    line = "    %30s & " % name
    for (r,c,s) in signed_row_column_sym.keys():
        line += "\mbox{%d$\cdot$sRC(%d, %d; %s)} " % (signed_row_column_sym[r,c,s], r, c, s)
        found = True
    for (rb, cb, r, c) in row_column_sym.keys():
        line += "\mbox{%d$\cdot$RC(%d, %d)} " % (row_column_sym[rb,cb,r,c], r, c)
        found = True
    for (r,c) in signed_row_sym.keys():
        line += "\mbox{%d$\cdot$sC(%d, %d)} " % (signed_row_sym[r,c], r, c)
        found = True
    for (r,c) in row_sym.keys():
        line += "\mbox{%d$\cdot$C(%d, %d)} " % (row_sym[r,c], r, c)
        found = True
    if statistics["nsimple"] != 0:
        line += "\mbox{S(%d)}" % statistics["nsimple"]
        found = True

    if not found:
        return
        # line += "---"
    line += " \\\\"

    print(line)


def display_full_results(statistics):
    '''
    from statistics of SCIP experiments, displays symmetry information per tested instance

    statistics - dictionary containing statistics of entire test set
    '''

    for instance in statistics:
        display_full_line(statistics[instance], instance)

def extract_symmetry_statistics(results_file):
    '''
    from the SCIP results for an entire test set, extracts information about symmetry groups

    results_file - path to file containing the SCIP results
    '''

    statistics = dict()

    f = open(results_file, 'r')

    name = ""
    stats = None
    for line in f:

        if line.startswith("@01"):
            # a new instance is detected
            name = line.split()[1].split('/')[-1]
            stats = {
                "nperms": -1,
                "nsperms": -1,
                "nsdoublelex": 0,
                "sdoublelex": [],
                "norbitope": 0,
                "orbitope": [],
                "ndoublelex": 0,
                "doublelex": [],
                "nsorbitope": 0,
                "sorbitope": [],
                "nsimple": 0
            }
        elif line.startswith("@04"):
            # store statistics
            statistics[name] = stats
        elif "SYMMETRY" in line:
            sline = line.strip()

            if sline.startswith("SYMMETRY stats perms"):
                ssline = sline.split()
                stats["nperms"] = int(ssline[3])
                stats["nsperms"] = int(ssline[5])
            elif "simplecut" in sline:
                stats["nsimple"] += 1
            elif "doublelexorbitope" in sline:
                ssline = sline.split()
                stats["nsdoublelex"] += 1
                stat = tuple([int(ssline[5]), int(ssline[7]), int(ssline[9])])
                stats["sdoublelex"].append(stat)
            elif "orbitope dynamic" in sline:
                ssline = sline.split()
                stats["norbitope"] += 1
                stat = tuple([int(ssline[6]), int(ssline[8])])
                stats["orbitope"].append(stat)
            elif "doublelex columnblocks" in sline:
                ssline = sline.split()
                stats["ndoublelex"] += 1
                stat = [int(ssline[5]), int(ssline[7])]
                for i in range(stat[0]):
                    stat.append(int(ssline[9 + i]))
                for i in range(stat[1]):
                    stat.append(int(ssline[9 + stat[0] + 1 + i]))
                stat = tuple(stat)
                stats["doublelex"].append(stat)
            else:
                assert "signedorbitope" in sline

                ssline = sline.split()
                stats["nsorbitope"] += 1
                stat = tuple([int(ssline[5]), int(ssline[7])])
                stats["sorbitope"].append(stat)

    f.close()

    return statistics


if __name__ == "__main__":

    # create a parser for arguments
    parser = argparse.ArgumentParser(description='evaluates the symmetry structures for a test set')
    parser.add_argument('results', metavar='results', type=str, help='file containing results for a test set')
    parser.add_argument('tname', metavar='tname', type=str, help='name of test set')
    parser.add_argument('--full', action='store_true', default=False, help='shall results per instance be created')

    args = parser.parse_args()

    statistics = extract_symmetry_statistics(args.results)

    if args.full:
        display_full_results(statistics)
    else:
        display_aggregated_results(statistics, args.tname)
