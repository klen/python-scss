Usage
=====

#. **From python source code**: ::

    from scss import parser
    src = file.read()
    print parser.parse('src')

#. **From command line**: ::

    scss test.scss

#. **In interactive mode**: ::

    scss -i

    >>> 25px + 1.5em
