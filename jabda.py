"""
Jabda is a simple personal diary program. I am encouraged to write a diary if I can make entries quickly. I had Jabda as a bottle application using a browser as the GUI and that worked fine, but the program was not as responsive as I wanted. Jabda is now a very simple TKinter application running off a sqlite backend.

|-------------------|
|     |             |
|  A  |      B      |
|     |             |
|     |             |
|-------------------|

A - list box that lets us flip through our entries/search results
B - reading/writing pane.

New entry   -  Press 'n'. The B window will clear, allowing you to create your entry.
               Press <shift> + <enter> to save the entry. ESC to cancel
               Pane A is inactive during editing

Edit entry  -  Just edit the text in box B.
               Press <shift> + <enter> to save. ESC to cancel
               Pane A is inactive during editing

Search      -  Press 's'. The B window will clear. Type your term and hit <shift> + <enter>

Exit search -  Press 'x'
"""

import logging
logger = logging.getLogger(__name__)
import Tkinter as tki, argparse, ConfigParser, sqlite3, os.path, datetime

class App(object):

  def __init__(self):
    self.root = tki.Tk()
    self.root.wm_title('Jabda')
    self.load_prefs()
    self.connect_to_database()
    self.setup_window()
    self.set_entry_list(self.get_all_entries())
    self.root.wm_protocol("WM_DELETE_WINDOW", self.cleanup_on_exit)
    self.cmd_state = 'Idle'

  def load_prefs(self):
    self.config_fname = os.path.expanduser('~/jabda.cfg')
    self.config_default = {
        'dbpath': 'test.sqlite3',
        'geometry': 'none',
    }
    self.config = ConfigParser.ConfigParser(self.config_default)
    self.config.read(self.config_fname)

  def create_database(self):
    logger.info('Creating new database')
    c = self.conn.cursor()
    c.execute('CREATE TABLE "entries" ("id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, "entry_date" datetime, "entry" text)')
    self.conn.commit()

  def connect_to_database(self):
    """Returns us a cursor and connection object to our database."""
    logger.info('Connecting to {:s}'.format(self.config.get('DEFAULT','dbpath')))
    need_to_create_db = not os.path.exists(self.config.get('DEFAULT','dbpath'))
    self.conn = sqlite3.connect(self.config.get('DEFAULT','dbpath'))
    if need_to_create_db: self.create_database()
    #self.conn.row_factory = sqlite3.Row

  def get_all_entries(self):
    """Date formatting from http://www.sqlite.org/lang_datefunc.html."""
    c = self.conn.cursor()
    c.execute("SELECT id, DATE(entry_date) FROM entries order by entry_date desc")
    return c.fetchall()

  def set_entry_list(self, list):
    self.listbox.delete(0, tki.END) # clear
    for id, value in list:
      self.listbox.insert(tki.END, value)
    self.entries = list
    self.current_entry_id = None

  def setup_window(self):
    self.listbox = tki.Listbox(self.root, selectmode=tki.BROWSE, selectbackground='black', selectforeground='white', selectborderwidth=0, width=13, bd=5, highlightthickness=0)
    self.listbox.pack(side='left', fill='y')
    #self.listbox.bind("<ButtonRelease-1>", self.selection_changed)
    #self.listbox.bind("<KeyRelease-Up>", self.selection_changed)
    #self.listbox.bind("<KeyRelease-Down>", self.selection_changed)
    self.listbox.bind('<<ListboxSelect>>', self.selection_changed)
    self.listbox.bind("<Key>", self.cmd_key_trap)

    self.edit_win = tki.Text(self.root, undo=True, width=50, height=12, fg='white', bg='black', insertbackground='white', highlightthickness=0, wrap=tki.WORD)
    self.edit_win.pack(side='left', expand=True, fill='both')
    self.edit_win.bind('<<Modified>>', self.edit_start) #We set this rightaway because we want to be able to start a new entry by just typing
    self.edit_win.bind("<Shift-Return>", self.shift_enter_pressed)

    geom=self.config.get('DEFAULT', 'geometry')
    if geom != 'none':
      self.root.geometry(geom)

  def cleanup_on_exit(self):
    """Save pending edits configuration."""
    #self.save_entry()
    self.config.set('DEFAULT', 'geometry', self.root.geometry())
    with open(self.config_fname, 'wb') as configfile:
      self.config.write(configfile)
    self.root.quit() #Allow the rest of the quit process to continue

  def cmd_key_trap(self, event):
    chr = event.char
    if self.cmd_state == 'Idle':
      if chr=='n':
        self.new()
        return 'break'
      elif chr=='s':
        self.start_search()
        return 'break'
      elif chr=='d':
        self.set_database()

  def selection_changed(self, event=None):
    item = self.listbox.curselection()[0]
    sel_id = int(self.entries[int(item)][0])
    c = self.conn.cursor()
    c.execute("SELECT id, entry FROM entries WHERE id={:d}".format(sel_id))
    entry = c.fetchone()
    self.edit_win.unbind('<<Modified>>') #Deleting and inserting will trigger the callback
    self.edit_win.delete(1.0, tki.END)
    self.edit_win.insert(tki.END, entry[1])
    self.edit_win.edit_modified(0) #Deleting and inserting sets this flag
    self.edit_win.bind('<<Modified>>', self.edit_start)
    self.current_entry_id = entry[0]

  def new(self):
    self.current_entry_id = None #No id
    self.edit_win.unbind('<<Modified>>') #Deleting and inserting will trigger the callback
    self.edit_win.delete(1.0, tki.END)
    self.edit_win.focus_set()
    self.start_editing()

  def edit_start(self, event):
    self.start_editing()

  def start_editing(self):
    """We need to
       1) Disable the listbox
       2) Disconnect the selection changed function (Tkinter bug IMO)
    """
    self.cmd_state ='editing'
    self.listbox.config(state=tki.DISABLED)
    self.listbox.unbind('<<ListboxSelect>>') #Don't forget to bind after all this is over

  def end_editing(self):
    self.listbox.config(state=tki.NORMAL)
    #TODO keep cursor at current entry
    self.set_entry_list(self.get_all_entries())
    self.listbox.focus_set()
    self.listbox.bind('<<ListboxSelect>>', self.selection_changed)

  def shift_enter_pressed(self, event):
    if self.cmd_state=='editing':
      self.save()
      return 'break'
    elif self.cmd_state=='search':
      self.search()
      return 'break'

  def save(self):
    if self.edit_win.edit_modified():
      logger.debug('Saving entry')
      entry_text = self.edit_win.get(1.0, tki.END)
      if self.current_entry_id is None:
        query = 'INSERT INTO entries (entry_date, entry) VALUES (?,?)'
        bindings = (datetime.datetime.now(), entry_text)
      else:
        query = 'UPDATE entries SET entry = ? WHERE id = ?'
        bindings = (entry_text, self.current_entry_id)
      c = self.conn.cursor()
      c.execute(query, bindings)
      self.conn.commit()
    self.end_editing()

  def log_command(self, cmd):
    if hasattr(self, 'log_win_after_id'):
      self.log_win.after_cancel(self.log_win_after_id)
    self.log_win.insert(tki.END, '|' + cmd)
    self.log_win_after_id = self.log_win.after(2000, self.clear_log_command)

  def clear_log_command(self):
    self.log_win.delete(1.0, tki.END)

  def command_cancel(self):
    self.cmd_win.delete(1.0, tki.END)
    self.cmd_state = 'Idle'
    self.log_command('Command canceled.')

  def search_execute(self, query_str):
    self.log_command('Searching for {:s}'.format(lch.query_to_rawquery(query_str)))
    files = lch.execute_query(query_str, root = self.config.get('DEFAULT', 'root'))
    self.tab.widget_list[1].virtual_flat(files, title='Search result') #1 is the search window
    self.show_search()
    self.log_command('Found {:d} files.'.format(len(files)))

  def show_help(self):
    top = tki.Toplevel()
    top.title("Help")
    msg = tki.Message(top, text=__doc__, font=('consolas', 11))
    msg.pack()
    self.log_command('Showing help')

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument('-d', default=False, action='store_true', help='Print debugging messages')
  args,_ = parser.parse_known_args()
  if args.d:
    level=logging.DEBUG
  else:
    level=logging.INFO
  logging.basicConfig(level=level)

  app = App()
  app.root.mainloop()
