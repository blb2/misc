import argparse
import os
import shlex
import shutil
import subprocess
import sys
import xml.etree.ElementTree as etree


class SourceControl:
    def __init__(self, name, path, update=None, clean=None, gc=None, url=None, status=None, available=None):
        self.name = name
        self.path = path
        self.update = update
        self.clean = clean
        self.gc = gc
        self.url = url
        self.status = status
        self.available = available if available is not None else bool(shutil.which(name))


class Project:
    def __init__(self, path, scm):
        self.path = path
        self.scm = scm


def del_prefix(s, prefix):
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
        print(f"error running command: {cmd}\n\t{e}", file=sys.stderr)
        return None


def cmd_run(path, cmd):
    return run(path, cmd, None)


def cmd_get(path, cmd, oneline=False):
    return run(path, cmd, subprocess.PIPE, oneline)


def git_update(path):
    branch = cmd_get(path, "git symbolic-ref -q HEAD", True)
    if not branch:
        return
    branch = del_prefix(branch, "refs/heads/")
    cmd_run(path, f"git fetch --all --prune")
    cmd_run(path, f"git merge --ff-only 'origin/{branch}'")
    if os.path.exists(os.path.join(path, ".gitmodules")):
        cmd_run(path, "git submodule update --recursive")


def svn_clean(path):
    # http://svn.apache.org/viewvc/subversion/trunk/subversion/svn/schema/status.rnc?view=markup
    svn = cmd_get(path, "svn status --depth empty --xml")
    if svn:
        root = etree.fromstring(svn)
        if root and root.tag == "status":
            if root.findall("./target/entry/wc-status/[@wc-locked='true']"):
                cmd_run(path, "svn cleanup --include-externals")
    cmd_run(path, "svn cleanup --include-externals --remove-unversioned --remove-ignored")


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
    return {
        "git" : SourceControl("git", ".git",
                              update=git_update,
                              clean="git clean -xfd",
                              gc="git gc",
                              url="git config remote.origin.url",
                              status="git status"),
        "svn" : SourceControl("svn", ".svn",
                              update="svn update",
                              clean=svn_clean,
                              gc="svn cleanup --include-externals --vacuum-pristines",
                              url=svn_url,
                              status="svn status -q"),
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


def get_proj_scm(path, scms):
    for scm in scms.values():
        if os.path.exists(os.path.join(path, scm.path)):
            return scm
    return None


def get_dirs(path, scms):
    repos = []
    projs = []
    for e in os.scandir(path):
        if e.is_dir():
            fullpath = os.path.join(path, e.name)
            scm = get_proj_scm(fullpath, scms)
            if scm:
                projs.append(Project(fullpath, scm))
            else:
                repos.append(fullpath)

    return repos, projs


def apply_cmd(path, scm, cmd, show_proj):
    if not scm.available:
        return
    if callable(cmd):
        show_proj(path, scm)
        cmd(scm, path)
    else:
        method = getattr(scm, cmd)
        if method:
            show_proj(path, scm)
            if callable(method):
                method(path)
            else:
                cmd_run(path, method)


def show_proj_default(path, scm):
    print(f"{scm.name:<3} {os.path.relpath(path)} ...", flush=True)


def apply(path, scms, cmd, root=True, show_proj=show_proj_default):
    if root:
        scm = get_proj_scm(path, scms)
        if scm:
            apply_cmd(path, scm, cmd, show_proj)
            return
    repos, projs = get_dirs(path, scms) 
    for proj in projs:
        apply_cmd(proj.path, proj.scm, cmd, show_proj)
    for repo in repos:
        apply(repo, scms, cmd, False, show_proj)


def apply_url(scm, path):
    if not scm.url:
        return
    url = scm.url(path) if callable(scm.url) else cmd_get(path, scm.url, True)
    if url:
        print(f"{scm.name:<3} {os.path.relpath(path)} {url}", flush=True)


def update(args, scms):
    apply(os.getcwd(), scms, "update")


def status(args, scms):
    apply(os.getcwd(), scms, "status")


def clean(args, scms):
    apply(os.getcwd(), scms, "clean")


def gc(args, scms):
    apply(os.getcwd(), scms, "gc")


def urls(args, scms):
    apply(os.getcwd(), scms, apply_url, show_proj=lambda *args: None)


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

    desc = "retrieve status of each repository"
    parser_status = subparser.add_parser("status", help=desc, description=desc)
    parser_status.set_defaults(call=status)
    parser_status.add_argument("-t", "--type", dest="types", action="append", metavar="type", help="repository type")

    desc = "clean repositories"
    parser_clean = subparser.add_parser("clean", help=desc, description=desc)
    parser_clean.set_defaults(call=clean)
    parser_clean.add_argument("-t", "--type", dest="types", action="append", metavar="type", help="repository type")

    desc = "garbage collect repositories"
    parser_gc = subparser.add_parser("gc", help=desc, description=desc)
    parser_gc.set_defaults(call=gc)
    parser_gc.add_argument("-t", "--type", dest="types", action="append", metavar="type", help="repository type")

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
        "status" : parser_status,
        "clean"  : parser_clean,
        "gc"     : parser_gc,
        "urls"   : parser_urls,
        "types"  : parser_types,
    }

    if hasattr(args, "topic") and args.topic and args.topic in parsers:
        parsers[args.topic].print_help()
    else:
        parser.print_help()

    return None


if __name__ == "__main__":
    action = get_action(sys.argv[1:])
    if action:
        scms = get_scm_commands()
        if hasattr(action, "types") and action.types:
            for name in action.types:
                if name not in scms.keys():
                    sys.exit(f"unknown type: {name}")
            for scm in scms.values():
                if scm.name not in action.types:
                    scm.available = False
        action.call(action, scms)
