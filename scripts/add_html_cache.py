"""Converts db from older pylog version to one that caches the html and
nice date."""

"""Add an html cache column to the notes table to speed up display.

* First from the command line, make a copy of your current chotha db
* Add a column called html to the db
* For each note, load the 'body', run markdown on it and save the html under html
"""
import datetime, sqlite3, sys, markdown2
md = markdown2.markdown

def cache_generator(rows_in):
  """Run each note through the markdown parser."""

  def nice_date(date):
    """We can't do this in the db as sqlites strftime does not support the 
    formats we want."""
    nd = datetime.date(int(date[0:4]),int(date[5:7]),int(date[8:10]))
    return nd.strftime('%a %b %d, %Y')
  
  for this_row in rows_in:
    yield (nice_date(this_row['date']),md(this_row['body']),this_row['id'])
    

if __name__ == "__main__":
  if len(sys.argv) > 1:
    diary_db = sys.argv[1]
  else:
    exit()

  print 'Adding htmlcache column to ' + diary_db

  conn = sqlite3.connect(diary_db)
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
#  query = 'ALTER TABLE entries ADD COLUMN "htmlcache" TEXT'
#  c.execute(query)

#  query = 'ALTER TABLE entries ADD COLUMN "nicedate" TEXT'
#  c.execute(query)

  print 'Caching html'
  rows = c.execute('SELECT id,date,body FROM entries').fetchall()
  print len(rows)
  c.executemany('UPDATE entries SET nicedate=?, htmlcache=? WHERE id=?', cache_generator(rows))
  conn.commit()
  print 'Done'