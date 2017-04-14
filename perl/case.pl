#!/usr/bin/perl

use strict;

exit if @ARGV == 0;

my @a = split(//, lc $ARGV[0]);
my @p = reverse map { 2**$_ } 0 .. $#a;

foreach my $i (0 .. 2**@a - 1) {
	my $j = 0;
	@a = map { ($i & $p[$j++]) ? uc : lc } @a;

	print "$i ", join("", @a), "\n";
}
