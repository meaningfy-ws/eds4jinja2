#!/usr/bin/python3

# test_latex_utils.py
# Date:  05/01/2021
# Author: Eugeniu Costetchi
# Email: costezki.eugen@gmail.com 

""" """
from eds4jinja2.adapters.latex_utils import escape_latex


def test_escape_chars():
    in_s = r"$%\$#_\{}~^"
    out_s = r"\$\%\$\#\_\{\}\~\^"
    assert escape_latex(in_s) == out_s


def test_with_backslash():
    in_s = r"$%\$#_\\\{}~^"
    out_s = r"\$\%\$\#\_\\\{\}\~\^"
    assert escape_latex(in_s) == out_s


def test_multiline_str():
    in_s = r'''this is \a very great string
    and I couldn't ever_want to make too \\ much money$'''
    out_s = r'''this is \\a very great string
    and I couldn't ever\_want to make too \\ much money\$'''
    assert escape_latex(in_s) == out_s


def test_non_string_returns_original_value():
    for non_string_value in [
        123,
        11.5,
        ['hello', 'world'],
        {1: 2, 3: 4},
    ]: assert non_string_value == escape_latex(non_string_value)
