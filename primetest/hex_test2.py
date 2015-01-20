#!/usr/bin/python

hex, solutions, y = [], [], 1
for j in range(3000):
    y += 6*j
    hex.append(y)

for k in range(1,1000):
    n = 6*k+1
    for m in range(3000):
        if not hex[m]%n:
            solutions.append(n)
            #print "Found n=%d, m=%d, hex[m]=%d" % (6*k+1,m,hex[m])
            break

print "solutions exist for n=6k+1:"
print solutions

badsol = []
for k in range(1,1000):
    n = 6*k-1
    for m in range(3000):
        if not hex[m]%n:
            badsol.append(n)
            #print "Found n=%d, m=%d, hex[m]=%d" % (6*k+1,m,hex[m])
            break

print "solutions with n=6k-1:"
print badsol
