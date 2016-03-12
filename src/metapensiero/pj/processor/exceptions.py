# -*- coding: utf-8 -*-
# :Project:  pj -- exceptions
# :Created:  ven 26 feb 2016 15:17:49 CET
# :Authors:  Andrew Schaaf <andrew@andrewschaaf.com>,
#            Alberto Berti <alberto@metapensiero.it>
# :License:  GNU General Public License version 3 or later
#


class ProcessorError(Exception):

    def __str__(self):
        ast = self.args[0]
        return "Node type '%s': Line: %d, column: %d" % (type(ast).__name__,
                                                         ast.lineno,
                                                         ast.col_offset)


class TransformationError(ProcessorError):

    def __str__(self):
        error = super().__str__()
        if len(self.args) > 1:
            error += ". %s" % self.args[1]
        return error


class UnsupportedSyntaxError(TransformationError):
    pass
