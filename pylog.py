import datetime
import sqlite3
import markdown2 as markdown
#import discount
#md = discount.Markdown
import bottle
from bottle import route, debug, template, request, validate, send_file, error

def get_cursor():
  conn = sqlite3.connect('pylogdb.sqlite3')
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
  return c

def fetch_entries(c):  
  c.execute('select * from entries order by date desc')
  #return c.fetchall()
  return parse_entries(c.fetchall())

def fetch_entries_by_year(c, year):
  st = '%s-01-01' %(year)
  nd = '%s-12-31' %(year)
  print st,nd
  c.execute("select * from entries where (date >= date(?) and date <= date(?)) order by date desc", (st,nd))
  rows = c.fetchall()
  print len(rows)
  return parse_entries(rows)
  
def parse_entries(rows_in):
  rows = []
  for this_row in rows_in:
    new_row = {         
      'date': this_row['date'],
      'title': this_row['title'],
      'body': markdown.markdown(this_row['body'])}
    rows.append(new_row)
  return rows

@route('/')  
@route('/:year')
def index(year=str(datetime.date.today().year)):
  
    c = get_cursor()
    rows = fetch_entries_by_year(c,year)
    output = template('index', rows=rows, year=year)
    return output

def test_run():
  import profile
  profile.run(bottle.run(host='localhost', port=8080))

if __name__ == "__main__":  
  debug(True)  
  bottle.run(host='localhost', port=8080,reloader=True)
  #bottle.run(host='localhost', port=8080)
  