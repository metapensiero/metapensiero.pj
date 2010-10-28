#!/usr/bin/env python3.1

# For each of many Python fragments, check that...
#
#   * it runs as Python
#   * it compiles to js
#   * the js runs
#   * the value of the last line is the same in py and js
#
# Prereqs
# 
#   * have [Rhino](http://www.mozilla.org/rhino/)'s js.jar somewhere
#   * have the environment variable <code>RHINO_JAR</code> point to it

import os, json, re, sys

def up(n):
    path = os.path.abspath(__file__)
    return '/'.join(path.rstrip('/').split('/')[:-n])

sys.path.append(up(3))

from pyxc.util import usingPython3, check_communicate, exceptionRepr
assert usingPython3()
from pj.api_internal import codeToCode


def main():
    
    for py in getFragments():
        
        js = codeToCode(py)
        jsValue = valueOfLastLine_js(js)
        
        m = re.search(r'# Expected value: (.*)', py)
        if m:
            pyValue = json.loads(m.group(1))
        else:
            pyValue = valueOfLastLine_py(py)
        
        
        sys.stderr.write('%s... ' % json.dumps(py))
        if jsValue == pyValue:
            sys.stderr.write('ok.\n')
        else:
            sys.stderr.write('FAIL!')
            for k in ['py', 'js', 'jsValue', 'pyValue']:
                print('--- %s ---' % k)
                print(locals()[k])
            sys.exit(1)


def runJs(js):
    
    rhinoPath = os.environ['RHINO_JAR']
    
    try:
        out, err = check_communicate([
                            '/usr/bin/env',
                            'java',
                            '-jar', rhinoPath,
                            '-e', js.encode('utf-8')])
    except Exception as e:
        raise Exception(e.msg + '\n--- js ---\n' + js)
    return out


def valueOfLastLine_py(py):
    try:
        k = '___result___'
        py = changeLastLine(py, lambda line: '%s = %s' % (k, line))
        l, g = {}, {}
        exec(py, g, l)
        return json.loads(json.dumps(l[k]))
    except Exception:
        raise Exception('Error when running Python code.\n--- py ---\n%s\n--- err ---\n%s' % (py, exceptionRepr()))


def valueOfLastLine_js(js):
    newJs = changeLastLine(
                js.strip(),
                lambda line: 'print(json_dumps(%s));' % line.rstrip(';'))
    jsWithJson = '%s\n%s' % (
                getJsonCode(),
                newJs)
    jsOut = runJs(jsWithJson)
    try:
        return json.loads(str(jsOut, 'utf-8'))
    except Exception:
        raise Exception('Error decoding Rhino output %s for js %s' % (
                                repr(jsOut),
                                repr(newJs)))


def changeLastLine(code, f):
    lines = code.split('\n')
    lines[-1] = f(lines[-1])
    return '\n'.join(lines)


def getJsonCode():
    return '''
        var json_dumps = function(x) {
            var json_dumps = arguments.callee;
            if (
                    (x === true) ||
                    (x === false) ||
                    (x === null)) {
                return x;
            }
            else if ((typeof x) == "number") {
                return '' + x;
            }
            else if ((typeof x) == "string") {
                //ASSUMPTION: x is a very safe string
                return '"' + x + '"';
            }
            else if (x instanceof Array) {
                var bits = [];
                for (var i = 0, bound = x.length; i < bound; i++) {
                    bits.push(arguments.callee(x[i]));
                }
                return '[' + bits.join(', ') + ']';
            }
            else {
                var bits = [];
                for (var k in x) {
                    if (x.hasOwnProperty(k)) {
                        bits.push(json_dumps(k) + ':' + json_dumps(x[k]));
                    }
                }
                return '{' + bits.join(', ') + '}';
            }
        };
    '''

def getFragments():
    s = '''1729

y = [x + 1 for x in [1, 2, 3, 100]]
y

if 3 < 3:
    x = 1
elif 2 < 3:
    x = 2
else:
    x = 3
x

x = 0
i = 10
while True:
    pass
    x += i
    i -= 1
    if i < 0:
        break
    else:
        continue
x

d = {'foo': 1, 'bar': 2}
del d['bar']
d

def f(x):
    return x + 1000
f(7)

x = 0
for i in range(5):
    x += i
x

x = 0
for i in range(3, 5):
    x += i
x

x = ''
d = {'foo': 'FOO', 'bar': 'BAR'}
for k in dict(d):
    x += k + d[k]
x

x = 0
for t in [1, 2, 3, 100]:
    x += t
x

def f(x):
    "docstring"
    return x
f(5)

try:
    raise Exception('foo')
except Exception as e:
    pass
5

class Foo:
    def __init__(self):
        self.msg = 'foo'
Foo().msg

class Animal:
    def __init__(self, name):
        self.name = name
class TalkingAnimal(Animal):
    def __init__(self, name, catchphrase):
        super(name)
        self.catchphrase = catchphrase
    def caption(self):
        return self.name + " sez '" + self.catchphrase + "'"
# Expected value: "Pac-Man sez 'waka waka'"
TalkingAnimal('Pac-Man', 'waka waka').caption()

class Animal:
    def __init__(self, name):
        self.name = name
class TalkingAnimal(Animal):
    def __init__(self, name, catchphrase):
        super(name)
        self.catchphrase = catchphrase
    def caption(self):
        return self.name + " sez '" + self.catchphrase + "'"
class Kitteh(TalkingAnimal):
    def __init__(self, name):
        super(name, 'OH HAI')
    def caption(self):
        return 'OMG AWESOMECUTE: ' + super()
# Expected value: "OMG AWESOMECUTE: Maru-san sez 'OH HAI'"
Kitteh('Maru-san').caption()

1

-1

1E3

True

False

None

0.5

x = "foo"
x

[1, 2, "foo"]

(1, 2, "foo")

{'foo': 1, 'bar': 2}

2 + 3

2 - 3

2 * 3

4 / 2

7 % 6

2**5

1 + 2 * 3

2 < 3

3 <= 3

3 >= 3

3 > 3

2 < 3 <= 3

2 < 3 < 3

100 if 2 < 3 else 200

(lambda x, y: x + y)(2, 3)

(True and False) or (True and not False)

x = 5
x

x = 5
x += 2
x'''
    
    return re.split(r'\n\n[\n]*', s)


if __name__ == '__main__':
    main()
