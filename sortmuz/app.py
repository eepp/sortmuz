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
        print('Error: source is not an existing directory',
              file=sys.stderr)
        sys.exit(1)

    # validate output directory
    if not os.path.isdir(args.output):
        print('Error: output is not an existing directory',
              file=sys.stderr)
        sys.exit(1)

    return args


def _print_summary(src, output, muz_files, meta_files):
    print('source: {}'.format(os.path.abspath(src)))
    print('output: {}'.format(os.path.abspath(output)))
    print('')

    if not muz_files:
        print('no music files')
    else:
        print('music files:')

        for file in muz_files:
            print('  {}'.format(os.path.basename(file)))

    print('')

    if not meta_files:
        print('no meta files')
    else:
        print('meta files:')

        for file in meta_files:
            print('  {}'.format(os.path.basename(file)))


def _collect_files(src):
    exts = ['.mp3', '.mp4', '.flac']
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


def do_sortmuz(src, output):
    muz_files, meta_files = _collect_files(src)

    _print_summary(src, output, muz_files, meta_files)
    print('\n---\n')

    artist, album, year = _guess_infos(muz_files)

    while True:
        user_artist = input('artist? [{}] '.format(artist))
        user_album = input('album? [{}] '.format(album))
        user_year = input('year? [{}] '.format(year))
        user_confirm = input('confirm? [y] ')

        if len(user_confirm) == 0 or user_confirm.lower() == 'y':
            break

        print('')

    user_artist = user_artist.strip()
    user_album = user_album.strip()
    user_year = user_year.strip()

    if len(user_artist.strip()) == 0:
        user_artist = artist

    if len(user_album.strip()) == 0:
        user_album = album

    if len(user_year.strip()) == 0:
        user_year = year

    if len(user_artist) == 0:
        print('Error: invalid artist name', file=sys.stderr)
        sys.exit(1)

    if len(user_album) == 0:
        print('Error: invalid album name', file=sys.stderr)
        sys.exit(1)

    if len(user_year) == 0:
        print('Error: invalid year', file=sys.stderr)
        sys.exit(1)

    year_album = '{} {}'.format(user_year, user_album)
    album_dir = os.path.join(output, user_artist, year_album)
    abs_album_dir = os.path.abspath(album_dir)

    if os.path.isdir(album_dir):
        res = input('overwrite "{}"? [y] '.format(abs_album_dir))

        if len(res) != 0 and res.lower() != 'y':
            sys.exit(0)

        print('')

        print('[rm]    "{}"'.format(abs_album_dir))
        shutil.rmtree(album_dir)
    else:
        print('')

    print('[mkdir] "{}"'.format(abs_album_dir))
    os.makedirs(album_dir)

    for file in muz_files:
        dst = os.path.join(abs_album_dir, os.path.basename(file))
        msg = '[cp]    "{}" -> "{}"'.format(file, dst)

        print(msg)
        shutil.copyfile(file, dst)

    if meta_files:
        meta_dir = os.path.join(abs_album_dir, '_')
        print('[mkdir] "{}"'.format(meta_dir))
        os.makedirs(meta_dir)

        for file in meta_files:
            dst = os.path.join(meta_dir, os.path.basename(file))
            msg = '[cp]    "{}" -> "{}"'.format(file, dst)

            print(msg)

            if os.path.isdir(file):
                shutil.copytree(file, dst)
            else:
                shutil.copyfile(file, dst)


def run():
    args = _parse_args()

    try:
        do_sortmuz(args.src, args.output)
    except KeyboardInterrupt:
        sys.exit(1)
