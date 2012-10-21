#!/usr/bin/env python


import platform
import os
import re
import shutil
import sys


WINDOWS = (platform.system() == 'Windows')
WINDOWS_PATH_PREFIX = '\\\\?\\'


def fix_windows_path(path):
    if not WINDOWS or len(path) < 260 or path.startswith(WINDOWS_PATH_PREFIX):
        return path
    return WINDOWS_PATH_PREFIX + path


def get_paths(filename):
    try:
        with open(filename, 'r') as f:
            lines = [line.rstrip('\r\n') for line in f if not line.isspace()]
            paths = [path for path in lines if os.path.exists(path)]
            for path in set(lines) - set(paths):
                print >> sys.stderr, '%s: path does not exist' % path
            return paths
    except IOError as e:
        print >> sys.stderr, '%s: %s' % (filename, e.strerror)
        return []


def parse_namespace(path):
    try:
        with open(path, 'r') as f:
            for line in f:
                match = re.match('^namespace\s+([\w\.]+)\s*{*', line)
                if match:
                    return match.group(1)
    except IOError as e:
        print >> sys.stderr, '%s: %s' % (path, e.strerror)
    return None


def get_unique_path(path):
    root, ext = os.path.splitext(path)
    i = 1
    while True:
        unique_path = '%s.%i%s' % (root, i, ext)
        if not os.path.exists(unique_path):
            return unique_path
        i += 1


def get_generated_path(path):
    root, ext = os.path.splitext(path)
    return '%s.g%s' % (root, ext)


def copy_file(src_path, dst_path):
    try:
        dst_dir = os.path.dirname(dst_path)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        elif os.path.exists(dst_path):
            print >> sys.stderr, '%s: duplicate filename detected' % os.path.relpath(dst_path, '.')
            dst_path = get_unique_path(dst_path)
        print os.path.relpath(dst_path, '.')
        shutil.copy(src_path, dst_path)
    except (OSError, IOError) as e:
        print >> sys.stderr, '%s: %s' % (dst_dir, e.strerror)


def copy_files(paths, dst_root_dir):
    dst_root_dir = os.path.abspath(dst_root_dir)
    for path in paths:
        gen_level = -1
        path = os.path.abspath(path)
        for curr_root, dirs, files in os.walk(path):
            curr_dir = os.path.relpath(curr_root, path)
            curr_level = len(curr_dir.split(os.path.sep))
            if gen_level >= 0 and curr_level <= gen_level:
                gen_level = -1
            elif curr_root.endswith('Generated'):
                gen_level = curr_level
            if not files:
                continue
            for f in files:
                src_path = fix_windows_path(os.path.join(curr_root, f))
                namespace = parse_namespace(src_path)
                if not namespace:
                    print >> sys.stderr, '%s: namespace not found' % src_path
                    continue
                sub_path = os.path.join(namespace.replace('.', os.path.sep), f)
                dst_path = fix_windows_path(os.path.join(dst_root_dir, sub_path))
                if gen_level >= 0:
                    dst_path = get_generated_path(dst_path)
                copy_file(src_path, dst_path)


def process_files(files):
    for filename in files:
        paths = get_paths(filename)
        if paths:
            dst_root_dir = os.path.splitext(os.path.basename(filename))[0]
            if os.path.exists(dst_root_dir):
                ret = raw_input('Destination directory exists: ' + dst_root_dir + '\nContinue? (y/n): ')
                if ret != 'y':
                    continue
            copy_files(paths, dst_root_dir)
        else:
            print >> sys.stderr, filename, 'does not contain any valid paths'


if __name__ == "__main__":
    process_files(sys.argv[1:])


# vim: set et ts=4 sw=4:
