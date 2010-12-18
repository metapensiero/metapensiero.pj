
import sys, os, json, subprocess, re, hashlib, time
import urllib.request
import urllib.parse

from pyxc.util import TempDir, parentOf, simplePost

import pj.api_internal


def runViaNode(path, codepath, exceptionServerHost, exceptionServerPort, runExceptionServer):
    
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        raise Exception('File not found: ' + repr(path))
    filename = path.split('/')[-1]
    module = filename.split('.')[-2]
    codepath = (codepath or []) + [parentOf(path)]
    
    if exceptionServerPort:
        #LATER: nice fatal error if exception-server not installed
        prependJs = "require('exception-server').devCombo(%s);\n" % json.dumps({
            'connectTo': [exceptionServerHost, exceptionServerPort],
        })
    else:
        prependJs = None
    
    info = pj.api_internal.buildBundle(
                            module,
                            path=codepath,
                            createSourceMap=True,
                            includeSource=True,
                            prependJs=prependJs)
    js = info['js']
    sourceMap = info['sourceMap']
    sourceDict = info['sourceDict']
    
    with TempDir() as td:
        
        jsPath = '%s/%s.js' % (td.path, filename)
        with open(jsPath, 'wb') as f:
            f.write(js.encode('utf-8'))
        
        exception_server_proc = None
        if runExceptionServer:
            exception_server_proc = startExceptionServer(
                                        exceptionServerPort, js, sourceMap, sourceDict, jsPath)
        try:
            subprocess.check_call(['node', jsPath])
            if exception_server_proc is not None:
                exception_server_proc.kill()
        except Exception:
            sys.stderr.write('[PYXC] Leaving exception server running until you Control-C...\n')
            try:
                while True:
                    time.sleep(1)
            finally:
                if exception_server_proc is not None:
                    exception_server_proc.kill()


def startExceptionServer(exceptionServerPort, js, sourceMap, sourceDict, jsPath):
    path = '%s/nodejs_exception_server.js' % parentOf(__file__)
    p = subprocess.Popen(
                            ['node', path, str(exceptionServerPort)],
                            stdout=subprocess.PIPE)
    
    try:
        line = p.stdout.readline()
        assert line.startswith(b'Server ready, PYXC-PJ. Go, go, go!'), repr(line)
    
        # Send it information
        jsdata = js.encode('utf-8')
        jshash = hashlib.sha1(jsdata).hexdigest()
        tups = [('mapping', jshash, sourceMap.encode('utf-8'))]
        for k, d in sourceDict.items():
            data = d['code'].encode('utf-8')
            tups.append((
                            'code',
                            hashlib.sha1(data).hexdigest(),
                            data))
        url = 'http://localhost:%d/api/log.js' % exceptionServerPort
        for typename, k, v in tups:
            simplePost(url, POST={
                'type': typename,
                'code_sha1': k,
                'v': v,
            })
    
    except Exception:
        p.kill()
        raise
    
    return p

