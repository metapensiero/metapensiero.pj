#!/usr/bin/env python3.1

import optparse, sys, os, json

# Require Python 3
from pyxc.util import usingPython3, writeExceptionJsonAndDie, TempDir, parentOf
if not usingPython3():
    sys.stderr.write('Python 3 required.')
    sys.exit(1)

import pj.api_internal
from pj.nodejs import runViaNode


#### Main
def main():

    parser = optparse.OptionParser()

    parser.add_option('-p', '--path', dest='path', default=None)
    parser.add_option('-M', '--create-source-map', dest='createSourceMap', default=False, action='store_true')

    parser.add_option('-C', '--code-to-code', dest='codeToCode', default=False, action='store_true')
    parser.add_option('-B', '--build-bundle', dest='buildBundle', default=False, action='store_true')
    parser.add_option('-E', '--run-exception-server',
                                dest='runExceptionServer', default=False, action='store_true')
    parser.add_option('-U', '--use-exception-server',
                                dest='useExceptionServer', default=None)

    options, args = parser.parse_args()

    codepath = None
    if options.path is not None:
        codepath = options.path.split(':')
    elif os.environ.get('PYXC_PJ_PATH'):
        codepath = os.environ['PYXC_PJ_PATH'].strip(':').split(':')

    # Code to code
    if options.codeToCode:
        codeToCode()

    # Build bundle
    elif options.buildBundle:
        buildBundle(args[0], codepath, options.createSourceMap)

    # Run via node
    elif len(args) == 1:
        esHost, esPort = (None, None)
        if options.runExceptionServer:
            esHost, esPort = 'localhost', 61163
        elif options.useExceptionServer is not None:
            (esHost, esPort) = options.useExceptionServer.split(':')
            if not esHost:
                esHost = 'localhost'
        runViaNode(args[0], codepath, esHost, esPort, options.runExceptionServer)

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
        raise
        #writeExceptionJsonAndDie(e)


#### Build Bundle
# See [pj.api_internal.buildBundle](api_internal.py)
def buildBundle(mainModule, codepath, createSourceMap):
    try:
        info = pj.api_internal.buildBundle(
                            mainModule,
                            path=codepath,
                            createSourceMap=createSourceMap)
        sys.stdout.write(json.dumps(info))
    except Exception as e:
        writeExceptionJsonAndDie(e)


if __name__ == '__main__':
    main()
