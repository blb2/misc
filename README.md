# misc
Just a collection of random code files or scripts.

### [case.pl](perl/case.pl)
Testing out enumerating different character case combinations in Perl.

	gaia:~$ perl case.pl abc
	0 abc
	1 abC
	2 aBc
	3 aBC
	4 Abc
	5 AbC
	6 ABc
	7 ABC

### [clean-build-dryrun.bat](batch/clean-build-dryrun.bat) / [clean-build.bat](batch/clean-build.bat)
For my projects that are not in some kind of source control yet, I needed some
way to uniformly clean out files that were temporary or from the build.  The
`dryrun` version just prints out what the regular script would do without
actually doing it.

### [minecraft-backup.bat](batch/minecraft-backup.bat)
I play Minecraft!  I made this to create backups of my worlds.  This uses 7-Zip
for archival and compression.  It'll create a directory on the current user's
desktop and place the backup files there.

### [range.rb](ruby/range.rb) / [range.txt](ruby/range.txt)
A friend of mine wanted a little utility that took in a text file that contained
page ranges and consolidated the overlapping ranges.  This was so that he could
print the page ranges without printing pages multiple times.  I made this little
script to help him out and also practice some Ruby.

### [remove-dups.pl](perl/remove-dups.pl)
This is to find and remove duplicate files based on file size and MD5 hashes.

### [repos](sh/repos)
I love to collect source code repositories.  This script just helps me out in
updating the checkouts/clones.

### [sieve.py](python/sieve.py)
Just a sieve of Eratosthenes implementation in Python.
