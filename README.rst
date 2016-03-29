.. -*- coding: utf-8 -*-
.. :Project:  pj -- readme
.. :Created:    mar 01 mar 2016 15:52:36 CET
.. :Author:    Alberto Berti <alberto@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
..

======================================================
javascripthon: a Python 3 to ES6 JavaScript translator
======================================================

 :author: Alberto Berti
 :contact: alberto@metapensiero.it
 :license: GNU General Public License version 3 or later

It is based on previous work by `Andrew Schaaf <andrew@andrewschaaf.com>`_.

Goal
----

JavaScripthon is a small and simple Python 3 translator to JavaScript
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
has BabelJS integration to getting this job done.

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

To install the package execute the following command::

  $ pip install javascripthon

Usage
-----

To *compile* or *transpile* a python source module, use the
commandline:

.. code:: bash

  $ python -m pj source.py

or:

.. code:: bash

  $ python -m pj -5 source.py

to transpile. As of now  it doesn't check which features require a
transpilation, so the latter is always safer.

Examples
--------

Execute ``make`` inside the ``examples`` directory.

Testing
-------

To run the tests you should run the following at the package root::

  python setup.py test


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

* use arrow functions for functions created in functions;
* refactor the comprehensions conversion to use the snippets facility;
* refactor snippets rendering to write them as a module and import
  them in the module when tree conversion is enabled;
* convert ``dict()`` calls to ES6 ``Map`` object creation;
* convert *set* literals to ES6 ``Set`` objects;
* convert *async* and *await* to the same proposed features for js
  (see BabelJS documentation);
* convert `*iterable` syntax to ES6 destructuring;
* convert argument defaults on functions to ES6;
* multi-line strings to ES6 template strings (does this make any sense?);
* properties to ES6 properties (getter and setter);
* class and method decorators to ES7 class and method decorators;
* implement *yield* and generator functions;

Done
----

Stuff that was previously in the todo:

* translate *import* statements to ES6;
* translate ``__all__`` definition to ES6 module exports;
* write a command line interface to expose the api;
* make try...except work again and implement try...finally;

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
