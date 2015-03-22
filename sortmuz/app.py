# The MIT License (MIT)
#
# Copyright (c) 2014 Philippe Proulx <eepp.ca>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import mutagenx
import argparse
import readline
import sys
import os
import shutil
import sortmuz
from termcolor import colored


def _perror(msg, exit=True):
    print(colored('Error: {}'.format(msg), 'red', attrs=['bold']),
          file=sys.stderr)

    if exit:
        sys.exit(1)


def _pwarning(msg):
    print(colored('Warning: {}'.format(msg), 'yellow', attrs=['bold']),
          file=sys.stderr)


def _pinfo(msg):
    print(colored('{}'.format(msg), 'blue'), file=sys.stderr)


def _parse_args():
    ap = argparse.ArgumentParser()

    ap.add_argument('-V', '--version', action='version',
                    version='%(prog)s v{}'.format(sortmuz.__version__))
    ap.add_argument('-o', '--output', action='store', type=str,
                    default=os.getcwd(), metavar='DIR',
                    help='Output music collection directory (default: CWD)')
    ap.add_argument('src', metavar='SRC', action='store', type=str,
                    help='Path to source directory')

    # parse args
    args = ap.parse_args()

    # validate source directory
    if not os.path.isdir(args.src):
        _perror('source "{}" is not an existing directory'.format(args.src))

    # validate output directory
    if not os.path.isdir(args.output):
        _perror('output "{}" is not an existing directory'.format(args.output))
        sys.exit(1)

    return args


def _print_summary(src, output, muz_files, meta_files):
    print('{} {}'.format(colored('source:', 'blue'),
                         colored(os.path.abspath(src), 'blue', attrs=['bold'])))
    print('{} {}'.format(colored('output:', 'blue'),
                         colored(os.path.abspath(output),
                                 'blue', attrs=['bold'])))

    if not muz_files:
        _pwarning('no music files found')
    else:
        print()
        _pinfo('music files:')

        for file in muz_files:
            print('  {}'.format(os.path.basename(file)))

    print()

    if not meta_files:
        _pinfo('no meta files')
    else:
        _pinfo('meta files:')

        for file in meta_files:
            print('  {}'.format(os.path.basename(file)))


def _collect_files(src):
    exts = ['.mp3', '.m4a', '.flac']
    exclude_meta = ['.ds_store', 'desktop.ini', 'thumbs.db']

    muz_files = []
    meta_files = []

    for file in os.listdir(src):
        name, ext = os.path.splitext(file)
        ext = ext.lower()

        if ext in exts:
            muz_files.append(os.path.abspath(os.path.join(src, file)))
        else:
            if file.lower() in exclude_meta:
                continue

            meta_files.append(os.path.abspath(os.path.join(src, file)))

    return sorted(muz_files), sorted(meta_files)


def _get_file_infos(file):
    try:
        m_file = mutagenx.File(file)
    except:
        return '', '', ''

    artist = ''
    album = ''
    year = ''

    if type(m_file) is mutagenx.mp3.MP3:
        if 'TPE1' in m_file:
            artist = m_file['TPE1'].text[0]
        elif 'TPE2' in m_file:
            artist = m_file['TPE2'].text[0]

        if 'TALB' in m_file:
            album = m_file['TALB'].text[0]

        year_tags = [
            'TDRC',
            'TYER',
            'TDAT',
            'TIME',
            'TRDA',
        ]

        for tag in year_tags:
            if tag in m_file:
                year = str(m_file[tag].text[0])
                break
    elif type(m_file) is mutagenx.mp4.MP4:
        if b'\xa9ART' in m_file:
            artist = m_file[b'\xa9ART'][0]
        elif b'aART' in m_file:
            artist = m_file[b'aART'][0]

        if b'\xa9alb' in m_file:
            album = m_file[b'\xa9alb'][0]

        if b'\xa9day' in m_file:
            year = str(m_file[b'\xa9day'][0])

    return artist, album, year


