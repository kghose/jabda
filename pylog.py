import datetime
import sqlite3
import markdown2 as markdown
md = markdown.markdown
import bottle
from bottle import route, debug, template, request, validate, send_file, error

import ConfigParser
config = ConfigParser.RawConfigParser()
dbname = None

def get_cursor():
  """Returns us a cursor and connection object to our database."""
  conn = sqlite3.connect(dbname)
  conn.row_factory = sqlite3.Row
  c = conn.cursor()
  return c, conn

def fetch_single_entry(id):
  c, conn = get_cursor()
  c.execute('SELECT * FROM entries WHERE id LIKE ?', (id,))
  #return c.fetchall()
  return parse_entries(c.fetchall())
  
def fetch_all_entries():
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

def fetch_entries_by_search(text):
  """Fetch all entries containing text."""
  c, conn = get_cursor()
  c.execute("SELECT * FROM entries WHERE (title LIKE ? OR body LIKE ?) order by date desc", ("%%%s%%" %text, "%%%s%%" %text))
  rows = c.fetchall()
  return parse_entries(rows)
  
def parse_entries(rows_in):
  """Given a list of row objects returned by a fetch, copy the data into a new
  dictionary after running each entry through the markdown parser."""
  def nice_date(date):
    nd = datetime.date(int(date[0:4]),int(date[5:7]),int(date[8:10]))
    return nd.strftime('%a %b %d, %Y')
  
  rows = []
  for this_row in rows_in:
    new_row = {
      'id': this_row['id'],
      'date': this_row['date'],
      'nicedate': nice_date(this_row['date']),
      'title': this_row['title'],
      'body': md(this_row['body']),
      'markup text': this_row['body'],
      'updated_at': this_row['updated_at']}
    rows.append(new_row)
  return rows

def create_new_entry(entry):
  c, conn = get_cursor()
  now = datetime.datetime.now()
  c.execute("INSERT INTO entries (title,date,body,created_at,updated_at) VALUES (?,?,?,?,?)", 
            (entry['title'], now, entry['body'], now, now))
  conn.commit()
  

def save_entry(entry):
  """We then refetch the saved entry so we can display it."""
  c, conn = get_cursor()
  now = datetime.datetime.now()  
  c.execute("UPDATE entries SET date = ?, title = ?, body = ?, updated_at = ? WHERE id LIKE ?", 
            (entry['date'], entry['title'], entry['body'], now, entry['id']))
  conn.commit()
  return fetch_single_entry(entry['id'])[0]

def get_year_count_list():
  """Return a list of years that are in our database and the number of entries
  in that year."""
  c, conn = get_cursor()
  c.execute("select strftime('%Y',date) as year, count(date) as cnt from entries group by year order by year desc")
  rows = c.fetchall()
  return rows

# Common use pages -------------------------------------------------------------
  
@route('/')  
@route('/:year')
def index(year=str(datetime.date.today().year)):
  """Main page serve function. 
  If edit is True and id has a integer value,
  instead of showing a form for a new entry at the top, setup a form for
  editing the entry with id. Scroll to that form using an anchor (all this magic
  happens in the template)
  If edit is False but id is an integer, scroll to that entry using an anchor.
  This is used to show us an entry we have just edited."""

  rows = fetch_entries_by_year(year)
  output = template('index', rows=rows, year=year, 
                    year_count=get_year_count_list(), 
                    title=year, view='list')
  return output

#We use POST for creating/editing the entries because these operations have 
#lasting observable effects on the state of the world
#
@route('/new', method='POST')
def new_item():

  title = unicode(request.POST.get('title', '').strip(),'utf_8')
  body = unicode(request.POST.get('body', '').strip(),'utf_8')
  entry = {'title': title, 'body': body}
  create_new_entry(entry)  
  return index()

@route('/edit/:id')
def edit_item(year=str(datetime.date.today().year),id=None):
  
  entry = fetch_single_entry(id)[0]
  output = template('index', year=year, entry=entry, title='Editing', 
                    current_year=str(datetime.date.today().year),
                    view='edit')
  return output

@route('/save/:id', method='POST')
def save_item(year=str(datetime.date.today().year),id=None):

  date = request.POST.get('date', '').strip()
  title = unicode(request.POST.get('title', '').strip(),'utf_8')
  body = unicode(request.POST.get('body', '').strip(),'utf_8')
  entry = {'id': int(id), 'date': date, 'title': title, 'body': body}
  entry = save_entry(entry)
  output = template('index', year=year, entry=entry, title='Saved', 
                    current_year=str(datetime.date.today().year),
                    view='saved')  
  return output

@route('/search')
def search(text=''):
  """."""
  text = unicode(request.GET.get('searchtext', '').strip(),'utf_8')
  rows = fetch_entries_by_search(text)
  output = template('index', rows=rows, year=str(datetime.date.today().year), 
                    current_year=str(datetime.date.today().year),
                    title='Searched for "%s. Found %d entries"' %(text,len(rows)), view='searchlist')
  return output


@route('/quit')
def quit_server():
  """A bit extreme, but really the only thing that worked, including exit(0),
  and SIGINT. Not needed if we use it from the command line or as a startup
  server, but essential when we use it as an app."""
  bottle.os._exit(0)  

# Configuration helpers --------------------------------------------------------
def create_default_config_file():
  config.add_section('Basic')
  config.set('Basic', 'dbname', 'diary.sqlite3')
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

# Configuration pages ---------------------------------------------------------  
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
  config.set('Basic', 'dbname', newdbname)
  save_config()
  return index()
  
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
  