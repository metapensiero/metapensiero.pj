.. -*- coding: utf-8 -*-
.. :Project:  pj -- readme
.. :Created:  mar 01 mar 2016 15:52:36 CET
.. :Author:   Alberto Berti <alberto@metapensiero.it>
.. :License:  GNU General Public License version 3 or later
..

======================================================
JavaScripthon: a Python 3 to ES6 JavaScript translator
======================================================

.. figure:: http://s3.amazonaws.com/fossbytes.content/wp-content/uploads/2016/04/Javascripthon-python-js-converter.jpg
   :alt: JavaScripthon
   :align: center

   ..

   (image courtesy of `fossBytes`__)

   __ http://fossbytes.com/javascripthon-a-simple-python-to-es6-javascript-translator/


It is based on previous work by `Andrew Schaaf <andrew@andrewschaaf.com>`_.

 :author: Alberto Berti
 :contact: alberto@metapensiero.it
 :license: GNU General Public License version 3 or later

.. contents:: Table of Contents
   :backlinks: top

Introduction
------------

JavaScripthon is a small and simple Python 3.5+ translator to JavaScript which
aims to be able to translate most of the Python's core semantics without
providing a full python-in-js environment, as most existing translators do. It
tries to emit code which is simple to read and check. It does so by switching
to ES6 construct when possible/required. This allows to simplify the needs of
polyfills for many of the expected Python behaviors.

It is designed to be the first step in a pipeline that translates your Pyhton
code into something that a browser can understand. Usually it is used with
tools like `BabelJS`__ and `Webpack`__ to prepare the final bundle that will
be served to the browser. The steps from the source code to the bundle are the
following:

1) JavaScripthon converts your Python 3.5+ code to ES6 JavaScript modules;
2) the BabelJS loader (configured inside Webpack or standalone) translates the
   ES6 JavaScript to ES5 so that the browser can understand it;
3) Webpack parses the resulting source code and packages your source code with
   its dependencies by analyzing ``import`` statements and emits a
   ``bundle.js`` ready to be served to the browser.

Along this process the corresponding `source maps`__ are read and integrated at
every step, allowing you to place breakpoints on your original Python source
files when working with the developer tools of your browser.

An example of such setup is provided in the ``examples`` directory.

__ http://babeljs.io/
__ http://webpack.github.io/
__ http://blog.teamtreehouse.com/introduction-source-maps


In addition to that, you can choose to do most these steps without using
external JS tools. It comes with an `embedded js interpreter`__ that loads a
standalone version of BabelJS and converts your code to ES5 JavaScript without
the need to install anything else. In fact most of the the test you can find
in ``tests/test_evaljs.py`` use the embedded interpreter to dual evaluate the
source code (one time in Python, one time in JavaScript) and simply check that
the results are the same.

__ https://github.com/amol-/dukpy

Thanks to that, JavaScripthon can also be used as a server-side library to
translate single functions or classes that you want your browser to load and
evaluate.

The interface with the JS world is completely flat, just import the modules
or use the expected globals (``window``, ``document``, etc...) as you
would do in JavaScript.

Brief list of the supported Python semantics
--------------------------------------------

The fact that JavaScripthon doesn't *reinvent the wheel* by reimplementing in
Python many of the features available with JavaScript translators/transpilers
allows it to be lean while implementing quite a decent set of the core Python
semanticts. These are, briefly:

* Misc

  - list slices;
  - list' ``append()``;
  - dict's ``copy()``, ``update()``;
  - ``len()``;
  - ``print()``;
  - ``str()``;
  - ``type(instance)``;
  - ``yield`` and ``yield from``;
  - ``async`` and ``await``;
  - ``import`` and ``from...import`` to use any JS module (see `import
    statements`_);

