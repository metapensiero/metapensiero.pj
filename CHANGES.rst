.. -*- coding: utf-8 -*-

Changes
-------

0.12 (2022-07-19)
-----------------

- remove macropy
- fix evaluation from commandline
- deprecate Python 3.5 and 3.6
- tested on Python 3.10


0.11 (2020-03-30)
~~~~~~~~~~~~~~~~~

- update test infrastructure to work with latest ``pytest``;
- add support for Python 3.7 and 3.8 (thanks to Richard Höchenberger).
- do not crash when translating source with assignment typehints (
  with the help of Sirenfal)

0.10 (2018-05-12)
~~~~~~~~~~~~~~~~~

- use Macropy3 version 1.1.0b2 to avoid issues with Django

0.9 (2018-04-19)
~~~~~~~~~~~~~~~~

- add a ``--source-name`` options to be used together with
  ``--inline-map`` when using ``-s``;
- move main repository to gitlab.com/metapensiero;
- add support for default export and import;
- add documentation for the ``JS()`` marker function;
- refactor of the JS AST nodes;
- fix path splitting and joining on Windows (thanks to Roman Yakubuk);

0.8 (2017-11-16)
~~~~~~~~~~~~~~~~

- add support for ``except`` sections with more than one exception
  type and arbitrary exception variable name. Thanks to @devanlai;
- dict keys conversion fixes;
- enable ``--inline-map`` when translating a string with ``-s``;


0.7 (2017-09-08)
~~~~~~~~~~~~~~~~

- translate dicts unambiguously, using "computed member name form" for
  keys that aren't strings;
- use ``macropy`` package to deal with some of the translation
  details;
- translate ``int()`` and ``float()``;
- fix a bug that prevented BabelJS translation when keyword arguments;
  are present;

0.6 (2017-05-09)
~~~~~~~~~~~~~~~~~

- allow to define template literals and tagged templates;
- define package scopes in imports prepending names with ``__``;
- translate ``issubclass()``;
- translate lambdas as arrow functions;
- translate Python 3.6+ f-strings to ES6 template literals;
- Add translation for ``__instancecheck__`` to ``[Symbol.hasInstance]``;
- Sort imports alphabetically;

0.5 (2016-11-23)
~~~~~~~~~~~~~~~~

- translate ``tmpl("A string with js ${interpolation}")`` to ES6 template
  literals;
- preliminary support to translate names like ``d_foo`` and ``dd_bar`` to
  ``$foo`` and ``$$bar``;
- addded translation of the ``assert`` statement;
- fixed a bug in ``try...except...finally`` statement when there's no
  ``except`` section;
- added translation for ``foo is not bar`` that seems to have dedicated ast
  node;
- if the function is defined in a method but starts with ``fn_`` do not convert
  it to an arrow function. Useful to *not* maintain ``this``;
- added translation for ``callable`` and ``hasattr/getattr/setattr``;
- updated for loops to support more than one target, so now its possible to
  write loops like ``for k, v in iterable(a_map):``;
- updated documentation;
- added a new cli option ``-s`` to translate source from the command line or
  the standard input;
- fixed a pair of bugs on sourcemaps;
- added a new cli option ``--eval`` to also evaluate the produced JavaScript
  using the embedded interpreter;
- added a new cli option ``--dump-ast`` to print out the ast tree of the
  passed in string;
- added sorting to the rendered snippets/decorators/assignments so that their
  order does not change at every ricompilation;
- do not re-declare variables declare in outer scopes;

0.4 (2016-11-15)
~~~~~~~~~~~~~~~~

- updated BabelJS to version 6.18.1;
- allow to import modules with dashes inside by using dunder-inside-words
  notation (``foo__bar`` becomes ``foo-bar``);
- reuse JavaScript interpreter context to speedup translation;
- update ``in`` operator to support ES6 collections;
- added support for method and class decorators;
- added support for class properties and descriptors;
- add ``for`` loop over JS iterables;
- allow to loop over inherited properties;
- fix a bug on ``type()`` translation;
- support for ``range()`` steps;
- add support for generator functions and ``yield`` and ``yield from``
  expressions;
- optionally load babel-polyfill before evaluating code;
- fix a bug on sourcemaps having wrong references when there are documentation
  elements;
- translate ``__get__()`` and ``__set__()`` to to JS equivalents;
- implement ``dict(foo).update(bar)`` and ``dict(foo).copy``;
- documentation improvements;

0.3 (2016-04-08)
~~~~~~~~~~~~~~~~

- updates to the documentation ( with some fixes made by Hugo Herter,
  Daniel Kopitchinski and ironmaniiith)
- Translate ``str(x)`` into ``x.toString()``
- Add support for properties and classmethods
- Translate ``__len__`` and ``__str__`` methods to ``get length()``
  and ``toString()``
- Add support for slices syntax to ``.slice()``
- Fixed two bugs in sourcemaps generation
- Fixed a bug in the ``inport ... from`` translation
- Correctly include BabelJS minimized code
- Fix transpiling of stage3 features

0.2 (2016-03-29)
~~~~~~~~~~~~~~~~

- use arrow functions to retain ``this`` were possible
- translate ``async/await``
- refactoring of the ``for`` loops
- add ability to subtranslate pieces of Python code or objects. Used
  to template the creation of ``Exception`` sublasses
- add support for param defaults and keyword arguments
- updated documentation

0.1 (2016-03-21)
~~~~~~~~~~~~~~~~

- First cut of the features
