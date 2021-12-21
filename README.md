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

### [colorspaces.py](python/colorspaces.py)
Takes the ANSI escape codes, specified in RGB, and print them as
UYVY-compatible values.  The pixel values are converted froM RGB to YUV via
BT.709 recommendation.

### [digitalocean-ddns.py](python/digitalocean-ddns.py)
A script to update a specific domain hosted on DigitalOcean to act as dynamic
DNS.

### [env.pl](perl/env.pl)
Prints environment variables.

### [minecraft-backup.bat](batch/minecraft-backup.bat)
I play Minecraft!  I made this to create backups of my worlds.  This uses 7-Zip
for archival and compression.  It'll create a directory on the current user's
desktop and place the backup files there.

### [range.rb](ruby/range.rb) / [range.txt](ruby/range.txt)
A friend of mine wanted a little utility that took in a text file that
contained page ranges and consolidated the overlapping ranges.  This was so
that he could print the page ranges without printing pages multiple times.  I
made this little script to help him out and also practice some Ruby.

### [rmdups.pl](perl/rmdups.pl)
This is to find and remove duplicate files based on file size and MD5 hashes.

### [repos.py](python/repos.py) / [repos.bat](python/repos.bat) / [repos.sh](python/repos.sh)
I love to collect source code repositories.  This script just helps me out in
updating the checkouts/clones.  `repos.bat` and `repos.sh` are just helper
scripts to launch `repos.py` on their respective platforms.  On Windows,
`repos.bat` expects Git for Windows to be installed.


### [repos.sh](sh/repos.sh)
I love to collect source code repositories.  This script just helps me out in
updating the checkouts/clones.

### [sieve.py](python/sieve.py)
Just a sieve of Eratosthenes implementation in Python.

### [vs-verify-paths.py](python/vs-verify-paths.py)
Analyze a Visual Studio project and help determine if referenced file paths
exist or not.