* Comparisons (see section `Simple stuff`_ for the details)

  - most of the basics;
  - ``isinstance()``;
  - ``element in container`` for use with lists, objects, strings and the new
    ES6 collections like ``Map``, ``Set`` and so on;
  - identity checks: ``foo is bar``;
  - ternary comparisons like ``x < y <= z``;

* Statements (see section `Simple stuff`_ and `for statement`_ for the
  details)

  - ``if...elif...else``;
  - ``while`` loop;
  - ``for`` over list, over range, over plain js objects, over iterables (JS
    iterables);
  - ``try...except...finally`` with pythonesque behavior (see
    `try...except...finally statement`_ section for the details);

* Functions (see `Functions`_ section)

  - standard functions, generator functions, async functions;
  - parameters defaults;
  - keyword parameters;
  - parameters accumulators (``*args`` and ``**kwargs``), with some
    restrictions;

* Classes (see `Classes`_ section)

  - single inheritance;
  - Exception classes for use with ``except`` statement;
  - class decorators and method decorators;
  - property descriptors;
  - special handling of ``property`` and ``classmethod`` descriptors;
  - async methods, generator methods;
  - non-function body members (i.e. ``member_of_class_Foo = bar``);

Installation
------------

Python 3.5 is required because Python's AST has changed between 3.4
and 3.5 and as of now supporting multiple Python versions is not one
of my priorities.

To install the package execute the following command::

  $ pip install javascripthon


Usage
-----

To *compile* or *transpile* a python source module, use the
commandline:

.. code:: bash

  $ python -m metapensiero.pj source.py

or:

.. code:: bash

  $ python -m metapensiero.pj -5 source.py

to transpile.

A ``pj`` console script is also automatically installed:

.. code:: bash

  $ pj --help
  usage: pj [-h] [--disable-es6] [--disable-stage3] [-5] [-o OUTPUT] [-d]
            [--pdb]
            file [file ...]

  A Python 3.5+ to ES6 JavaScript compiler

  positional arguments:
    file                  Python source file(s) or directory(ies) to convert.
                          When it is a directory it will be converted
                          recursively

  optional arguments:
    -h, --help            show this help message and exit
    --disable-es6         Disable ES6 features during conversion (Ignored if
                          --es5 is specified)
    --disable-stage3      Disable ES7 stage3 features during conversion
    -5, --es5             Also transpile to ES5 using BabelJS.
    -o OUTPUT, --output OUTPUT
                          Output file/directory where to save the generated code
    -d, --debug           Enable error reporting
    --pdb                 Enter post-mortem debug when an error occurs

Conversions Rosetta Stone
-------------------------

Here is a brief list of examples of the conversions the tool applies,
just some, but not all.

Simple stuff
~~~~~~~~~~~~

.. list-table:: Most are obvious
  :header-rows: 1

  * - Python
    - JavaScript

  * - .. code:: python

        x < y <= z < 5

    - .. code:: javascript

        ((x < y) && (y <= z) && (z < 5))

  * - .. code:: python


        def foo():
            return [True, False, None, 1729,
                    "foo", r"foo\bar", {}]

    - .. code:: javascript

        function foo() {
            return [true, false, null, 1729,
                    "foo", "foo\\bar", {}];
        }


  * - .. code:: python

        while len(foo) > 0:
            print(foo.pop())

    - .. code:: javascript

        while ((foo.length > 0)) {
            console.log(foo.pop());
        }


  * - .. code:: python

        if foo > 0:
            ....
        elif foo < 0:
            ....
        else:
            ....

    - .. code:: javascript

        if ((foo > 0)) {
            ....
        } else {
            if ((foo < 0)) {
                ....
            } else {
                ....
            }
        }


  * - .. code:: python

        str(x)

    - .. code:: javascript

        x.toString()

  * - .. code:: python

        yield foo
        yield from foo

    - .. code:: javascript

        yield foo
        yield* foo


