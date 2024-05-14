import math

def matrix_sort_first_row(cip, mat_vars, nrows, ncols, row_is_nonnegative):
    '''
    Given a matrix of variables, adds the inequalities
    x_{1,1} >= x_{1,2} >= ... >= x_{1,n}
    to a CIP file.

    cip                - write stream to CIP file to which inequalities are added
    mat_vars           - dictionary mapping matrix indices to the corresponding variable names
    nrows              - number of rows of matrix
    ncols              - number of columns of matrix
    row_is_nonnegative - whether the variables of the first row are assumed to be non-negative
    '''

    for j in range(ncols - 1):
        cip.write(f"  [linear] <sort_first_row{j}>: -<{mat_vars[0,j]}> + <{mat_vars[0,j+1]}> <= 0;\n")

    if row_is_nonnegative:
        cip.write(f"  [linear] <first_row_nonnegative>: -<{mat_vars[0,ncols-1]}> <= 0;\n")

def matrix_sort_first_column(cip, mat_vars, nrows, ncols):
    '''
    Given a matrix of variables, adds the inequalities
    x_{1,1} >= x_{2,1} >= ... >= x_{m,1}
    to a CIP file.

    cip      - write stream to CIP file to which inequalities are added
    mat_vars - dictionary mapping matrix indices to the corresponding variable names
    nrows    - number of rows of matrix
    ncols    - number of columns of matrix
    '''

    for i in range(nrows - 1):
        cip.write(f"  [linear] <sort_first_column{i}>: -<{mat_vars[i,0]}> + <{mat_vars[i+1,0]}> <= 0;\n")

def double_lex_reflection_matrix(cip, mat_vars, nrows, ncols, enforce_sorting):
    '''
    Given a matrix whose rows and columns can be permuted arbitrarily and whose column entries can be reflected,
    iteratively adds the following inequalities. If column i has k active rows, then it enforces that the ceil(k/2)
    first entries in this column are nonnegative. Here, we say that the first column has nrows many active rows,
    whereas every other column has ceil(k/2) active rows, where k is the number of active rows of the preceding
    column.

    If enforce_sorting is true, it furthermore ensures that the entries ceil(k/2)+1,...,k in column 1 are sorted.

    The corresponding inequalities are written to a CIP file.

    cip             - write stream to CIP file to which inequalities are added
    mat_vars        - dictionary mapping matrix indices to the corresponding variable names
    nrows           - number of rows of matrix
    ncols           - number of columns of matrix
    enforce_sorting - whether sorting shall be enforced
    '''

    nsymrows = math.ceil(nrows/2)
    ub = nrows
    for j in range(ncols):
        # the first nsymrows rows have a nonnegative entry in column j
        for i in range(nsymrows):
            cip.write(f"  [linear] <doublelex_nonnegative_col{j}_row{i}>: -<{mat_vars[i,j]}> <= 0;\n")

        # possible sort some entries in column j no covered by previous constraint
        if enforce_sorting:
            for i in range(nsymrows, ub-1):
                cip.write(f"  [linear] <doublelex_sort_row{i}>: -<{mat_vars[i,0]}> + <{mat_vars[i+1,0]}> <= 0;\n")
        ub = nsymrows
        nsymrows = math.ceil(nsymrows/2)

    # also sort elements in last group
    if enforce_sorting:
        for i in range(nsymrows - 1):
            cip.write(f"  [linear] <doublelex_sort_row{i}>: -<{mat_vars[i,0]}> + <{mat_vars[i+1,0]}> <= 0;\n")
    

def add_symmetry_handling_conss(cip, mat_vars, nrows, ncols, variant):
    '''
    Adds symmetry handling inequalities for matrix symmetries to a CIP file.

    cip      - write stream to CIP file to which inequalities are added
    mat_vars - dictionary mapping matrix indices to the corresponding variable names
    nrows    - number of rows of matrix
    ncols    - number of columns of matrix
    variant  - variant of symmetry handling inequalities encoded by an integer
               0: none
               1: sort first row
               2: sort first row and all entries are nonnegative
               3: sort first row and all entries are nonnegative, and sort first column
               4: use double_lex_reflection_matrix without sorting of first column
               5: use double_lex_reflection_matrix with sorting of first column
               6: use double_lex_reflection_matrix with sorting of first column and row
    '''

    if variant == 1:
        matrix_sort_first_row(cip, mat_vars, nrows, ncols, False)
    elif variant == 2:
        matrix_sort_first_row(cip, mat_vars, nrows, ncols, True)
    elif variant == 3:
        matrix_sort_first_row(cip, mat_vars, nrows, ncols, True)
        matrix_sort_first_column(cip, mat_vars, nrows, ncols)
    elif variant == 4:
        double_lex_reflection_matrix(cip, mat_vars, nrows, ncols, False)
    elif variant == 5:
        double_lex_reflection_matrix(cip, mat_vars, nrows, ncols, True)
    elif variant == 6:
        double_lex_reflection_matrix(cip, mat_vars, nrows, ncols, True)
        matrix_sort_first_row(cip, mat_vars, nrows, ncols, False)
    elif variant == 0:
        pass
    else:
        print(f"Expected variant to be an integer between 0 and 6, but received {variant}.")
        assert False

def ub_number_conss(nrows, ncols):
    '''
    returns an upper bound on the number of symmetry handling constraints that can
    be generated to handle symmetries of a matrix

    nrows - number of rows of matrix
    ncols - number of columns of matrix
    '''

    return 2*(nrows*ncols + 1) + ncols
