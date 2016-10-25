
import numpy as np
import scipy as sp
from patsy import dmatrix
import logging


def alias_list(model, design):
    """Returns a human-readable list of dependent model columns.

    This is done by solving AX=B, where X is the full rank model matrix,
    and B is all of the columns of the model matrix. The result is a matrix
    of coefficients which represent to what degree a given column is
    collinear with another column.
    """

    logging.debug("model:\n%s", model)
    model_matrix = dmatrix(model, design, return_type="dataframe")
    logging.debug("model matrix (rhs):\n%s", model_matrix)

    # there is no requirement that the model matrix is full rank
    # so first remove linearly dependent columns using LU decomp
    _, _, upper_matrix = sp.linalg.lu(model_matrix)
    logging.debug("upper matrix from LU:\n%s", upper_matrix)

    unaliased = model_matrix.loc[:, np.array(abs(np.diagonal(upper_matrix)) >
                                             np.finfo(float).eps)]
    logging.debug("full rank matrix (lhs):\n%s", unaliased)

    alias_coefs, _, _, _ = np.linalg.lstsq(unaliased, model_matrix)
    logging.debug("alias matrix:\n%s", alias_coefs)
    alias_list = []
    for r in range(alias_coefs.shape[0]):
        alias_strings = []
        for c in range(alias_coefs.shape[1]):
            if c == r or abs(alias_coefs[r, c]) < np.finfo(float).eps:
                continue
            if abs(alias_coefs[r, c] - 1.0) > np.finfo(float).eps:
                alias_strings.append("{}*{}".format(alias_coefs[r, c],
                                     model_matrix.columns[c]))
            else:
                alias_strings.append(model_matrix.columns[c])
        if len(alias_strings):
            alias_list.append("{} = {}".format(unaliased.columns[r],
                              " + ".join(alias_strings)))
    return alias_list, alias_coefs
