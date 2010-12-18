#!/usr/bin/env python3.1

import optparse, sys, os, json, subprocess

# Require Python 3
from pyxc.util import usingPython3, writeExceptionJsonAndDie, TempDir, parentOf
if not usingPython3():
    sys.stderr.write('Python 3 required.')
    sys.exit(1)

import pj.api_internal


#### Main
def main():
    
    parser = optparse.OptionParser()
    parser.add_option('-p', '--path', dest='path', default=None)
    parser.add_option('-C', '--code-to-code', dest='codeToCode', default=False, action='store_true')
    parser.add_option('-B', '--build-bundle', dest='buildBundle', default=False, action='store_true')
    
    options, args = parser.parse_args()
    
    codepath = None
    if options.path is not None:
        codepath = options.path.split(':')
    elif os.environ.get('PYXC_PJ_PATH'):
        codepath = os.environ['PYXC_PJ_PATH'].strip(':').split(':')
    
    if options.codeToCode:
        codeToCode()
    
    elif options.buildBundle:
        buildBundle(args[0], codepath)
    
    elif len(args) == 1:
        runNodeJs(args[0], codepath)
    
    else:
        sys.stderr.write('Invalid args -- see http://pyxc.org/pj for usage.\n')
        sys.exit(1)


#### Code to Code
# See [pj.api_internal.codeToCode](api_internal.py)
def codeToCode():
    py = sys.stdin.read()
    try:
        js = pj.api_internal.codeToCode(py)
        sys.stdout.write(js)
    except Exception as e:
        writeExceptionJsonAndDie(e)


#### runNodeJs
def runNodeJs(path, codepath):
    
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        raise Exception('File not found: ' + repr(path))
    filename = path.split('/')[-1]
    module = filename.split('.')[-2]
    codepath = (codepath or []) + [parentOf(path)]
    
    js = pj.api_internal.buildBundle(
                            module,
                            path=codepath)
    
    with TempDir() as td:
        
        jsPath = '%s/%s.js' % (td.path, filename)
        with open(jsPath, 'wb') as f:
            f.write(js.encode('utf-8'))
        
        subprocess.check_call(['node', jsPath])


#### Build Bundle
# See [pj.api_internal.buildBundle](api_internal.py)
def buildBundle(mainModule, codepath):
    try:
        info = pj.api_internal.buildBundle(
                            mainModule,
                            path=codepath)
        sys.stdout.write(json.dumps(info))
    except Exception as e:
        writeExceptionJsonAndDie(e)


if __name__ == '__main__':
    main()
