#!/usr/bin/env python
# http://en.wikipedia.org/wiki/Neutral_density_filter

import sys

def pct(val):
	return val * 100.0

def transmittance(density):
	if density < 0.0:
		return

	trans = 10.0 ** -density
	delta = 1.0 - trans
	fstop = density / 0.3

	print '--> ' + str(density)
	print 'transmittance=%.4f%% f-stop=%.1f' % (pct(trans), fstop)
	print 'light reduced by %.4f%% (%.1f times)' % (pct(delta), 1.0 / trans)

for arg in sys.argv[1:]:
	transmittance(float(arg))
