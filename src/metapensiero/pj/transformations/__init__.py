# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj
# :Created:  gio 09 mar 2017 19:43:11 CET
# :Author:   Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#

def _normalize_name(n):
    if n.startswith('d_'):
        n = n.replace('d_', '$')
    elif n.startswith('dd_'):
        n = n.replace('dd_', '$$')
    elif not n.startswith('_') and n.endswith('_'):
        n = n[:-1]
    return n
