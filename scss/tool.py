"""Command-line tool to parse scss file.
"""
import sys

from scss import parser


def main():
    if len(sys.argv) == 1:
        infile = sys.stdin
        outfile = sys.stdout
    elif len(sys.argv) == 2:
        infile = open(sys.argv[1], 'rb')
        outfile = sys.stdout
    elif len(sys.argv) == 3:
        infile = open(sys.argv[1], 'rb')
        outfile = open(sys.argv[2], 'wb')
    else:
        raise SystemExit(sys.argv[0] + " [infile [outfile]]")
    try:
        result = parser.load(infile, precache=True)
    except ValueError, e:
        raise SystemExit(e)
    outfile.write(result)


if __name__ == '__main__':
    main()
