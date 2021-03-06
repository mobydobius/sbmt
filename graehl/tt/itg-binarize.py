#!/usr/bin/env pypy
usage="""
no args: lines from stdin are permutations (0 for first element)
1 arg = n : all permutations of length n are used as inputs.
>1 arg : indices for a single permutation are taken from arguments

returns an ITG binarization for the permutation if there is one. (0 1) => 0 1 and <0 1> => 1 0
"""

import sys,os
from tree import *
stdout=os.getenv('showall',False)
pretty=os.getenv('pretty',True)
showperm=os.getenv('showperm',pretty)

from dumpx import *

n_perm=0
n_perm_itg_bin=0
def print_itg_bin(perm,out=sys.stdout):
    if out is not None and showperm:
        out.write(' '.join(map(str,perm))+' = ')
    d=itg_bin(perm)
    global n_perm,n_perm_itg_bin
    n_perm+=1
    if d is not None:
        n_perm_itg_bin+=1
        if out is not None:
            out.write('%s'%d[2])
    if out is not None:
        out.write('\n')

def print_stats(out=sys.stderr):
    out.write('%s out of %s permutations (%s) were ITG-binarizable.\n'%(n_perm_itg_bin,n_perm,float(n_perm_itg_bin)/n_perm))

mon='[]'
inv='<>'

def itg_bin(perm):
    """
    *** input: perm=[0,1,4,2,3] a permutation of [0,1,...,max] - think of this
as a funny word:word alignment if you like (every word is 1:1 aligned)

    *** output: returns None if the original and permuted sequence
[0,1,....,max] can't be synchronously generated by a 1-state ITG (with at most
2 symbols and 1 NT on the source and target rhs) grammar.

     otherwise, return Tree with labels '[]' or '<>' except leaves
    """
    p=[int(x) for x in perm]
#    dump('itg_bin(%s)'%p)
    n=len(p)
    if n==1:
        return Tree(p[0])
    if (n==0 or min(p)!=0 or max(p)!=n-1):
        raise Exception("expected args, or lines to stdin, of at least 1 space-separated indices (permutations of >=1 elements notated e.g. 0 2 1 of the ints 0...max) - you supplied %s min=%s max=%s"%(perm,min(p),max(p)))
    return itg_bin_greedy(p)

def connect(a,b):
    if a[1]==b[0]:
        return (a[0],b[1],Node(mon,[a[2],b[2]]))
    elif a[0]==b[1]:
        return (b[0],a[1],Node(inv,[a[2],b[2]]))
    return None

def itg_bin_greedy(p):
    assert(len(p)>1)
    i=0
    s=[]
    for i in range(0,len(p)):
        x=p[i]
        s.append((x,x+1,Node(x)))
        while(len(s)>1):
            c=connect(s[-2],s[-1])
            if c is None:
                break
            s.pop()
            s.pop()
            s.append(c)
    if len(s)==1:
        return s[0]
    dump("can't ITG binarize %s"%' '.join(str(x[2]) for x in s))
    return None


# pypy doesn't support itertools.permutations
def permute_in_place(a):
    'a is a list. yield all shuffled versions of it, starting w/ sorted'
    a.sort()
    yield list(a)
    if len(a) <= 1:
        return
    first = 0
    last = len(a)
    while 1:
        i = last - 1
        while 1:
            i = i - 1
            if a[i] < a[i+1]:
                j = last - 1
                while not (a[i] < a[j]):
                    j = j - 1
                a[i], a[j] = a[j], a[i] # swap
                r = a[i+1:last]
                r.reverse()
                a[i+1:last] = r
                yield list(a)
                break
            if i == first:
                a.reverse()
                return

def main(argv):
    if len(argv)==1:
        for p in permute_in_place(range(0,int(argv[0]))):
            print_itg_bin(p,sys.stdout if stdout else None)
    elif len(argv):
        print_itg_bin(argv)
    else:
        for line in sys.stdin:
            print_itg_bin(line.split())
    print_stats()

if __name__ == "__main__":
    main(sys.argv[1:])


