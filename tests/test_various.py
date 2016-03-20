# -*- coding: utf-8 -*-
# :Project:  pyxc-pj -- tests for various stuff
# :Created:    lun 22 feb 2016 23:31:45 CET
# :Author:    Alberto Berti <alberto@metapensiero.it>
# :License:   GNU General Public License version 3 or later
#

from metapensiero.pj.api import translate_object


def test_body_names_stop_at_func(astobj):

    from metapensiero.pj.processor.util import body_local_names

    def outer(no):
        yes = 1

        def yes_func():
            no2 = 3

        yes2 = 3

    assert body_local_names(astobj(outer).body) == {'yes', 'yes2'}

def test_textwrap_behavior():

    txt = " " * 4 + "foo bar" + "\n" + " " * 4 + "bar foo" + "\n"
    assert len(txt) == 24
    l = txt.splitlines()[0]
    assert len(l) == 11
    import textwrap
    out = textwrap.dedent(txt)
    assert len(out) == 16


def test_globals():

    def func():

        def simple_alert():
            window.alert('Hi there!')

        el = document.querySelector('button')
        el.addEventListener('click', simple_alert)


    expected = ('var el;\n'
                'function simple_alert() {\n'
                '    window.alert("Hi there!");\n'
                '}\n'
                'el = document.querySelector("button");\n'
                'el.addEventListener("click", simple_alert);\n')

    assert translate_object(func, body_only=True)[0] == expected


def test_imports():

    def func():
        import foo, bar
        import foo.bar as b
        from foo.bar import hello as h, bye as bb
        from ..foo.zoo import bar
        from . import foo
        from .foo import bar

        from __globals__ import test_name

        # this should not trigger variable definition
        test_name = 2

        # this instead should do it
        test_foo = True

        __all__ = ['test_name', 'test_foo']

    expected = ('var test_foo;\n'
                "import * as foo from 'foo';\n"
                "import * as bar from 'bar';\n"
                "import * as b from 'foo/bar';\n"
                "import {hello as h, bye as bb} from 'foo/bar';\n"
                "import {bar} from '../../foo/zoo';\n"
                "import * as foo from './foo';\n"
                "import {bar} from './foo';\n"
                'test_name = 2;\n'
                'test_foo = true;\n'
                'export {test_name};\n'
                'export {test_foo};\n')

    assert translate_object(func, body_only=True, enable_es6=True)[0] == expected


def test_exception():

    def func():

        class MyError(Exception):
            pass

        class MySecondError(MyError):
            """A stupid error"""

    expected = (
        'function MyError(message) {\n'
        '    this.name = "MyError";\n'
        '    this.message = (message || "Custom error MyError");\n'
        '    if (((typeof Error.captureStackTrace) === "function")) {\n'
        '        Error.captureStackTrace(this, this.constructor);\n'
        '    } else {\n'
        '        this.stack = new Error(message).stack;\n'
        '    }\n'
        '}\n'
        'MyError.prototype = Object.create(Error.prototype);\n'
        'MyError.prototype.constructor = MyError;\n'
        'class MySecondError extends MyError {\n'
        '}\n'
    )

    assert translate_object(func, body_only=True, enable_es6=True)[0] == expected


def test_try_except_simple():

    def func():

        class MyError(Exception):
            pass

        class MySecondError(MyError):
            """A stupid error"""

        try:
            value = 0
            raise MySecondError('This is an error')
        except MySecondError:
            value = 1

    expected = (
        'var value;\n'
        'function MyError(message) {\n'
        '    this.name = "MyError";\n'
        '    this.message = (message || "Custom error MyError");\n'
        '    if (((typeof Error.captureStackTrace) === "function")) {\n'
        '        Error.captureStackTrace(this, this.constructor);\n'
        '    } else {\n'
        '        this.stack = new Error(message).stack;\n'
        '    }\n'
        '}\n'
        'MyError.prototype = Object.create(Error.prototype);\n'
        'MyError.prototype.constructor = MyError;\n'
        'class MySecondError extends MyError {\n'
        '}\n'
        'try {\n'
        '    value = 0;\n'
        '    throw new MySecondError("This is an error");\n'
        '} catch(e) {\n'
        '    if ((e instanceof MySecondError)) {\n'
        '        value = 1;\n'
        '    } else {\n'
        '        throw e;\n'
        '    }\n'
        '}\n'
    )

    assert translate_object(func, body_only=True, enable_es6=True)[0] == expected

def test_try_except_complex():


    def func():
        value = 0

        class MyError(Exception):
            pass

        class MySecondError(MyError):
            """A stupid error"""

        try:
            value += 1
            raise MyError("Something bad happened")
            value += 1
        except MySecondError:
            value += 20
        except MyError:
            value += 30
        except:
            value += 40
        finally:
            value += 1


    expected = (
        'var value;\n'
        'value = 0;\n'
        'function MyError(message) {\n'
        '    this.name = "MyError";\n'
        '    this.message = (message || "Custom error MyError");\n'
        '    if (((typeof Error.captureStackTrace) === "function")) {\n'
        '        Error.captureStackTrace(this, this.constructor);\n'
        '    } else {\n'
        '        this.stack = new Error(message).stack;\n'
        '    }\n'
        '}\n'
        'MyError.prototype = Object.create(Error.prototype);\n'
        'MyError.prototype.constructor = MyError;\n'
        'class MySecondError extends MyError {\n'
        '}\n'
        'try {\n'
        '    value += 1;\n'
        '    throw new MyError("Something bad happened");\n'
        '    value += 1;\n'
        '} catch(e) {\n'
        '    if ((e instanceof MySecondError)) {\n'
        '        value += 20;\n'
        '    } else {\n'
        '        if ((e instanceof MyError)) {\n'
        '            value += 30;\n'
        '        } else {\n'
        '            value += 40;\n'
        '        }\n'
        '    }\n'
        '} finally {\n'
        '    value += 1;\n'
        '}\n'
    )

    assert translate_object(func, body_only=True, enable_es6=True)[0] == expected
