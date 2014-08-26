sortmuz
=======

Interactive command line utility to sort downloaded music albums.


installing
----------

Make sure you have Python 3 and
[setuptools](https://pypi.python.org/pypi/setuptools).

Clone using Git and run `setup.py`:

    git clone https://github.com/eepp/sortmuz.git
    cd sortmuz
    sudo python3 setup.py install


using
-----

The purpose of sortmuz is to take a music album directory, usually filled
with MP3/M4A/FLAC and some metadata files (album cover, log/cue files,
etc.), and sort it in another music collection directory following
this format:

    root of collection/
      <artist>/
        <release year> <album>/
          _/
            <meta files>
          <music files>

It interactively asks the user to confirm/modify the guessed artist
name, album name and album release year from audio files tags.

More info:

    sortmuz --help
