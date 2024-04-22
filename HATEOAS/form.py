"""
This module provides the glossary query form
"""

import HATEOAS.form_filler as ff

from HATEOAS.form_filler import FLD_NM  # for tests

USERNAME = 'username'
PASSWORD = 'password'
EMAIL = 'email'

LOGIN_FORM_FLDS = [
    {
        FLD_NM: 'Instructions',
        ff.QSTN: 'Enter your username and password.',
        ff.INSTRUCTIONS: True,
    },
    {
        FLD_NM: USERNAME,
        ff.QSTN: 'Username',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: False,
    },
    # {
    #     FLD_NM: EMAIL,
    #     ff.QSTN: 'Email',
    #     ff.PARAM_TYPE: ff.QUERY_STR,
    #     ff.OPT: False,
    # },
    {
        FLD_NM: PASSWORD,
        ff.QSTN: 'Password',
        ff.PARAM_TYPE: ff.QUERY_STR,
        ff.OPT: False,
    },
    
]


def get_form() -> list:
    return LOGIN_FORM_FLDS


def get_form_descr() -> dict:
    """
    For Swagger!
    """
    return ff.get_form_descr(LOGIN_FORM_FLDS)


def get_fld_names() -> list:
    return ff.get_fld_names(LOGIN_FORM_FLDS)


def main():
    print(f'Form: {get_form_descr()=}\n\n')


if __name__ == "__main__":
    main()