""" Command-line tool to parse scss file.
"""
import sys

import getopt
from scss import parser


def main():
    opts, args = getopt.getopt(sys.argv[1:], 'ti')
    opts = dict(opts)

    if '-i' in opts or '--interactive' in opts:
        p = parser.Stylecheet()
        print 'SCSS interactive mode.'
        print 'Ctrl+D or quit for exit'
        while True:
            try:
                s = raw_input('>>> ').strip()
                if s == 'quit':
                    raise EOFError
                print p.parse(s)
            except EOFError:
                break

        sys.exit()

    elif not args:
        infile = sys.stdin
        outfile = sys.stdout

    elif len(args) == 1:
        infile = open(args[0], 'rb')
        outfile = sys.stdout

    elif len(args) == 3:
        infile = open(args[0], 'rb')
        outfile = open(args[1], 'wb')

    else:
        raise SystemExit("scss [-i, --interactive] [infile [outfile]]")

    try:
        result = parser.load(infile, precache=True)
    except ValueError, e:
        raise SystemExit(e)

    outfile.write(result)


if __name__ == '__main__':
    main()
