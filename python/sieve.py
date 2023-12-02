from math import sqrt

n = 49
sieve = [True] * n

print ">>", int(sqrt(n))

for i in xrange(2, int(sqrt(n))):
    if sieve[i]:
        for j in xrange(i * 2, n, i):
            sieve[j] = False

for i, v in enumerate(sieve):
    if i > 1 and v:
        print i
