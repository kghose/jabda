A rewriting of the Diary sub-app contained in RRiki. PyLog uses python as its
language, SQlite as its database backend and bottle as the browser server 
framework.

Making an application out of this:

py2applet --make-setup pylog.py index.tpl diary.sqlite3 icon.icns
python setup.py py2app

OR

py2applet pylog.py index.tpl diary.sqlite3 icon.icns



TODOS:

1. Incorporate snippet in search and return search results like a search
engine, from which we can click and open individual entries

2. Look into full text search

3. Bug in FF5 with textbox and span and submit button etc.