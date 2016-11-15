.. -*- coding: utf-8 -*-

Changes
-------


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