Then there are special cases. Here you can see some of these
conversions. JavaScripthon cannot do a full trace of the sources, so
some shortcuts are taken about the conversion of some core, specific
Python's semantics. For example Python's ``self`` is always converted
to JavaScript's ``this``, no matter where it's found. Or ``len(foo)``
is always translated to ``foo.length``. Albeit this an API specific of
just some objects (Strings, Arrays, etc...), it is considered wide
adopted and something the user may consider obvious.

The rules of thumb to treat things especially are:

* Is it possible to think of a conversion that covers most of the use
  cases?

* Is ts possible to find a convention widely used on the Python world
  to express this special case?

.. list-table:: There are special cases
  :header-rows: 1

  * - Python
    - JavaScript

  * - .. code:: python

        ==

    - .. code:: javascript

        ===

  * - .. code:: python

        !=

    - .. code:: javascript

        !==

  * - .. code:: python

        2**3

    - .. code:: javascript

        Math.pow(2, 3)

  * - .. code:: python

        'docstring'

    - .. code:: javascript

        /* docstring */

  * - .. code:: python

        self

    - .. code:: javascript

        this

  * - .. code:: python

        len(...)

    - .. code:: javascript

        (...).length

  * - .. code:: python

        print(...)

    - .. code:: javascript

        console.log(...)

  * - .. code:: python

        isinstance(x, y)
        isinstance(x, (y, z))

    - .. code:: javascript

        (x instanceof y)
        (x instanceof y || x instanceof z)

  * - .. code:: python

        typeof(x)

    - .. code:: javascript

        (typeof x)

  * - .. code:: python

        type(x)

    - .. code:: javascript

        Object.getPrototypeOf(x)

  * - .. code:: python

        FirstCharCapitalized(...)
        new(any_function(...))

    - .. code:: javascript

        new FirstCharCapitalized(...)
        new any_function(...)

  * - .. code:: python

        foo in bar

    - .. code:: javascript

        var _pj;
        function _pj_snippets(container) {
            function in_es6(left, right) {
                if (((right instanceof Array) || ((typeof right) === "string"))) {
                    return (right.indexOf(left) > (- 1));
                } else {
                    if (((right instanceof Map) || (right instanceof Set)
                        || (right instanceof WeakMap)
                        || (right instanceof WeakSet))) {
                        return right.has(left);
                    } else {
                        return (left in right);
                    }
                }
            }
            container["in_es6"] = in_es6;
            return container;
        }
        _pj = {};
        _pj_snippets(_pj);
        _pj.in_es6(foo, bar);

  * - .. code:: python

        foo[3:]
        foo[:3]

    - .. code:: javascript

        foo.slice(3);
        foo.slice(0, 3);

  * - .. code:: python

        list(foo).append(bar)

    - .. code:: javascript

        foo.push(bar);

  * - .. code:: python

        dict(foo).update(bar)

    - .. code:: javascript

        Object.assign(foo, bar);

  * - .. code:: python

        dict(foo).copy()

    - .. code:: javascript

        Object.assign({}, foo);


``for`` statement
~~~~~~~~~~~~~~~~~

The ``for`` statement by default is translated as if the object of the
cycle is a list but has two special cases:


.. list-table:: ``for`` loops
  :header-rows: 1

  * - Python
    - JavaScript
    - notes

  * - .. code:: python

        for el in dict(a_dict):
            print(el)

    - .. code:: javascript

        var _pj_a = a_dict;
        for (var el in _pj_a) {
            if (_pj_a.hasOwnProperty(el)) {
                console.log(el);
            }
        }

    - With this kind of loop if you use ``dict(a_dict, True)`` the check on
      ``hasOwnProperty()`` will not be added, so the loop will include
      *inherited* (and *enumerable*) properties.

  * - .. code:: python

        for el in an_array:
            print(el)

    - .. code:: javascript

        for (var el, _pj_c = 0, _pj_a = an_array, _pj_b = _pj_a.length;
              (_pj_c < _pj_b); _pj_c += 1) {
            el = _pj_a[_pj_c];
            console.log(el);
        }

    -

  * - .. code:: python

        for i in range(5):
            print(i)

    - .. code:: javascript

        for (var i = 0, _pj_a = 5; (i < _pj_a); i += 1) {
            console.log(i);
        }

    -

  * - .. code:: python

        for el in iterable(a_set):
            print(el)

    - .. code:: javascript

        var _pj_a = a_set;
        for (var el of  _pj_a) {
            console.log(el);
        }

    - This will loop over all the iterables, like instances of ``Array``,
      ``Map``, ``Set``, etc. **but not over normal objects**.

