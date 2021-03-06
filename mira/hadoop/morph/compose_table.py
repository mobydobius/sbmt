#!/usr/bin/env python

import sys, itertools

def input():
    for line in sys.stdin:
        fields = line.rstrip().split("\t")
        if len(fields) != 4:
            sys.stderr.write("warning: couldn't read line %s\n" % line.rstrip())
            continue
        z, x, pxy, pyz = fields
        pxy = float(pxy)
        pyz = float(pyz)
        yield z, x, pxy, pyz

for (z, x), records in itertools.groupby(input(), lambda (z, x, pxy, pyz): (z, x)):
    pxz = 0.
    for _, _, pxy, pyz in records:
        pxz += pxy * pyz
    print "%s\t%s\t%s" % (z, x, pxz)
