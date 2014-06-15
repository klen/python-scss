import operator
import sys

PY3 = sys.version_info[0] == 3


def with_metaclass(base, meta):
    return meta('%sWithMeta' % base.__name__, (base,), {})

if PY3:
    div = operator.__truediv__
else:
    div = operator.__div__

if PY3:
    unicode_ = str
    bytes_ = bytes
else:
    unicode_ = unicode
    bytes_ = str

if PY3:
    import io
    file_ = io.IOBase
else:
    file_ = file

if PY3:
    import pickle
else:
    import cPickle as pickle

# pylama:ignore=W0611,D