Functions
~~~~~~~~~

Functions are very well supported. This should be obvious, you can say. Really
it is not so simple, if we mean functions in their broader meaning, including
the  *async functions* and *generator functions*.

.. list-table:: The various types of functions at play
  :header-rows: 1

  * - Python
    - JavaScript
    - notes

  * - .. code:: python

        def foo(a, b, c):
            pass

    - .. code:: javascript

        function foo(a, b, c) {
        }

    - Normal functions

  * - .. code:: python

        def foo(a, b, c):
            for i in range(a, b, c):
                yield i

        for i in iterable(foo(0, 5, 2)):
            print(i)

    - .. code:: javascript

        function* foo(a, b, c) {
            for ... { // loop control omitted for brevity
                yield i;
            }
        }

        for (var i of foo(0, 5, 2)) {
            console.log(i);
        }

    - Generator functions. They return an iterable and to correctly loop over
      it you should use the ``iterable(...)`` call, so that the Python's
      ``for...in`` will be converted into a ``for...of``

  * - .. code:: python

        async def foo(a, b, c):
            await some_promise_based_async


    - .. code:: javascript

        async function foo(a, b, c) {
            await some_promised_base_async;
        }

    - Async functions. They make use of the new ``Promise`` class, which is
      also available.


Function's args and call parameters
+++++++++++++++++++++++++++++++++++

Parmeters defaults and keyword parameters are supported and so is ``*foo``
accumulator, which is translated into the ES6 rest expression (``...foo``).

The only caveat is that JS support for keyword args sucks, so you will have to
**remember to fill in all the arguments before specifying keywords**.

On function definitions, ``**kwargs`` is supported if it's alone, i.e. without
either keyword arguments or ``*args``.

.. list-table:: function's args and call parameters
  :header-rows: 1

  * - Python
    - JavaScript

  * - .. code:: python

        def foo(a=2, b=3, *args):
            pass

    - .. code:: javascript

        function foo(a = 2, b = 3, ...args) {
        }

  * - .. code:: python

        def bar(c, d, *, zoo=2):
            pass

    - .. code:: javascript

        function bar(c, d, {zoo = 2}={}) {
        }

  * - .. code:: python

        foo(5, *a_list)

    - .. code:: javascript

        foo(5, ...a_list);

  * - .. code:: python

        bar('a', 'b', zoo=5, another='c')

    - .. code:: javascript

        bar("a", "b", {zoo: 5, another: "c"});

  * - .. code:: python

        def zoo(e, **kwargs):
            print(kwargs['bar'])

    - .. code:: javascript

        function zoo(e, kwargs = {}) {
            console.log(kwargs['bar'])
        }

  * - .. code:: python

        zoo(4, bar=6)

    - .. code:: javascript

        zoo(4, {bar: 6})

Classes
~~~~~~~

Classes are translated to ES6 classes as much as they can support. This means:

* no direct support multi-class inheritance, you have to come up with your own
  solution for now. Many established frameworks support this in a way or
  another so just use those facilities for now. I've read of some attempts,
  see for example the suggestion on `Mozilla developer`__ or the other about
  `simple mixins`__ on ``Exploring ES6``.

