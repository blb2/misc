# misc
Just a collection of random code files or scripts.


### [case.pl][1]
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


### [clean-build-dryrun.bat][2] / [clean-build.bat][3]
For my projects that are not in some kind of source control yet, I needed some
way to uniformly clean out files that were temporary or from the build. The
`dryrun` version just prints out what the regular script would do without
actually doing it.


### [colorspaces.py][4]
Takes the ANSI escape codes, specified in RGB, and print them as UYVY compatible
values. The pixel values are converted froM RGB to YUV via BT.709 recommendation.


### [digitalocean-ddns.py][5]
A script to update a specific domain hosted on DigitalOcean to act as dynamic DNS.


### [env.pl][6]
Prints environment variables.


### [minecraft-backup.bat][7]
I play Minecraft! I made this to create backups of my worlds. This uses 7-Zip
for archival and compression. It'll create a directory on the current user's
desktop and place the backup files there.


### [range.rb][8] / [range.txt][9]
A friend of mine wanted a little utility that took in a text file that contained
page ranges and consolidated the overlapping ranges. This was so that he could
print the page ranges without printing pages multiple times. I made this little
script to help him out and also practice some Ruby.


### [rmdups.pl][10]
This is to find and remove duplicate files based on file size and MD5 hashes.


### [repos.py][11] / [repos.bat][12] / [repos.sh][13]
I love to collect source code repositories. This script just helps me out in
updating the checkouts/clones. `repos.bat` and `repos.sh` are just helper
scripts to launch `repos.py` on their respective platforms. On Windows,
`repos.bat` expects Git for Windows to be installed.


### [repos.sh][14]
I love to collect source code repositories. This script just helps me out in
updating the checkouts/clones.


### [sieve.py][15]
Just a sieve of Eratosthenes implementation in Python.


### [vs-verify-paths.py][16]
Analyze a Visual Studio project and help determine if referenced file paths
exist or not.


[1]: perl/case.pl
[2]: batch/clean-build-dryrun.bat
[3]: batch/clean-build.bat
[4]: python/colorspaces.py
[5]: python/digitalocean-ddns.py
[6]: perl/env.pl
[7]: batch/minecraft-backup.bat
[8]: ruby/range.rb
[9]: ruby/range.txt
[10]: perl/rmdups.pl
[11]: python/repos.py
[12]: python/repos.bat
[13]: python/repos.sh
[14]: sh/repos.sh
[15]: python/sieve.py
[16]: python/vs-verify-paths.py
