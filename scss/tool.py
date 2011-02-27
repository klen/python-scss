""" Command-line tool to parse scss file.
"""
import optparse
import sys, os
import time

from scss import parser, VERSION


COMMANDS = ['import', 'option', 'mixin', 'include', 'for', 'if', 'else']

def complete(text, state):
    for cmd in COMMANDS:
        if cmd.startswith(text):
            if not state:
                return cmd
            else:
                state -= 1

def main():

    try:
        import atexit
        import readline
        history = os.path.join(os.environ['HOME'], ".scss-history")
        atexit.register(readline.write_history_file, history)
        readline.parse_and_bind("tab: complete")
        readline.set_completer(complete)
        readline.read_history_file(history)
    except ( ImportError, IOError ):
        pass

    p = optparse.OptionParser(
        usage="%prog [OPTION]... [INFILE] [OUTFILE]",
        version="%prog " + VERSION,
        epilog="SCSS compiler.",
        description="Compile INFILE or standard input, to OUTFILE or standard output.")

    p.add_option(
        '-c', '--cache', action='store_true', dest='cache',
        help="Create and use cache file. Only for files.")

    p.add_option(
        '-i', '--interactive', action='store_true', dest='shell',
        help="Run in interactive shell mode.")

    p.add_option(
        '-m', '--compress', action='store_true', dest='compress',
        help="Compress css output.")

    p.add_option(
        '-w', '--watch', dest='watch',
        help="""Watch files or directories for changes.
The location of the generated CSS can be set using a colon:
    scss -w input.scss:output.css
""")

    p.add_option(
        '-S', '--no-sorted', action='store_false', dest='sort',
        help="Do not sort declaration.")

    p.add_option(
        '-C', '--no-comments', action='store_false', dest='comments',
        help="Clear css comments.")

    p.add_option(
        '-W', '--no-warnings', action='store_false', dest='warn',
        help="Disable warnings.")

    opts, args = p.parse_args()
    precache = opts.cache

    if opts.shell:
        p = parser.Stylecheet()
        print 'SCSS v. %s interactive mode' % VERSION
        print '================================'
        print 'Ctrl+D or quit for exit'
        while True:
            try:
                s = raw_input('>>> ').strip()
                if s == 'quit':
                    raise EOFError
                print p.parse(s)
            except ( EOFError, KeyboardInterrupt ):
                print '\nBye bye.'
                break

        sys.exit()

    elif opts.watch:
        self, sep, target = opts.watch.partition(':')
        files = []
        if not os.path.exists(self):
            print >> sys.stderr, "Path don't exist: %s" % self
            sys.exit(1)

        if os.path.isdir(self):
            for f in os.listdir(self):
                if os.path.isfile(f) and f.endswitch('.scss'):
                    path = os.path.join(self, f)
                    tpath = os.path.join(target, f[:-5] + '.css')
                    files.append([ path, tpath, 0 ])
        else:
            files.append([ self, target or self[:-5] + '.css', 0 ])

        s = parser.Stylecheet(
            options=dict(
                comments = opts.comments,
                compress = opts.compress,
                warn = opts.warn,
                sort = opts.sort,
                cache = precache,
            ))

        def parse(f):
            infile, outfile, mtime = f
            ttime = os.path.getmtime(infile)
            if mtime < ttime:
                print " Parse '%s' to '%s' .. done" % ( infile, outfile )
                s.load(open(infile, 'r'))
                open(outfile, 'w').write(str(s))
                f[2] = os.path.getmtime(outfile)

        print 'SCSS v. %s watch mode' % VERSION
        print '================================'
        print 'Ctrl+C for exit\n'
        while True:
            try:
                for f in files:
                    parse(f)
                time.sleep(0.3)
            except OSError:
                pass
            except KeyboardInterrupt:
                print "\nSCSS stoped."
                break

        sys.exit()


    elif not args:
        infile = sys.stdin
        outfile = sys.stdout
        precache = False

    elif len(args) == 1:
        try:
            infile = open(args[0], 'r')
            outfile = sys.stdout
        except IOError, e:
            sys.stderr.write(str(e))
            sys.exit()

    elif len(args) == 2:
        try:
            infile = open(args[0], 'r')
            outfile = open(args[1], 'w')
        except IOError, e:
            sys.stderr.write(str(e))
            sys.exit()

    else:
        p.print_help(sys.stdout)
        sys.exit()

    try:
        s = parser.Stylecheet(
            options=dict(
                comments = opts.comments,
                compress = opts.compress,
                warn = opts.warn,
                sort = opts.sort,
                cache = precache,
            ))
        s.load( infile )
        outfile.write( str(s) )
    except ValueError, e:
        raise SystemExit(e)


if __name__ == '__main__':
    main()