* external implementation for class-level non assignment members. Assignement
  members are those on the body of a class which are defined with: ``a_label =
  an_expression`` like:

  .. code:: python

    class Foo:

        bar = 'zoo' # or any kind of expression

  These members are removed from the translated body and submitted to a
  snippet of code that will run after class creation in JS land. This serves
  two purposes: if the value is *simple*, i.e. it isn't an instance of
  ``Object``, it will be setup as a *data descriptor*, and it will work mostly
  like you are used to in Python. The most noticeable caveat is that it will
  not be accessible through the class as it is in Python, you will have to
  access the class' *prototype*, so in the case above i mean
  ``Foo.prototype.bar``.

  The other purpose is to check for *accessor descriptors*. If the value on
  the right side of the assignment implements a ``get`` function, it will be
  installed as a property as-is, and its *get* and *set* members will be used
  to manage the value with the ``bar`` name.

* external implementation for method decorators whose name is different from
  ``property`` or ``classmethod`` (more on these later on), because these are
  already supported by the ES6 class notation.

* external implementation for class decorators. One caveat here is that the
  return value of the decorator has always to be a function with a prototype:
  unfortunately a ``new`` statement seems not to be *delegable* in any way. So
  for example a class decorator implemented like the following:

  .. code:: python

    def test_class_deco():

        counter = 0

        def deco(cls):
            def wrapper(self, *args):
                counter += 1 # side effect
                return cls(*args)
            return wrapper

        @deco
        class Foo:
            pass

  will never work. This will work instead:

  .. code:: python

    def deco(cls):
        def wrapper(self, *args):
            counter += 1 # side effect
            return cls.prototype.constructor.call(self, *args)
        wrapper.prototype = cls.prototype
        return wrapper

  So either return the original class or setup the wrapper appropriately.


__ https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes#Mix-ins
__ http://exploringjs.com/es6/ch_classes.html#_simple-mixins


Methods can be functions or async-functions although the latters aren't
officially supported yet by the JavaScript specification. You can disable them
adding a ``--disable-stage3`` to the command line utility.

