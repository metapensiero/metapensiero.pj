.. -*- coding: utf-8 -*-
.. :Project:  pj -- readme
.. :Created:    mar 01 mar 2016 15:52:36 CET
.. :Author:    Alberto Berti <alberto@metapensiero.it>
.. :License:   GNU General Public License version 3 or later
..

========================================
PJ a Python 3 to ES6 JavaScript compiler
========================================

 :author: Alberto Berti
 :contact: alberto@metapensiero.it

It is based on previous work by `Andrew Schaaf <andrew@andrewschaaf.com>`_.

Goal
----

PJ is a small and simple Python 3 translator to JavaScript which aims
to be able to translate most of the Python's core semantics without
providing a full python-in-js environment, as most existing
translators do. It tries to emit code which is simple to read and
check and it does so by switching to ES6 construct when
necessary. This allows to simplify the needs of polyfills for many of
the expected Python behaviors.

The interface with the js world is completely flat, import the modules
or use the expected globals (``window``, ``document``, etc...) as you
would do in JavaDcript

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

PJ tries to generate also `SourceMap`__ files with the higher detail
possible in order to aid development.

__ http://blog.teamtreehouse.com/introduction-source-maps

This project is far from complete, but it has achieved a good deal of
features, please have a look at ``tests/test_evaljs.py`` file for the
currently supported ones.

Todo
----

This is a brief list of what needs to be done:

* translate *import* statements to ES6;
* translate ``__all__`` definition to ES6 module exports;
* write a command line interface to expose the api;
* refactor the comprehensions conversion to use the snippets facility;
* refactor snippets rendering to write them as a module and import
  them in the module when tree conversion is enabled;
* convert ``dict()`` calls to ES6 ``Map`` object creation;
* convert *set* literals to ES6 ``Set`` objects;
* convert *async* and *await* to the same proposed features for js
  (see BabelJS documentation);
* convert `*iterable` syntax to ES6 destructuring;
* convert argument defaults on functions to ES6;


External documentation
----------------------

A good documentation and explanation of ES6 features can be found on
the book `Exploring ES6`__ by Axel Rauschmayer (donate if you can).

__ http://exploringjs.com/es6/


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
