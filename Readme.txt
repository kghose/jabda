Jabda is a personal journal (diary) program 
Copyright (C) 2011 Kaushik Ghose 

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

History
-------
A rewriting of the Diary sub-app contained in RRiki. Jabda uses python as its
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