Python`s ``super()`` calls are converted accordingly to the type of
their surrounding method: ``super().__init__(foo)`` becomes
``super(foo)`` in constructors.

Functions inside methods are translated to arrow functions so that
they keep the ``this`` of the surrounding method.

``@property`` and ``@a_property.setter`` are translated to ES6 properties.

Methods decorated with ``@classmethod`` are translated to ``static`` methods.

Special methods ``__str__`` and ``__len__`` are translated to
``toString()`` method and ``get length()`` property, respectively.

Arrow method expression to retain the ``this`` at method level aren't
implemented yet.


.. list-table:: Classes
  :header-rows: 1

  * - Python
    - JavaScript

  * - .. code:: python

        class Foo(bar):
            def __init__(self, zoo):
                super().__init__(zoo)


            def meth(self, zoo):
                super().meth(zoo)
                def cool(a, b, c):
                    print(self.zoo)


            async def something(self, a_promise):
                result = await a_promise

            def generator_method(self):
                yield something

            @property
            def foo(self):
                return self._foo


            @foo.setter
            def foo(self, value):
                self._foo = value


            @classmethod
            def bar(self, val):
                do_something()


            def __len__(self):
                return 1


            def __str__(self):
                return 'Foo instance'

    - .. code:: javascript

        class Foo extends bar {
            constructor(zoo) {
                super(zoo);
            }

            meth(zoo) {
                super.meth(zoo);
                var cool;
                cool = (a, b, c) => {
                    console.log(this.zoo);
                };
            }

            async something(a_promise) {
                var result;
                result = await a_promise;
            }

            * generator_method() {
                yield something;
            }

            get foo() {
                return this._foo;
            }

            set foo(value) {
                self._foo = value;
            }

            static bar(val) {
                do_something()
            }

            get length() {
                return 1;
            }

            toString() {
                return "Foo instance";
            }
        }

Only direct descendants of ``Exception`` are threated especially, but
just for them to be meaningful in JS land and to be detectable with
``instanceof`` in catch statements.


.. list-table:: Exceptions
  :header-rows: 1

  * - Python
    - JavaScript

  * - .. code:: python

        class MyError(Exception):
            pass

        raise MyError("An error occurred")

    - .. code:: javascript

        function MyError(message) {
            this.name = "MyError";
            this.message = (message || "Custom error MyError");
            if (((typeof Error.captureStackTrace) === "function")) {
                Error.captureStackTrace(this, this.constructor);
            } else {
                this.stack = new Error(message).stack;
            }
        }
        MyError.prototype = Object.create(Error.prototype);
        MyError.prototype.constructor = MyError;
        throw new MyError("An error occurred");


``try...except...finally`` statement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The conversion of this statement is mostly obvious with the only
exception of the ``except`` part: it translates to a ``catch`` part
containing one ``if`` statement for each non catchall ``except``. If a
catchall ``except`` isn't present, the error will be re-thrown, to mimic
Python's behavior.

.. list-table:: ``try...catch...finally`` statement
  :header-rows: 1

  * - Python
    - JavaScript

  * - .. code:: python

        try:
            foo.bar()
        except MyError:
            recover()
        except MyOtherError:
            recover_bad()
        finally:
            foo.on_end()

    - .. code:: javascript

        try {
            foo.bar();
        } catch(e) {
            if ((e instanceof MyError)) {
                recover();
            } else {
                if ((e instanceof MyOtherError)) {
                    recover_bad()
                } else {
                    throw e;
                }
            }
        } finally {
            foo.on_end();
        }


``import`` statements
~~~~~~~~~~~~~~~~~~~~~

``import`` and ``from ... import`` statements are converted to ES6
imports, and the declaration of an ``__all__`` member on the module
top level is translated to ES6 exports.


.. list-table:: import and exports
  :header-rows: 1

  * - Python
    - JavaScript

  * - .. code:: python

        import foo, bar
        import foo.bar as b
        from foo.bar import hello as h, bye as bb
        from ..foo.zoo import bar
        from . import foo
        from .foo import bar

        from foo__bar import zoo

        from __globals__ import test_name

        # this should not trigger variable definition
        test_name = 2

        # this instead should do it
        test_foo = True

        __all__ = ['test_name', 'test_foo']

    - .. code:: javascript

        var test_foo;

        import * as foo from 'foo';
        import * as bar from 'bar';
        import * as b from 'foo/bar';
        import {hello as h, bye as bb} from 'foo/bar';
        import {bar} from '../foo/zoo';
        import * as foo from './foo';
        import {bar} from './foo';

        import {zoo} from 'foo-bar';

        test_name = 2;
        test_foo = true;

        export {test_name};
        export {test_foo};

Examples
--------

Execute ``make`` inside the ``examples`` directory.

Testing
-------

To run the tests you should run the following at the package root::

  python setup.py test

How to contribute
-----------------

So you like this project and want to contribute? Good!

These are the terse guidelines::

  There are some TODO points in the readme, or even the issue #6 is
  quite simple to fix. Feel free to pick what you like.

  The guidelines are to follow PEP8 for coding where possible, so use
  CamelCase for classes and snake_case for variables, functions and
  members, and UPPERCASE for constants.

  An exception to this rules are the function names inside
  ``metapensiero.pj.transformations`` subpackage. Those are matched
  against names of the ast objects coming from the ``ast`` module in
  standard lib, so they have to to match even in case.

  Try to keep lines lengths under 79 chars, more or less ;-)

  The workflow is to fork the project, do your stuff, maybe add a test
  for it and then submit a pull request.

  Have fun


Build status
------------

.. image:: https://travis-ci.org/azazel75/metapensiero.pj.svg?branch=master
    :target: https://travis-ci.org/azazel75/metapensiero.pj

Contributing
------------

Any contribution is welcome, drop me a line or file a pull request.

Todo
----

This is a brief list of what needs to be done:

* refactor the comprehensions conversion to use the snippets facility;
* refactor snippets rendering to write them as a module and import
  them in the module when tree conversion is enabled;
* convert ``dict()`` calls to ES6 ``Map`` object creation;
* convert *set* literals to ES6 ``Set`` objects. Also, update
  "foo in bar" to use bar.has(foo) for sets;
* multi-line strings to ES6 template strings (does this make any sense?);

Done
----

Stuff that was previously in the todo:

* translate *import* statements to ES6;
* translate ``__all__`` definition to ES6 module exports;
* write a command line interface to expose the api;
* make try...except work again and implement try...finally;
* convert *async* and *await* to the same proposed features for js
  (see BabelJS documentation);
* convert argument defaults on functions to ES6;
* convert call keyword arguments;
* convert `*iterable` syntax to ES6 destructuring;
* use arrow functions for functions created in functions;
* properties to ES6 properties (getter and setter);
* take advantage of new duckpy features to use a JS execution context
  that lasts multiple calls. This way the BabelJS bootstrap affects
  only the initial execution;
* class and method decorators;
* implement *yield*, *yield from* and generator functions;
* update "foo in bar" to use bar.has(foo) for maps;


External documentation
----------------------

A good documentation and explanation of ES6 features can be found on
the book `Exploring ES6`__ by Axel Rauschmayer (donate if you can).

__ http://exploringjs.com/es6/

An `extensive documentation`__ about Python's ast objects, very handy.

__ https://greentreesnakes.readthedocs.org/en/latest/

Tools
-----

Have a look at `ECMAScript 6 Tools`__ by Addy Osmani.

__ https://github.com/addyosmani/es6-tools

To debug *source maps* have a look at `source-map-visualization`__ and
its `package`__ on npm.

__ https://sokra.github.io/source-map-visualization/
__ https://www.npmjs.com/package/source-map-visualize

Still i found these links to be helpful:

* `BASE64 VLQ CODEC (COder/DECoder)`__
* `Testing Source Maps`__

__ http://murzwin.com/base64vlq.html
__ http://fitzgeraldnick.com/2013/08/02/testing-source-maps.html

Here is an `example`__ of the latter tool showing code generated by
JavaScripthon, have fun!

__ https://sokra.github.io/source-map-visualization/#base64,ZnVuY3Rpb24gc2ltcGxlX2FsZXJ0KCkgewogICAgd2luZG93LmFsZXJ0KCJIaSB0aGVyZSEiKTsKfQpmdW5jdGlvbiBhdHRhY2hfaGFuZGxlcigpIHsKICAgIHZhciBlbDsKICAgIGVsID0gZG9jdW1lbnQucXVlcnlTZWxlY3RvcigiYnV0dG9uIik7CiAgICBlbC5hZGRFdmVudExpc3RlbmVyKCJjbGljayIsIHNpbXBsZV9hbGVydCk7Cn0KYXR0YWNoX2hhbmRsZXIoKTsKCi8vIyBzb3VyY2VNYXBwaW5nVVJMPWh0bWxfdGVzdC5qcy5tYXAK,eyJtYXBwaW5ncyI6IkFBT0E7SUFDSUEsTUFBQUMsTUFBQSxDQUFhLFdBQWI7QUFESjtBQUdBOztJQUNJQyxLQUFLQyxRQUFBQyxjQUFBLENBQXVCLFFBQXZCO0lBQ0xGLEVBQUFHLGlCQUFBLENBQW9CLE9BQXBCLEVBQTZCQyxZQUE3QjtBQUZKO0FBSUFDLGNBQUEiLCJzb3VyY2VzIjpbImh0bWxfdGVzdC5weSJdLCJ2ZXJzaW9uIjozLCJuYW1lcyI6WyJ3aW5kb3ciLCJ3aW5kb3cuYWxlcnQiLCJlbCIsImRvY3VtZW50IiwiZG9jdW1lbnQucXVlcnlTZWxlY3RvciIsImVsLmFkZEV2ZW50TGlzdGVuZXIiLCJzaW1wbGVfYWxlcnQiLCJhdHRhY2hfaGFuZGxlciJdLCJzb3VyY2VzQ29udGVudCI6WyIjIC0qLSBjb2Rpbmc6IHV0Zi04IC0qLVxuIyA6UHJvamVjdDogIHBqIC0tIHRlc3QgZm9yIGh0bWxcbiMgOkNyZWF0ZWQ6ICAgIG1hciAwMSBtYXIgMjAxNiAyMzo0ODo1MiBDRVRcbiMgOkF1dGhvcjogICAgQWxiZXJ0byBCZXJ0aSA8YWxiZXJ0b0BtZXRhcGVuc2llcm8uaXQ+XG4jIDpMaWNlbnNlOiAgIEdOVSBHZW5lcmFsIFB1YmxpYyBMaWNlbnNlIHZlcnNpb24gMyBvciBsYXRlclxuI1xuXG5kZWYgc2ltcGxlX2FsZXJ0KCk6XG4gICAgd2luZG93LmFsZXJ0KCdIaSB0aGVyZSEnKVxuXG5kZWYgYXR0YWNoX2hhbmRsZXIoKTpcbiAgICBlbCA9IGRvY3VtZW50LnF1ZXJ5U2VsZWN0b3IoJ2J1dHRvbicpXG4gICAgZWwuYWRkRXZlbnRMaXN0ZW5lcignY2xpY2snLCBzaW1wbGVfYWxlcnQpXG5cbmF0dGFjaF9oYW5kbGVyKClcbiJdfQ==,IyAtKi0gY29kaW5nOiB1dGYtOCAtKi0KIyA6UHJvamVjdDogIHBqIC0tIHRlc3QgZm9yIGh0bWwKIyA6Q3JlYXRlZDogICAgbWFyIDAxIG1hciAyMDE2IDIzOjQ4OjUyIENFVAojIDpBdXRob3I6ICAgIEFsYmVydG8gQmVydGkgPGFsYmVydG9AbWV0YXBlbnNpZXJvLml0PgojIDpMaWNlbnNlOiAgIEdOVSBHZW5lcmFsIFB1YmxpYyBMaWNlbnNlIHZlcnNpb24gMyBvciBsYXRlcgojCgpkZWYgc2ltcGxlX2FsZXJ0KCk6CiAgICB3aW5kb3cuYWxlcnQoJ0hpIHRoZXJlIScpCgpkZWYgYXR0YWNoX2hhbmRsZXIoKToKICAgIGVsID0gZG9jdW1lbnQucXVlcnlTZWxlY3RvcignYnV0dG9uJykKICAgIGVsLmFkZEV2ZW50TGlzdGVuZXIoJ2NsaWNrJywgc2ltcGxlX2FsZXJ0KQoKYXR0YWNoX2hhbmRsZXIoKQo=


Notes
-----

* A `post`__ about proposed solutions to use ES6 classes with
  `Backbone`__. See also the `bug`__ open on github.

__ http://benmccormick.org/2015/07/06/backbone-and-es6-classes-revisited/
__ http://backbonejs.org
__ https://github.com/jashkenas/backbone/issues/3560


* A `benchmark of ES6 features`__ and `discussion about it`__ on
  hacker's news.

__ https://kpdecker.github.io/six-speed/
__ https://news.ycombinator.com/item?id=11203183

* A `compatibility table of ES6 features`__ showing completeness of
  support feature by feature.

__ http://kangax.github.io/compat-table/es6/

* `A story`__ about ES6 crazyest stuff... symbols

__ http://blog.keithcirkel.co.uk/metaprogramming-in-es6-symbols/
