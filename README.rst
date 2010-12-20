..   -*- mode: rst -*-

python-scss
#######

Python-scss is scss parser. See http://sass-lang.com for more information about scss syntax.

.. contents::

Requirements
-------------

- python >= 2.5
- pyparsing
- pip >= 0.8


Installation
------------

**scss** should be installed using pip: ::

    pip install scss


Using
-----
example: ::

    from scss import parse
    src = file.read()
    print parse('src')


