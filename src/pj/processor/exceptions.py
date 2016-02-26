# -*- coding: utf-8 -*-
# :Project:  pj -- exceptions
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#


class PyxcError(Exception):
    pass


class NoTransformationForNode(PyxcError):
    pass
