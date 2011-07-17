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
  return c.fetchall()
  
def fetch_all_entries():
  """Returns a list of all the entries in the diary."""
  c, conn = get_cursor()
  c.execute('SELECT * FROM entries ORDER BY date DESC')
  return c.fetchall()

def fetch_entries_by_year(year):
  """Fetch all entries for the given year. I chose this as a good compromise
  against fetching all the entries which was slowing things down due to markdown."""
  c, conn = get_cursor()
  st = '%s-01-01' %(year)
  nd = '%s-12-31' %(year)
  c.execute("SELECT * FROM entries WHERE (date >= date(?) AND date <= date(?)) ORDER BY date DESC", (st,nd))
  return c.fetchall()

def fetch_entries_by_search(text):
  """Fetch all entries containing text."""
  c, conn = get_cursor()
  c.execute("SELECT * FROM entries WHERE (title LIKE ? OR body LIKE ?) order by date desc", ("%%%s%%" %text, "%%%s%%" %text))
  return c.fetchall()
  
def cache_generator(entry):
  """Generate our html cache"""
  def nice_date(date):
    """We can't do this in the db as sqlites strftime does not support the 
    formats we want."""
    nd = datetime.date(int(date[0:4]),int(date[5:7]),int(date[8:10]))
    return nd.strftime('%a %b %d, %Y')
  
  entry['nicedate'] = nice_date(entry['date'])
  entry['htmlcache'] = md(entry['body'])
  return entry

def create_new_entry(entry):
  c, conn = get_cursor()
  entry['date'] = datetime.datetime.now().isoformat()
  entry = cache_generator(entry)
  c.execute("INSERT INTO entries (title,date,nicedate,body,htmlcache,created_at,updated_at) VALUES (?,?,?,?,?,?,?)", 
            (entry['title'], entry['date'], entry['nicedate'], entry['body'], entry['htmlcache'], entry['date'], entry['date']))
  conn.commit()
  

def save_entry(entry):
  """We then refetch the saved entry so we can display it."""
  c, conn = get_cursor()
  now = datetime.datetime.now()
  entry = cache_generator(entry)  
  c.execute("UPDATE entries SET date = ?, nicedate = ?, title = ?, body = ?, htmlcache = ?, updated_at = ? WHERE id LIKE ?", 
            (entry['date'], entry['nicedate'], entry['title'], entry['body'], entry['htmlcache'], now, entry['id']))
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

  #rows = fetch_entries_by_year(year)
  rows = fetch_all_entries()
  output = template('index', rows=rows, 
                    year=year, year_count=get_year_count_list(), 
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
  output = template('index', entry=entry, 
                    year=year, year_count=get_year_count_list(), 
                    title='Editing', view='edit')
  return output

@route('/save/:id', method='POST')
def save_item(year=str(datetime.date.today().year),id=None):

  date = request.POST.get('date', '').strip()
  title = unicode(request.POST.get('title', '').strip(),'utf_8')
  body = unicode(request.POST.get('body', '').strip(),'utf_8')
  entry = {'id': int(id), 'date': date, 'title': title, 'body': body}
  entry = save_entry(entry)
  output = template('index', entry=entry, 
                    year=year, year_count=get_year_count_list(),
                    title='Saved', view='saved')  
  return output

@route('/search')
def search(text=''):
  """."""
  text = unicode(request.GET.get('searchtext', '').strip(),'utf_8')
  rows = fetch_entries_by_search(text)
  output = template('index', rows=rows, 
                    year=str(datetime.date.today().year), year_count=get_year_count_list(),
                    title='Searched for "%s". Found %d entries' %(text,len(rows)), view='searchlist')
  return output


# Nasty stuff -------------------------------------------------------------------
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
  c.execute('CREATE TABLE "entries" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "title" varchar(255), "date" datetime, "nicedate" text, "body" text, "htmlcache" text, "created_at" datetime, "updated_at" datetime)')
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
  