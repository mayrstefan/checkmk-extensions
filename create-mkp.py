#!/usr/bin/env python3

import datetime
import io
import json
import sys
import tarfile

def usage():
    print('./create-mkp.py source-directory')

def get_tarinfo(name, obj):
    info = tarfile.TarInfo(name)
    info.size = obj.getbuffer().nbytes
    info.mtime = datetime.datetime.now().timestamp()
    info.uid = 0
    info.gid = 0
    info.mode = 0o644
    return info

def create_mkp(directory):
    info = {}
    info_filename = '%s/info' % directory
    with open(info_filename, 'r') as info_file:
        info = eval(info_file.read())

    mkp_filename = '%s-%s.mkp' % (info['name'], info['version'])
    with tarfile.open(mkp_filename, 'w:gz') as tar:
        print('Package directory %s to %s' % (directory, mkp_filename))
        print('Add file info')
        tar.add(info_filename, 'info')
        print('Add file info.json')
        info_fileobj = io.BytesIO()
        info_fileobj.write(json.dumps(info).encode())
        info_fileobj.seek(0)
        tar.addfile(get_tarinfo('info.json', info_fileobj), info_fileobj)
        for folder in info['files']:
            folder_tarname = '%s.tar' % folder
            print('Add folder %s as %s' % (folder, folder_tarname))
            folder_fileobj = io.BytesIO()
            with tarfile.open(folder_tarname, 'w:', fileobj = folder_fileobj) as folder_tar:
                folder_tar.add('%s/%s' % (directory, folder), '')
                folder_fileobj.seek(0)
                tar.addfile(get_tarinfo(folder_tarname, folder_fileobj), folder_fileobj)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()
        sys.exit(1)

    create_mkp(sys.argv[1])
