SPLASH
======

How to use
----------

You should have installed PySide and PySide-tools (or something like that, to compile .ui files)

Run this commands in splash directory:

    mkvirtualenv splash
    setvirtualenvproject (optional)
    pip install -r requirements.txt
    ./pyside-to-virtualenv.sh
    (cd ui/; pyside-uic splash.ui > ui_splash.py)
    python splash.py
