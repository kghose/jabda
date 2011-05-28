import datetime
import sqlite3
import markdown2 as markdown
#import discount
#md = discount.Markdown
import bottle
from bottle import route, debug, template, request, validate, send_file, error

import ConfigParser
config = ConfigParser.RawConfigParser()
dbname = None

def get_cursor():
  """Returns us a cursor and connection object to our database."""
  print dbname
  conn = sqlite3.connect(dbname)
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
  return c, conn

def fetch_entries():
  """Not really used. Returns a list of all the entries in the diary."""
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
  """Given a list of row objects returned by a fetch, copy the data into a new
  dictionary after running each entry through the markdown parser."""
  rows = []
  for this_row in rows_in:
    new_row = {
      'id': this_row['id'],
      'date': this_row['date'],
      'title': this_row['title'],
      'body': markdown.markdown(this_row['body']),
      'markup text': this_row['body']}
    rows.append(new_row)
  return rows

def create_new_entry(entry):
  c, conn = get_cursor()
  c.execute("INSERT INTO entries (title,date,body) VALUES (?,?,?)", (entry['title'], datetime.datetime.now(), entry['body']))
  conn.commit()

def save_entry(entry):
  c, conn = get_cursor()
  c.execute("UPDATE entries SET title = ?, body = ? WHERE id LIKE ?", (entry['title'], entry['body'], entry['id']))
  conn.commit()

# Common use pages -------------------------------------------------------------
  
@route('/')  
@route('/:year')
def index(year=str(datetime.date.today().year), edit=False, id=None):
  """Main page serve function. 
  If edit is True and id has a integer value,
  instead of showing a form for a new entry at the top, setup a form for
  editing the entry with id. Scroll to that form using an anchor (all this magic
  happens in the template)
  If edit is False but id is an integer, scroll to that entry using an anchor.
  This is used to show us an entry we have just edited."""

  print type(edit), type(id)
  rows = fetch_entries_by_year(year)
  output = template('index', rows=rows, year=year, edit=edit, id=id)
  return output

#We use POST for creating/editing the entries because these operations have 
#lasting observable effects on the state of the world
#
@route('/new', method='POST')
def new_item():

  title = request.POST.get('title', '').strip()
  body = request.POST.get('body', '').strip()
  entry = {'title': title, 'body': body}
  create_new_entry(entry)  
  return index()

@route('/edit/:year/:id')
def edit_item(year=None,id=None):
  
  return index(year,True,id)

@route('/save/:year/:id', method='POST')
def save_item(year=None,id=None):
  title = request.POST.get('title', '').strip()
  body = request.POST.get('body', '').strip()
  entry = {'id': int(id), 'title': title, 'body': body}
  save_entry(entry)
  return index(year,False,id)

# Configuration pages ---------------------------------------------------------
def create_default_config_file():
  config.add_section('Basic')
  config.set('Basic', 'dbname', 'pylog.sqlite3')
  config.set('Basic', 'host', 'localhost')
  config.set('Basic', 'port', '3010')
  
  config.add_section('Advanced')  
  config.set('Advanced', 'debug', 'False')
  config.set('Advanced', 'reloader', 'False')
  
  with open('pylog.cfg', 'wb') as configfile:
    config.write(configfile)  

def load_config():
  result = config.read('pylog.cfg')
  if len(result) == 0:
    create_default_config_file()

def save_config():
  with open('pylog.cfg', 'wb') as configfile:
    config.write(configfile)  
  
def create_database():
  """."""
  c, conn = get_cursor()
  c.execute('CREATE TABLE "entries" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "title" varchar(255), "date" datetime, "body" text, "place" varchar(255), "lat" decimal, "lon" decimal, "created_at" datetime, "updated_at" datetime)')
  conn.commit()
  
@route('/selectdb/:newdbname')
def select_database(newdbname='pylogdb.sqlite3'):
  globals()['dbname']=newdbname
  config.set('Basic', 'dbname', newdbname)
  save_config()
  return index()

@route('/createdb/:newdbname')
def new_database(newdbname='pylogdb.sqlite3'):
  globals()['dbname']=newdbname
  create_database()
  return index()

def test_run():
  import profile
  profile.run(bottle.run(host='localhost', port=8080))

if __name__ == "__main__":
  
  load_config()
  deb = config.getboolean('Advanced', 'debug')
  host = config.get('Basic','host')
  port = config.getint('Basic', 'port')
  relo = config.getboolean('Advanced', 'reloader')
  globals()['dbname'] = config.get('Basic','dbname')
  debug(deb)  
  bottle.run(host=host, port=port,reloader=relo)
  #bottle.run(host='localhost', port=8080)
  