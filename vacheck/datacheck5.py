# -*- coding: utf-8 -*-

"""
vacheck.datacheck5

Tool for running data checks used by InterVA5.
"""

from .exceptions import VAInputException, VAIDException
from pandas import read_csv, Series
from pkgutil import get_data
from io import BytesIO
from numpy import nan


def datacheck5(va_input, va_id, insilico_check=False):
    """
    Runs verbal autopsy data consistency check from InterVA5 algorithm.
    :param va_input: original data for one observation with values
    0 (absence), 1 (presence), and numpy.nan (missing).
    :type va_input: pandas.Series
    :param va_id: ID for this observation
    :type va_id: string
    :param insilico_check: Indicator to use InSilicoVA rule which sets all
    symptoms that should not be asked to a value of missing. In contrast,
    the default rule sets these symptoms to missing only when they take the
    substantive value.
    :type insilico_check: boolean
    :return: cleaned input with log messages from first and second passes.
    :rtype: dictionary with keys output, first_pass (a list), and
    second_pass (a list).
    """

    probbase_bytes = get_data("vacheck", "data/probbaseV5.csv")
    probbase = read_csv(BytesIO(probbase_bytes))
    # note: drop second row so it matches the input
    probbase.drop(index=0, inplace=True)
    probbase["indic"].iloc[0] = "prior"
    if not isinstance(va_input, Series):
        raise VAInputException(
            "`va_input` must be a pandas.Series, not {}".format(
                va_input.__class__.__name__
            ))
    if not all(va_input.dropna().isin([va_id, 0, 1])):
        raise VAInputException(
            "`va_input` must have values 0, 1, nan, and `va_id`"
        )
    if len(va_input) != 354:
        raise VAInputException(
            "`va_input` must have 354 elements"
        )
    input_current = va_input.copy()
    number_symptoms = input_current.shape[0]
    index_current = va_id
    first_pass = []
    second_pass = []

    for k in range(2):
        for j in range(1, number_symptoms):
            subst_val = int(probbase.iat[j, 5] == "Y")
            bool_dont_asks = probbase.iloc[j, 7:15].notna()
            dont_asks = bool_dont_asks[bool_dont_asks].index
            if len(dont_asks) > 0:
                for q in dont_asks:
                    dont_ask_q = probbase[q].iloc[j]
                    dont_ask_q_who = probbase.iloc[j, 3]
                    input_dont_ask = input_current[dont_ask_q[0:5]]
                    dont_ask_val = int(dont_ask_q[5:6] == "Y")

                    if (input_current[j] is not nan and
                            input_dont_ask is not nan):
                        if (
                                (input_current[j] == subst_val or insilico_check) and
                                input_dont_ask == dont_ask_val):

                            input_current[j] = nan

                            dont_ask_row = probbase["indic"].str.contains(dont_ask_q[0:5])
                            dont_ask_sdesc = probbase[dont_ask_row].iat[0, 2]

                            msg = (f"{index_current}   {probbase.iat[j, 4]} "
                                   f"({probbase.iat[j, 3]}) value inconsistent with "
                                   f"{dont_ask_q_who} ({dont_ask_sdesc}) "
                                   "- cleared in working information")

                            if k == 0:
                                first_pass.append(msg)
                            else:
                                second_pass.append(msg)

            # ask if
            if probbase.iat[j, 15] is not nan and input_current[j] is not nan:
                ask_if_indic = probbase.iat[j, 15][0:5]
                ask_if_row = probbase["indic"].str.contains(ask_if_indic)
                ask_if_who = probbase[ask_if_row].iat[0, 3]
                input_ask_if = input_current[ask_if_indic]
                ask_if_val_str = probbase.iat[j, 15][5:6]
                ask_if_val = int(
                    ask_if_val_str.replace("Y", "1").replace("N", "0"))

                if input_current[j] == subst_val:
                    change_ask_if = (
                            input_ask_if is not ask_if_val and
                            subst_val is not input_ask_if)

                    if change_ask_if:
                        input_current[ask_if_indic] = ask_if_val
                        msg = (f"{index_current}   {ask_if_who} "
                               f"({probbase.iat[j, 2]})  not flagged in category "
                               f"{probbase[ask_if_row].iat[0, 3]} "
                               f"({probbase[ask_if_row].iat[0, 2]}) "
                               "- updated in working information")

                        if k == 0:
                            first_pass.append(msg)
                        else:
                            second_pass.append(msg)

            # neonates only
            if probbase.iat[j, 16] is not nan and input_current[j] is not nan:
                nn_only = probbase.iat[j, 16][0:5]
                input_nn_only = input_current[nn_only]
                if input_nn_only is nan:
                    input_nn_only = 0

                if input_current[j] == subst_val and input_nn_only != 1:
                    input_current[j] = nan

                    msg = (f"{index_current}   {probbase.iat[j, 3]} "
                           f"({probbase.iat[j, 2]}) only required for neonates"
                           " - cleared in working information")
                    if k == 0:
                        first_pass.append(msg)
                    else:
                        second_pass.append(msg)

    output = {"output": input_current,
              "first_pass": first_pass,
              "second_pass": second_pass}
    return output
