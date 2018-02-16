# -*- coding: utf-8 -*-
# :Project:   metapensiero.pj -- utility to compile transformations
# :Created:   gio 15 feb 2018 18:41:52 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2018 Alberto Berti
#

if __name__ == '__main__':
    import logging
    import os

    import macropy

    from metapensiero import pj
    from .processor.transforming import load_transformations

    pj.RUN_MODE = pj.RunMode.MACROPY
    this_dir = os.path.dirname(__file__)
    transformations_dir = os.path.join(this_dir, 'transformations')
    compiled_dir = os.path.join(this_dir, 'compiled_transformations')

    log = logging.getLogger(__name__)

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger().setLevel(logging.DEBUG)
    log.debug('Log started')

    import macropy.activate

    macropy.exporter = macropy.exporters.SaveExporter(
        compiled_dir, transformations_dir)

    from . import transformations  # noqa
    load_transformations(transformations)

    print('Transfomations compiled')
