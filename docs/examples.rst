Examples
========

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

#. **Interactive mode**
    Example::

	$ python scss.py --interactive
	>>> 25px + 1.5em
        44.5px
        >>> lighten(rgba(130,130,130,.4),10%)
        rgba(155,155,155,0.40)
        >>> .rule { test: red; }
        .rule {
            test: red }
	>>> _
