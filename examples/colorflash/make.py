import os, sys, time
from subprocess import check_call

import pj.api
from pyxc.util import parentOf


EXAMPLES_ROOT = parentOf(parentOf(os.path.abspath(__file__)))
PATH = [
    '%s/colorflash/js' % EXAMPLES_ROOT,
    '%s/mylib/js' % EXAMPLES_ROOT,
]


def main():

    check_call(['mkdir', '-p', 'build'])

    js = None

    for closureMode in ['', 'pretty', 'simple']:

        filename = {
            '': 'colorflash.raw.js',
            'pretty': 'colorflash.pretty.js',
            'simple': 'colorflash.min.simple.js',
        }[closureMode]

        path = 'build/%s' % filename

        sys.stderr.write('%s... ' % path)
        start = time.time()

        if not js:
            js = pj.api.buildBundle('colorflash.colorflash', path=PATH)

        with open(path, 'wb') as f:
            f.write(pj.api.closureCompile(js, closureMode))

        ms = int((time.time() - start) * 1000)
        sys.stderr.write('done. (%d ms)\n' % ms)


if __name__ == '__main__':
    main()
