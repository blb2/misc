import argparse
import os
import shlex
import shutil
import subprocess
import sys
import xml.etree.ElementTree as etree

################################################################################

class SourceControl:
    def __init__(self, name, path, update=None, clean=None, url=None, available=None):
        self.name = name
        self.path = path
        self.update = update
        self.clean = clean
        self.url = url
        self.available = available if available is not None else bool(shutil.which(name))

class Project:
    def __init__(self, path, scm):
        self.path = path
        self.scm = scm

################################################################################

def remove_prefix(s, prefix):
    if s.startswith(prefix):
        return s[len(prefix):]
    return s

def run(path, cmd, stdout, oneline=False):
    if isinstance(cmd, list):
        args = cmd
        cmd = " ".join([ shlex.quote(s) for s in cmd ])
    else:
        args = shlex.split(cmd)
    try:
        ret = subprocess.run(args, cwd=path, stdout=stdout, universal_newlines=True)
        if ret.returncode != 0 or stdout != subprocess.PIPE or ret.stdout is None:
            return None
        return ret.stdout.split('\n', 1)[0] if oneline else ret.stdout
    except Exception as e:
        print("error running command: {}\n\t{}".format(cmd, e), file=sys.stderr)
        return None

def cmd_run(path, cmd):
    return run(path, cmd, None)

def cmd_get(path, cmd, oneline=False):
    return run(path, cmd, subprocess.PIPE, oneline)

def git_update(path):
    branch = cmd_get(path, "git symbolic-ref -q HEAD", True)
    if not branch:
        return
    branch = remove_prefix(branch, "refs/heads/")
    cmd_run(path, "git fetch --all --prune")
    cmd_run(path, "git merge --ff-only 'origin/{}'".format(branch))
    if os.path.exists(os.path.join(path, ".gitmodules")):
        cmd_run(path, "git submodule update --init --recursive")

def git_clean(path):
    cmd_run(path, "git clean -x -f -d")
    cmd_run(path, "git gc")

def svn_clean(path):
    # http://svn.apache.org/viewvc/subversion/trunk/subversion/svn/schema/status.rnc?view=markup
    svn = cmd_get(path, "svn status --depth empty --xml")
    if not svn:
        return
    root = etree.fromstring(svn)
    if not root or root.tag != "status":
        return
    if root.findall("./target/entry/wc-status/[@wc-locked='true']"):
        cmd_run(path, "svn cleanup --include-externals")

def svn_url(path):
    # http://svn.apache.org/viewvc/subversion/trunk/subversion/svn/schema/info.rnc?view=markup
    svn = cmd_get(path, "svn info --xml")
    if not svn:
        return None
    root = etree.fromstring(svn)
    if not root or root.tag != "info":
        return None
    info = root.findall("./entry/url")
    return info[0].text if info else None

def cvs_url(path):
    try:
        with open(os.path.join(path, "CVS/Root")) as f:
            return f.readline().split('\n', 1)[0]
    except Exception as e:
        return None

def get_scm_commands():
    scms = {
        "git" : SourceControl("git", ".git",
                              update=git_update,
                              clean=git_clean,
                              url="git config remote.origin.url"),
        "svn" : SourceControl("svn", ".svn",
                              update="svn update",
                              clean=svn_clean,
                              url=svn_url),
        "bzr" : SourceControl("bzr", ".bzr",
                              update="bzr update",
                              url="bzr config bound_location"),
        "hg"  : SourceControl("hg", ".hg",
                              update="hg pull -u",
                              url="hg showconfig paths.default"),
        "cvs" : SourceControl("cvs", "CVS/Root",
                              update="cvs update",
                              url=cvs_url),
    }
    return scms

def get_project_scm(path, scms):
    for scm in scms.values():
        if os.path.exists(os.path.join(path, scm.path)):
            return scm
    return None