def _guess_infos(muz_files):
    if not muz_files:
        return '', '', ''

    artist, album, year = _get_file_infos(muz_files[0])

    if len(muz_files) > 1:
        artist2, album2, year2 = _get_file_infos(muz_files[1])

        if artist != artist2:
            artist = 'Various Artists'

    return artist, album, year


def _pcp(src, dst):
    msg = '[{}]    "{}" {} "{}"'.format(colored('cp', attrs=['bold']), src,
                                        colored('->', attrs=['bold']), dst)
    print(msg)


def _pmkdir(dst):
    print('[{}] "{}"'.format(colored('mkdir', attrs=['bold']), dst))


def do_sortmuz(src, output):
    muz_files, meta_files = _collect_files(src)

    _print_summary(src, output, muz_files, meta_files)
    print(colored('\n---\n', 'blue'))

    artist, album, year = _guess_infos(muz_files)

    while True:
        uartist = input('{}  [{}] '.format(colored('artist?', 'green',
                                                   attrs=['bold']),
                                           colored(artist, attrs=['bold'])))
        ualbum = input('{}   [{}] '.format(colored('album?', 'green',
                                                  attrs=['bold']),
                                           colored(album, attrs=['bold'])))
        uyear = input('{}    [{}] '.format(colored('year?', 'green',
                                                 attrs=['bold']),
                                           colored(year, attrs=['bold'])))
        uconfirm = input('{} [{}] '.format(colored('confirm?', 'cyan',
                                                    attrs=['bold']),
                                           colored('y', attrs=['bold'])))

        if len(uconfirm) == 0 or uconfirm.lower() == 'y':
            break

        print()

    uartist = uartist.strip()
    ualbum = ualbum.strip()
    uyear = uyear.strip()

    if len(uartist.strip()) == 0:
        uartist = artist

    if len(ualbum.strip()) == 0:
        ualbum = album

    if len(uyear.strip()) == 0:
        uyear = year

    if len(uartist) == 0:
        _perror('empty artist name')

    if len(ualbum) == 0:
        _perror('empty album name')

    if len(uyear) == 0:
        _perror('empty year')

    year_album = '{} {}'.format(uyear, ualbum)
    album_dir = os.path.join(output, uartist, year_album)
    abs_album_dir = os.path.abspath(album_dir)

    if os.path.isdir(album_dir):
        res = input('{} {} [{}] '.format(colored('overwrite', 'cyan',
                                                 attrs=['bold']),
                                         colored(abs_album_dir, 'blue',
                                                 attrs=['bold']),
                                         colored('n', attrs=['bold'])))

        if res.lower() != 'y':
            sys.exit(0)

        print()
        print('[{}]    "{}"'.format(colored('rm', attrs=['bold']),
                                    abs_album_dir))

        try:
            shutil.rmtree(album_dir)
        except Exception as e:
            _perror('cannot remove directory "{}": {}'.format(album_dir, e))
    else:
        print()

    _pmkdir(abs_album_dir)

    try:
        os.makedirs(album_dir)
    except Exception as e:
        _perror('cannot create directory "{}": {}'.format(album_dir, e))

    for file in muz_files:
        dst = os.path.join(abs_album_dir, os.path.basename(file))
        _pcp(file, dst)

        try:
            shutil.copyfile(file, dst)
        except Exception as e:
            _perror('cannot cannot copy file "{}": {}'.format(file, e))

    if meta_files:
        meta_dir = os.path.join(abs_album_dir, '_')
        _pmkdir(meta_dir)

        try:
            os.makedirs(meta_dir)
        except Exception as e:
            _perror('cannot create directory "{}": {}'.format(meta_dir, e))

        for file in meta_files:
            dst = os.path.join(meta_dir, os.path.basename(file))
            _pcp(file, dst)

            try:
                if os.path.isdir(file):
                    shutil.copytree(file, dst)
                else:
                    shutil.copyfile(file, dst)
            except Exception as e:
                fmt = 'cannot cannot copy file/directory "{}": {}'
                _perror(fmt.format(file, e))


def run():
    args = _parse_args()

    try:
        do_sortmuz(args.src, args.output)
    except KeyboardInterrupt:
        sys.exit(1)
