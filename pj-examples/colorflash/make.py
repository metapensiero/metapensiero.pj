
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
    
    for closureMode in ['', 'pretty', 'simple', 'advanced']:
        
        if closureMode:
            path = 'build/colorflash.%s.js' % closureMode
        else:
            path = 'build/colorflash.raw.js'
        
        sys.stderr.write('%s... ' % path)
        start = time.time()
        
        if not js:
            js = pj.api.buildBundle('colorflash.main', path=PATH)
        
        with open(path, 'wb') as f:
            f.write(pj.api.closureCompile(js, closureMode))
        
        ms = int((time.time() - start) * 1000)
        sys.stderr.write('done. (%d ms)\n' % ms)


if __name__ == '__main__':
    main()
