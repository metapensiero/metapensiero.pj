import subprocess, os, json


from pyxc.util import usingPython3, parentOf

from pyxc import pyxc_exceptions

#
# Most of pyxc and pj require Python 3,
# but your build script or Django app is probably running under 2.x...
#
# Not to worry, you can use this module as-is from either 2 or 3!
#
# If you're not running 3, this module will invoke
# a <code>pj</code> subprocess to perform the compilation.
#
# The <code>pj</code> script doesn't even have to be on your <code>PATH</code>

#### Code to Code
def codeToCode(pythonCode):
    return _runViaSubprocessIfNeeded(
                    # name, args, kwargs &mdash; if we're running Python 3
                    'codeToCode',
                    [pythonCode],
                    {},
                    # input, args &mdash; for the Python 3 subprocess
                    pythonCode,
                    ['--code-to-code'])

#### Build Bundle
def buildBundle(mainModule, **kwargs):
    '''
    kwargs:
        path=None, createSourceMap=False, includeSource=False, prependJs=None
    '''
    path = kwargs.get('path')
    assert path is not None

    args = ['--build-bundle', mainModule]
    if path is not None:
        args.append('--path=%s' % ':'.join(path))
    if kwargs.get('createSourceMap'):
        args.append('--create-source-map')

    return _runViaSubprocessIfNeeded(
                    # name, args, kwargs &mdash; if we're running Python 3
                    'buildBundle',
                    [mainModule],
                    kwargs,
                    # input, args &mdash; for the Python 3 subprocess
                    None,
                    args,
                    parseJson=True)


def _runViaSubprocessIfNeeded(name, args, kwargs, input, subprocessArgs, parseJson=False):

    if usingPython3():
        import pj.api_internal
        f = getattr(pj.api_internal, name)
        return f(*args, **kwargs)
    else:

        if isinstance(input, unicode):
            input = input.encode('utf-8')

        pythonPath = parentOf(parentOf(os.path.abspath(__file__)))
        if os.environ.get('PYTHONPATH'):
            pythonPath += ':' + os.environ.get('PYTHONPATH')

        subprocessArgs = ['/usr/bin/env',
                                    'PYTHONPATH=%s' % pythonPath,
                                    'python3.1',
                                    parentOf(os.path.abspath(__file__)) + '/pj',
                                    ] + subprocessArgs

        if input is None:
            p = subprocess.Popen(subprocessArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = p.communicate()
        else:
            p = subprocess.Popen(subprocessArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            out, err = p.communicate(input=input)

        if p.returncode == 0:
            result = unicode(out, 'utf-8')
            if parseJson:
                result = json.loads(result)
            return result
        else:
            try:
                errInfo = json.loads(err)
            except ValueError:
                errInfo = {
                    'name': 'Exception',
                    'message': unicode(err, 'utf-8'),
                }
            if hasattr(pyxc_exceptions, errInfo['name']):
                exceptionClass = getattr(pyxc_exceptions, errInfo['name'])
                raise exceptionClass(errInfo['message'])
            else:
                raise Exception('%s\n--------\n%s' % (errInfo['name'], errInfo['message']))


def closureCompile(js, closureMode):

    if not closureMode:
        return js

    if isinstance(closureMode, list) or isinstance(closureMode, tuple):
        for mode in closureMode:
            js = closureCompile(js, mode)
        return js

    modeArgs = {
        'pretty': [
                        '--compilation_level', 'WHITESPACE_ONLY',
                        '--formatting', 'PRETTY_PRINT'],
        'simple': [
                        '--compilation_level', 'SIMPLE_OPTIMIZATIONS'],
        'advanced': [
                        '--compilation_level', 'ADVANCED_OPTIMIZATIONS'],
    }[closureMode]

    p = subprocess.Popen([
                            '/usr/bin/env',
                            'java',
                            '-jar', os.environ['CLOSURE_JAR'],
                            ] + modeArgs,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE)
    out, err = p.communicate(input=js.encode('utf-8'))
    if p.returncode != 0:
        raise Exception('Error while Closure-compiling:\n' + err)

    return out
