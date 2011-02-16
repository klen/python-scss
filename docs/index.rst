.. python-scss documentation master file, created by
   sphinx-quickstart on Wed Feb 16 19:24:45 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to python-scss's documentation!
=======================================

Python-scss is scss compiler for python. See http://sass-lang.com for more information about scss syntax.
This is part of zeta-library_.


Features
--------
Currently it implements @mixin, @include, @if, @for. From sass function ready only 'enumerate',
color sass function be done in future, but now supported color lighten operation ex: color: #456 + 10%
For @import support with python-scss you may use zeta-library_ - my analog compass, with included js and css framework.
Zeta-library support @import only by file path, ex: @import url(path/child.scss), but zeta support css, scss and js imports( require ),
is solution for control all your static files ( css, scss, js )


Requirements
-------------

- python >= 2.5
- pyparsing
- pip >= 0.8


Contents:
---------

.. toctree::
   :maxdepth: 2

   usage
   examples

Make sure you`ve read the following document if you are upgrading from previous versions of makesite:

.. toctree::
   :maxdepth: 1

   changes

.. note::

    python-scss is still at early stages of development


Bug tracker
===========

If you have any suggestions, bug reports or
annoyances please report them to the issue tracker
at https://github.com/klen/python-scss/issues


Contributing
============

Development of python-scss happens at github:
https://github.com/klen/python-scss


License
=======

Licensed under a `GNU lesser general public license`_.


.. _zeta-library: http://github.com/klen/zeta-library
.. _GNU lesser general public license: http://www.gnu.org/copyleft/lesser.html
