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
  return c, conn

def fetch_entries():  
  c, conn = get_cursor()
  c.execute('select * from entries order by date desc')
  #return c.fetchall()
  return parse_entries(c.fetchall())

def fetch_entries_by_year(year):
  """Fetch all entries for the given year. I chose this as a good compromise
  against fetching all the entries which was slowing things down due to markdown."""
  c, conn = get_cursor()
  st = '%s-01-01' %(year)
  nd = '%s-12-31' %(year)
  c.execute("select * from entries where (date >= date(?) and date <= date(?)) order by date desc", (st,nd))
  rows = c.fetchall()
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

def create_new_entry(entry):
  c, conn = get_cursor()
  c.execute("INSERT INTO entries (title,date,body) VALUES (?,?,?)", (entry['title'], datetime.datetime.now(), entry['body']))
  conn.commit()
  
@route('/')  
@route('/:year')
def index(year=str(datetime.date.today().year)):

  rows = fetch_entries_by_year(year)
  output = template('index', rows=rows, year=year)
  return output


@route('/new', method='GET')
def new_item():

  title = request.GET.get('title', '').strip()
  body = request.GET.get('body', '').strip()
  entry = {'title': title, 'body': body}
  create_new_entry(entry)  
  return index()


def test_run():
  import profile
  profile.run(bottle.run(host='localhost', port=8080))

if __name__ == "__main__":  
  debug(True)  
  bottle.run(host='localhost', port=8080,reloader=True)
  #bottle.run(host='localhost', port=8080)
  