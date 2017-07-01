#!/usr/bin/perl

use strict;
use Digest::MD5;

sub compute_hash {
	my $file = shift;
	my ($md5, $hash);

	open FILE, "< $file";
	binmode FILE;

	$md5 = Digest::MD5->new;
	$md5->addfile(*FILE);
	$hash = $md5->hexdigest;

	close FILE;
	return $hash;
}

sub add_file_hash {
	my ($hashes, $dups, $file) = @_;
	my $hash = compute_hash($file);

	if (defined $hashes->{$hash}) {
		push @{$hashes->{$hash}}, $file;
		$dups->{$hash} = $hashes->{$hash};
	} else {
		$hashes->{$hash} = [$file];
	}
}

sub find_dups {
	my ($dir, $subdirs, $dups) = @_;
	my %sizes  = ();
	my %hashes = ();

	if (opendir DIR, $dir) {
		while (my $file = readdir DIR) {
			next if $file =~ /^\./;

			$file = "$dir/$file";

			if (-d $file) {
				push @$subdirs, $file;
			} else {
				my $size = -s $file;

				if (defined $sizes{$size}) {
					my $files = $sizes{$size};

					add_file_hash \%hashes, $dups, $files->[0] if @$files == 1;
					add_file_hash \%hashes, $dups, $file;

					push @$files, $file;
				} else {
					$sizes{$size} = [$file];
				}
			}
		}

		closedir DIR;
	}
}

sub rm_dups {
	my %dups = %{$_[0]};
	my $eof  = 0;
	my @unlinked = ();

	foreach my $hash (keys %dups) {
		my @files = @{$dups{$hash}};

		for my $i (1 .. @files) {
			print $i, " ", $files[$i - 1], "\n";
		}

		print "which to keep? [0 = skip] ";
		if (eof STDIN) {
			print "\n";
			$eof = 1;
			last;
		}

		my $c = <STDIN>;
		chomp $c;

		if (0 < $c && $c <= @files) {
			splice @files, $c - 1, 1;
			push @unlinked, @files;
		}
	}

	if (!$eof && @unlinked > 0) {
		print "removing files:\n";
		print "  $_\n" foreach @unlinked;

		unlink @unlinked;
	}

	return !$eof;
}

my $recursive = 0; # TODO: Add support for recursively checking directories
my @dirs = (".");  # TODO: Read directory list passed via ARGV

while (@dirs > 0) {
	my $dir = shift @dirs;
	my (%dups, @subdirs);

	print "searching directory: $dir\n";

	find_dups $dir, \@subdirs, \%dups;

	last if !rm_dups \%dups;

	push @dirs, @subdirs if $recursive;
}
