# -*- coding: utf-8 -*-
# :Project:   metapensiero.pj --
# :Created:   gio 15 feb 2018 20:05:03 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Alberto Berti
#

import enum

RunMode = enum.Enum('RunMode', ('COMPILED', 'MACROPY', 'AUTO'))

RUN_MODE = RunMode.AUTO


def _get_transforms_pkg():
    global RUN_MODE
    if RUN_MODE is RunMode.AUTO:
        try:
            from . import compiled_transformations as transformations
            RUN_MODE = RunMode.COMPILED
        except ImportError:
            from . import transformations  # noqa
            RUN_MODE = RunMode.MACROPY
    elif RUN_MODE is RunMode.COMPILED:
        from . import compiled_transformations as transformations
    else:
        from . import transformations
    return transformations
