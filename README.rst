.. -*- coding: utf-8 -*-
.. :Project:  pj -- readme
.. :Created:    mar 01 mar 2016 15:52:36 CET
.. :Author:    Alberto Berti <alberto@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
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

Goal
----

JavaScripthon is a small and simple Python 3.5+ translator to JavaScript
which aims to be able to translate most of the Python's core semantics
without providing a full python-in-js environment, as most existing
translators do. It tries to emit code which is simple to read and
check and it does so by switching to ES6 construct when
necessary. This allows to simplify the needs of polyfills for many of
the expected Python behaviors.

The interface with the js world is completely flat, import the modules
or use the expected globals (``window``, ``document``, etc...) as you
would do in JavaScript.

The ES6 code is then converted (if requested) to ES5 code with the aid
of the popular `BabelJS`__ library together with the fantastic
`dukpy`__ embedded js interpreter.

__ http://babeljs.io/
__ https://github.com/amol-/dukpy

Another goal is to just convert single modules or entire dir tree
structures without emitting concatenated or minified files. This is
left to the Javascript tooling of your choice. I use `webpack`__ which
has BabelJS integration to getting this job done. Check out the bundled
example.

__ http://webpack.github.io/

JavaScripthon also generates `SourceMap`__ files with the higher detail
possible in order to aid development. This means that while you are
debugging some piece of translated JavaScript with the browser's
tools, you can actually choose to follow the flow of the code on the
original Pyhton 3 source.

__ http://blog.teamtreehouse.com/introduction-source-maps

This project is far from complete, but it has achieved a good deal of
features, please have a look at ``tests/test_evaljs.py`` file for the
currently supported ones.

Installation
------------

Python 3.5 is required because Python's ast has changed between 3.4
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

Here are brief list of examples of the conversions the tool applies,
just some, but not all.

Simple stuff
~~~~~~~~~~~~

.. list-table:: Most are obvious
  :header-rows: 1

  * - Python
    - JavaScript

  * - .. code:: python

        x < y <= z < 5

        def foo():
            return [True, False, None, 1729,
                    "foo", r"foo\bar", {}]


        while len(foo) > 0:
            print(foo.pop())


        if foo > 0:
            ....
        elif foo < 0:
            ....
        else:
            ....




        str(x)

    - .. code:: javascript

        ((x < y) && (y <= z) && (z < 5))

        function foo() {
            return [true, false, null, 1729,
                    "foo", "foo\\bar", {}];
        }

        while ((foo.length > 0)) {
            console.log(foo.pop());
        }

        if ((foo > 0)) {
            ....
        } else {
            if ((foo < 0)) {
                ....
            } else {
                ....
            }
        }

        x.toString()


Then there are special cases. Here you can see some of these
conversions. JavaScripthon cannot do a full trace of the sources, so
some shortcuts are taken about the conversion of some core, specific
Python's semantics. For example Python's ``self`` is always converted
to JavaScript's ``this``, no matter where it's found. Or ``len(foo)``
is always translated to ``foo.length``. Albeit this an api specific of
just some objects (Strings, Arrays, etc...), it considered wide
adopted and something the user may consider obvious.

The rules of thumb to treat things especially are:

* Is it possible to think of a conversion that covers most of the use
  cases?

* It's possible to find a convention widely used on the Python world
  to express this special case?

.. list-table:: There are special cases
  :header-rows: 1

  * - Python
    - JavaScript

  * - .. code:: python

        ==
        !=
        2**3
        'docstring'

        self
        len(...)
        print(...)
        isinstance(x, y)
        typeof(x)

        FirstCharCapitalized(...)















        foo in bar

        foo[3:]
        foo[:3]

    - .. code:: javascript

        ===
        !==
        Math.pow(2, 3)
        /* docstring */

        this
        (...).length
        console.log(...)
        (x instanceof y)
        (typeof x)

        new FirstCharCapitalized(...)

        var _pj;
        function _pj_snippets(container) {
            function _in(left, right) {
                if (((right instanceof Array) || ((typeof right) === "string"))) {
                    return (right.indexOf(left) > (- 1));
                } else {
                    return (left in right);
                }
            }
            container["_in"] = _in;
            return container;
        }
        _pj = {};
        _pj_snippets(_pj);
        _pj._in(foo, bar);

        foo.slice(3);
        foo.slice(0, 3);

``for`` statement
~~~~~~~~~~~~~~~~~

The ``for`` statement by default is translated as if the object of the
cycle is a list but has two special cases:

.. list-table:: ``for`` loops
  :header-rows: 1

  * - Python
    - JavaScript

  * - .. code:: python

        for el in dict(a_dict):
            print(el)





        for el in an_array:
            print(el)




        for i in range(5):
            print(i)

    - .. code:: javascript

        var _pj_a = a_dict;
        for (var el in _pj_a) {
            if (_pj_a.hasOwnProperty(el)) {
                console.log(el);
            }
        }

        for (var el, _pj_c = 0, _pj_a = an_array, _pj_b = _pj_a.length;
              (_pj_c < _pj_b); _pj_c += 1) {
            el = _pj_a[_pj_c];
            console.log(el);
        }

        for (var i = 0, _pj_a = 5; (i < _pj_a); i += 1) {
            console.log(i);
        }

Classes
~~~~~~~

Classes with single inheritance are translated to ES6 classes, they
can have only function members for now, with no generic class or
method decorators, because the ES7 spec for them is being rediscussed.

Methods can be functions or async-functions.

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
just for them to be meaningful in js-land and to be detectable with
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

        test_name = 2;
        test_foo = true;

        export {test_name};
        export {test_foo};


function's args and call parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parmeters defaults and keyword parameters are supported and so is
``*foo`` accumulator, which is translated into the ES6 rest expression
(``...foo``).

The only caveat is that really JS support for keyword args sucks, so
you will have to remember to fill in all the arguments before
specifying keywords.

On function definitions, ``**kwargs`` is supported if it's alone,
i.e. without either keyword arguments or ``*args``.

.. list-table:: function's args and call parameters
  :header-rows: 1

  * - Python
    - JavaScript

  * - .. code:: python

        def foo(a=2, b=3, *args):
            pass

        def bar(c, d, *, zoo=2):
            pass

        foo(5, *a_list)

        bar('a', 'b', zoo=5, another='c')

        def zoo(e, **kwargs):
            print(kwargs['bar'])


        zoo(4, bar=6)

    - .. code:: javascript

        function foo(a = 2, b = 3, ...args) {
        }

        function bar(c, d, {zoo = 2}={}) {
        }

        foo(5, ...a_list);

        bar("a", "b", {zoo: 5, another: "c"});

        function zoo(e, kwargs = {}) {
            console.log(kwargs['bar'])
        }

        zoo(4, {bar: 6})

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
* convert ``dict()`` calls to ES6 ``Map`` object creation. Also,
  update "foo in bar" to use bar.has(foo) for maps;
* convert *set* literals to ES6 ``Set`` objects. Also, update
  "foo in bar" to use bar.has(foo) for sets;
* multi-line strings to ES6 template strings (does this make any sense?);
* class and method decorators to ES7 class and method decorators;
* implement *yield* and generator functions;
* take advantage of new duckpy features to use a JS execution context
  that lasts multiple calls. This way the BabelJS bootstrap affects
  only the initial execution;

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
__ http://fitzgeraldnick.com/weblog/51/

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
