#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Python script to convert tags within the filename to extended attributes.
Copyright 2018 by Reiner Rottmann <reiner@rottmann.it>
Released under the BSD License.
'''
import os
import re
import sys
import click
import logging
import platform
import subprocess

logging.basicConfig(level=logging.DEBUG, format='#%(levelname)s: %(message)s')

@click.command()
@click.option('--path', required=True, help='Path to the file to convert tags')
def tag2xattr(path):
    regex = '(?P<name>^.*)\[(?P<tags>[^\[]+)\](?P<ext>.*$)'
    result = ''
    fname = os.path.basename(path)
    m = re.search(regex, fname)
    tags = m.group('tags').split()
    if platform.system() == 'Darwin':
        ret = subprocess.getstatusoutput('which xattr')
        if not ret[0] == 0:
            logging.error('Command not found: xattr')
            sys.exit(1)
        plist_header = '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"><plist version="1.0"><array>'
        plist_footer = '</array></plist>'
        plist_tags = ''
        for tag in tags:
            plist_tags = plist_tags + '<string>{}</string>'.format(tag.replace("'", "-"))
        plist = plist_header + plist_tags + plist_footer
        tag_metadata = 'com.apple.metadata:'
        xattr_keys = ['kMDItemFinderComment', '_kMDItemUserTags', 'kMDItemOMUserTags']
        for xattr_key in xattr_keys:
            cmd = 'xattr -w {0} \'{1}\' "{2}"'.format(tag_metadata + xattr_key, plist, path)
            stdout = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
            result += str(stdout)
            sys.exit(1)
        return result
    if platform.system() == 'Linux':
        ret = subprocess.getstatusoutput('which setfattr')
        if not ret[0] == 0:
            logging.error('Command not found: setfattr')
        cmd = 'setfattr -n \'user.tags\' -v \'{0}\' "{1}"'.format(','.join(tags), path)
        stdout = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
        result += str(stdout)
        return result
    logging.error('Platform is not supported!')
    sys.exit(1)

if __name__ == '__main__':
    tag2xattr()