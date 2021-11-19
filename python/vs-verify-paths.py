import errno
import os
import sys
import urllib.parse
import xml.etree.ElementTree


xmlns = "{http://schemas.microsoft.com/developer/msbuild/2003}"
elements = { "ClInclude", "ProjectReference", "Page", "Compile", "Resource" }


def verify_path(dirname, relpath):
    if not relpath:
        return
    path = os.path.join(dirname, urllib.parse.unquote(relpath))
    if not os.path.exists(path):
        raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), path)


def verify_project(project):
    print(project)
    root = None
    try:
        tree = xml.etree.ElementTree.parse(project)
        root = tree.getroot()
        if not root:
            raise RuntimeError(f"[{project}] empty root")
        if root.tag != f"{xmlns}Project":
            raise RuntimeError(f"[{project}] unexpected root tag: {root.tag}")
    except Exception as e:
        print(e)
        return
    dirname = os.path.dirname(project)
    for group in root.findall(f"{xmlns}ItemGroup"):
        for element in elements:
            for ref in group.findall(f"{xmlns}{element}"):
                try:
                    verify_path(dirname, ref.get("Include"))
                except Exception as e:
                    print(e)


def verify_projects(projects):
    for project in projects:
        verify_project(project)


if __name__ == "__main__":
    verify_projects(sys.argv[1:])
