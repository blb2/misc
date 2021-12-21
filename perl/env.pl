#!/usr/bin/perl

use strict;

print "Content-Type: text/plain\r\n\r\n";

foreach my $key (keys %ENV) {
	print "$key=$ENV{$key}\n";
}