def get_dirs(path, scms):
    repos = []
    projects = []
    for e in os.scandir(path):
        if e.is_dir():
            fullpath = os.path.join(path, e.name)
            if e.name.startswith("repos-"):
                repos.append(fullpath)
            else:
                scm = get_project_scm(fullpath, scms)
                if scm:
                    projects.append(Project(fullpath, scm))
    return repos, projects

def apply_cmd(path, scm, cmd):
    if not scm.available:
        return
    if callable(cmd):
        cmd(scm, path)
    else:
        method = getattr(scm, cmd)
        if callable(method):
            method(path)
        else:
            cmd_run(path, method)

def apply(path, scms, cmd, root=True):
    if root:
        scm = get_project_scm(path, scms)
        if scm:
            apply_cmd(path, scm, cmd)
            return
    repos, projects = get_dirs(path, scms) 
    for project in projects:
        apply_cmd(project.path, project.scm, cmd)
    for repo in repos:
        apply(repo, scms, cmd, False)

def apply_update(scm, path):
    print("{:<3} {} ...".format(scm.name, os.path.relpath(path)), flush=True)
    if not scm.update:
        return
    if callable(scm.update):
        scm.update(path)
    else:
        cmd_run(path, scm.update)

def apply_url(scm, path):
    if not scm.url:
        return
    url = scm.url(path) if callable(scm.url) else cmd_get(path, scm.url, True)
    if url:
        print("{:<3} {} {}".format(scm.name, os.path.relpath(path), url))

def update(args, scms):
    apply(os.getcwd(), scms, apply_update)

def clean(args, scms):
    apply(os.getcwd(), scms, "clean")

def urls(args, scms):
    apply(os.getcwd(), scms, apply_url)

def types(args, scms):
    for scm in scms.values():
        if args.all or scm.available:
            print(scm.name)

def get_action(argv):
    parser = argparse.ArgumentParser(prog="repos", add_help=True, allow_abbrev=False)
    subparser = parser.add_subparsers(title="available commands", dest="command", metavar="command")

    desc = "update repositories"
    parser_update = subparser.add_parser("update", help=desc, description=desc)
    parser_update.set_defaults(call=update)
    parser_update.add_argument("-t", "--type", dest="types", action="append", metavar="type", help="repository type")

    desc = "clean repositories"
    parser_clean = subparser.add_parser("clean", help=desc, description=desc)
    parser_clean.set_defaults(call=clean)
    parser_clean.add_argument("-t", "--type", dest="types", action="append", metavar="type", help="repository type")

    desc = "show URLs for each repository"
    parser_urls = subparser.add_parser("urls", help=desc, description=desc)
    parser_urls.set_defaults(call=urls)
    parser_urls.add_argument("-t", "--type", dest="types", action="append", metavar="type", help="repository type")

    desc = "show available source controls"
    parser_types = subparser.add_parser("types", help=desc, description=desc)
    parser_types.add_argument("-a", "--all", action='store_true', help="show all supported source controls")
    parser_types.set_defaults(call=types)

    desc = "show this help message and exit"
    parser_help = subparser.add_parser("help", help=desc, description=desc)
    parser_help.add_argument("topic", nargs='?')

    args = parser.parse_args(argv)
    if args.command and args.command != "help":
        return args

    parsers = {
        "update" : parser_update,
        "clean"  : parser_clean,
        "urls"   : parser_urls,
        "types"  : parser_types,
    }

    if hasattr(args, "topic") and args.topic and args.topic in parsers:
        parsers[args.topic].print_help()
    else:
        parser.print_help()

    return None

################################################################################

if __name__ == "__main__":
    action = get_action(sys.argv[1:])
    if action:
        scms = get_scm_commands()
        if hasattr(action, "types") and action.types:
            for name in action.types:
                if name not in scms.keys():
                    sys.exit("unknown type: {}".format(name))
            for scm in scms.values():
                if scm.name not in action.types:
                    scm.available = False
        action.call(action, scms)
