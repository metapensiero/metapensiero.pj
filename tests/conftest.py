# -*- coding: utf-8 -*-
# :Project: pyxc-pj -- test fixtures
# :Created: lun 22 feb 2016 12:16:42 CET
# :Author:  Alberto Berti <alberto@metapensiero.it>
# :License: GNU General Public License version 3 or later
#

import pytest
from metapensiero.pj.testing import ast_object, ast_dump_object, ast_object_to_js

@pytest.fixture
def astdump():
    return ast_dump_object


@pytest.fixture
def astobj():
    return ast_object


@pytest.fixture
def astjs():
    return ast_object_to_js
