# -*- coding: utf-8 -*-
# :Project:  metapensiero.pj
# :Author:   Andrew Schaaf <andrew@andrewschaaf.com>
# :License:  See LICENSE file
#

def clamp(value, min, max):
    return Math.min(Math.max(value, min), max)


__all__ = ('clamp',)
