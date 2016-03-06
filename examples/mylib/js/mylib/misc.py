# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj
# :Author:   Andrew Schaaf <andrew@andrewschaaf.com>
# :License:  See LICENSE file
#

def bind(f, obj):
    return lambda: f.apply(obj, arguments)

__all__ = ('bind',)
