A rewriting of the Diary sub-app contained in RRiki. PyLog uses python as its
language, SQlite as its database backend and bottle as the browser server 
framework.

Making an application out of this:

py2applet --make-setup pylog.py index.tpl diary.sqlite3 icon.icns
python setup.py py2app

OR

py2applet pylog.py index.tpl diary.sqlite3 icon.icns