..   -*- mode: rst -*-

python-scss
############

Python-scss is scss compiler for python. See http://sass-lang.com for more information about scss syntax.
This is part of zeta-library_.

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


Usage
-----
example: ::

    from scss import parser
    src = file.read()
    print parser.parse('src')


Examples
--------

#. **Nested Rules**
    Example::

	.selector {
	    a {
	        display: block;
	    }
	    strong {
	        color: blue;
	    }
	}

    ...produces::

        .selector a {
            display: block}

        .selector strong {
            color: blue}


#. **Variables**
    Example::

        $main-color: #ce4dd6;
        $style: solid;
        $side: bottom;
        #navbar {
            border-#{$side}: {
            color: $main-color;
            style: $style;
            }
        }

    ...produces::

        #navbar {
            border-bottom-color: #ce4dd6;
            border-bottom-style: solid}

#. **Mixins**
    Example::

        @mixin rounded($side, $radius: 10px) {
            border-#{$side}-radius: $radius;
            -moz-border-radius-#{$side}: $radius;
            -webkit-border-#{$side}-radius: $radius;
        }
        #navbar li { @include rounded(top); }
        #footer { @include rounded(top, 5px); }
        #sidebar { @include rounded(left, 8px); }

    ...produces::

        #navbar li {
                -moz-border-radius-top: 10px;
                -webkit-border-top-radius: 10px;
                border-top-radius: 10px}

        #footer {
                -moz-border-radius-top: 5px;
                -webkit-border-top-radius: 5px;
                border-top-radius: 5px}

        #sidebar {
                -moz-border-radius-left: 8px;
                -webkit-border-left-radius: 8px;
                border-left-radius: 8px}

#. **Extend** (using `@extend`)
    Example::

        .error {
            border: 1px #f00;
            background-color: #fdd;
        }
        .error.intrusion {
            background-image: url("/image/hacked.png");
        }
        .seriousError {
            @extend .error;
            border-width: 3px;
        }

    ...produces::

        .error, .seriousError {
            background-color: #fdd;
            border: 1px #f00}

        .error .intrusion, .seriousError .intrusion {
            background-image: url('/image/hacked.png')}

        .seriousError {
            border-width: 3px}



Features
--------
Currently it implements @mixin, @include, @if, @for. From sass function ready only 'enumerate',
color sass function be done in future, but now supported color lighten operation ex: color: #456 + 10%
For @import support with python-scss you may use zeta-library_ - my analog compass, with included js and css framework.
Zeta-library support @import only by file path, ex: @import url(path/child.scss), but zeta support css, scss and js imports( require ),
is solution for control all your static files ( css, scss, js )

Your feedback is welcome.


.. _zeta-library: http://github.com/klen/zeta-library
