# -*- coding: utf-8 -*-

import pytest
from pandas import read_csv, Series
import pkgutil
from io import BytesIO

from vacheck.datacheck5 import datacheck5
va_data_csv = pkgutil.get_data("vacheck", "data/example_input.csv")
va_data = read_csv(BytesIO(va_data_csv))


class TestReturnDefaults:

    results = datacheck5(input=va_data.iloc[0], id=va_data["ID"][0])

    def test_return_type(self):
        assert type(self.results) is dict

    def test_output_type(self):
        assert type(self.results["output"]) == Series

    def test_output_first_pass(self):
        assert type(self.results["first_pass"]) == list

    def test_output_second_pass(self):
        assert type(self.results["second_pass"]) == list
