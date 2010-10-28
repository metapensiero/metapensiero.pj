#!/usr/bin/env python3.1

import optparse, sys, json

# Require Python 3
from pyxc.util import usingPython3, writeExceptionJsonAndDie
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
    
    if options.codeToCode:
        codeToCode()
    
    elif options.buildBundle:
        buildBundle(options, args)
    
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


#### Build Bundle
# See [pj.api_internal.buildBundle](api_internal.py)
def buildBundle(options, args):
    try:
        jsCode = pj.api_internal.buildBundle(
                            args[0],
                            path=options.path.split(':'))
        sys.stdout.write(jsCode)
    except Exception as e:
        writeExceptionJsonAndDie(e)


if __name__ == '__main__':
    main()
