#!/usr/bin/python
import itertools
flatten = lambda lst: list(itertools.chain.from_iterable(lst))

def primeFactors(n):
    primfac = []
    d = 2
    while d*d <= n:
        while (n % d) == 0:
            primfac.append(d)
            n /= d
        d += 1
    if n > 1:
       primfac.append(n)
    return primfac

NN = 3000

tri, hex, x, y = [], [], 0, 1
for j in range(NN):
    x += j
    y += 6*j
    tri.append(x)
    hex.append(y)

PR_file = open('1st_primes.txt')
strnums = PR_file.read().split()
allprimes = map(int, strnums)

hexprimes = list(set(flatten(map( primeFactors, hex ))))
hexprimes.sort()

check = [(hexprimes[j]-1)%6 for j in range(len(hexprimes))]
print "Any primes not of the form 6q+1 :", list(set(check))

for pr in hexprimes:
    if (pr+1)%6:    # p = 6q+1
        q = (pr-1)/6
        ll = [(tri[m]-q)%pr for m in range(min(3*q,len(tri)))]
        if len([i for i,ee in enumerate(ll) if not ee]) != 1:
            print 'Non-unique solution!  q =', q
    else:           # p = 6q-1
        q = (pr+1)/6
        ll = [(tri[m]+q)%pr for m in range(len(tri))]
        if len([i for i,ee in enumerate(ll) if not ee]) > 0:
            print 'Solution where there shouldn\'t be!  q =', q

print "All tests completed"
