#!/usr/bin/env ruby
# http://en.wikipedia.org/wiki/Neutral_density_filter

class Float
	def to_pct
		return self * 100.0
	end
end

def transmittance(density)
	return if density < 0.0

	trans = 10.0 ** -density
	delta = 1.0 - trans
	fstop = density / 0.3

	puts "--> #{density}"
	puts "transmittance=%.4f%% f-stop=%.1f" % [ trans.to_pct, fstop ]
	puts "light reduced by %.4f%% (%.1f times)" % [ delta.to_pct, 1.0/trans ]
end

ARGV.each do |arg|
	transmittance arg.to_f
end
