sortmuz
=======

Interactive command line utility to sort downloaded music albums.


installing
----------

Make sure you have Python 3 and
[setuptools](https://pypi.python.org/pypi/setuptools).

Install using pip (`python3-pip` Ubuntu package):

    sudo pip3 install sortmuz


wordup?
-------

sortmuz scans a downloaded music album directory and tries to guess the
appropriate artist name, album name, and year. It asks you to possibly
modify those three values, after which it "installs" the album to a
destination collection directory.

The artist name, album name, and year information is only used for
naming the destination directories, i.e. sortmuz does not alter tags.

The collection directory has the following layout:

    collection/
      aKido/
        2005 Playtime/
          _/
            <copied meta files here; everything not music>
          <copied music files here>
        2007 Blink/
          _/
            ...
          ...
      BADBADNOTGOOD/
        ...
      King Crimson/
        ...
      ...

sortmuz currently supports `.mp3`, `.flac`, and `.m4a` files.


using
-----

See

    sortmuz --help
