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
import Tkinter as tki, argparse, ConfigParser, sqlite3
from os.path import join, expanduser

class App(object):

  def __init__(self):
    self.root = tki.Tk()
    self.root.wm_title('Jabda')
    self.load_prefs()
    self.connect_to_database()
    self.setup_window()
    self.set_entries(self.get_all_entries())
    self.root.wm_protocol("WM_DELETE_WINDOW", self.cleanup_on_exit)
    self.cmd_state = 'Idle'

  def load_prefs(self):
    self.config_fname = expanduser('~/jabda.cfg')
    self.config_default = {
        'dbpath': 'mydiary.sqlite3',
        'geometry': 'none',
    }
    self.config = ConfigParser.ConfigParser(self.config_default)
    self.config.read(self.config_fname)

  def connect_to_database(self):
    """Returns us a cursor and connection object to our database."""
    self.conn = sqlite3.connect(self.config.get('DEFAULT','dbpath'))
    #self.conn.row_factory = sqlite3.Row

  def get_all_entries(self):
    """Date formatting from http://www.sqlite.org/lang_datefunc.html."""
    c = self.conn.cursor()
    c.execute("SELECT id, DATE(date) FROM entries order by date desc")
    return c.fetchall()

  def set_entries(self, list):
    self.listbox.delete(0, tki.END) # clear
    for id, value in list:
      self.listbox.insert(tki.END, value)
    self.entries = list

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
    self.edit_win.bind("<Shift-Return>", self.save)

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
      elif chr=='e':
        self.edit()
      elif chr=='d':
        self.set_database()

  def selection_changed(self, event=None):
    item = self.listbox.curselection()[0]
    sel_id = int(self.entries[int(item)][0])
    c = self.conn.cursor()
    c.execute("SELECT id, body FROM entries WHERE id={:d}".format(sel_id))
    self.current_entry = c.fetchone()
    self.edit_win.delete(1.0, tki.END)
    self.edit_win.insert(tki.END, self.current_entry[1])

  def new(self):
    self.cmd_state ='editing'
    self.current_entry = ('','') #No id, no body
    self.edit_win.delete(1.0, tki.END)
    self.listbox.config(state=tki.DISABLED)
    self.edit_win.focus_set()

  def save(self, event):
    if self.edit_win.edit_modified():
      print saving
      self.set_entries(self.get_all_entries())
    self.listbox.config(state=tki.NORMAL)
    self.listbox.focus_set()




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

  def browse_history(self, keysym):
    partial = self.cmd_win.get(1.0, tki.INSERT)
    insert = self.cmd_win.index(tki.INSERT)
    if keysym == 'Up':
      step = -1
    else:
      step = 1
    suggestion = self.cmd_history.completion(partial, step)
    if suggestion is not '':
      self.cmd_win.delete(1.0, tki.END)
      self.cmd_win.insert(tki.END, suggestion)
      self.cmd_win.mark_set(tki.INSERT, insert)

  def set_new_photo_root(self, new_root):
    self.config.set('DEFAULT', 'root', new_root)
    self.tab.widget_list[0].set_dir_root(new_root) #0 is the disk browser

  def search_execute(self, query_str):
    self.log_command('Searching for {:s}'.format(lch.query_to_rawquery(query_str)))
    files = lch.execute_query(query_str, root = self.config.get('DEFAULT', 'root'))
    self.tab.widget_list[1].virtual_flat(files, title='Search result') #1 is the search window
    self.show_search()
    self.log_command('Found {:d} files.'.format(len(files)))

  def open_external(self, event):
    files = self.tab.active_widget.file_selection()#Only returns files
    if len(files): lch.quick_look_file([fi[0] for fi in files])

  def reveal_in_finder(self):
    files_folders = self.tab.active_widget.all_selection()#Returns both files and folders
    if len(files_folders): lch.reveal_file_in_finder([fi[0] for fi in files_folders])

  def add_selected_to_pile(self):
    files = self.tab.active_widget.file_selection()#Only returns files
    l0 = len(self.pile)
    for f in files:
      self.pile.add(f[0])
    l1 = len(self.pile)
    self.log_command('Added {:d} files to pile.'.format(l1-l0))

  def remove_selected_from_pile(self):
    files = self.tab.active_widget.file_selection()#Only returns files
    l0 = len(self.pile)
    for f in files:
      self.pile.discard(f[0])
    l1 = len(self.pile)
    self.log_command('Removed {:d} files from pile.'.format(l0-l1))

  def clear_pile(self):
    self.pile.clear()
    self.log_command('Pile cleared')

  def show_pile(self):
    self.tab.widget_list[2].virtual_flat(self.pile, title='Showing pile.')
    self.tab.set_active_widget(2)
    self.selection_changed()
    self.log_command('Picture pile')

  def show_browser(self):
    self.tab.set_active_widget(0)
    self.selection_changed()
    self.log_command('File browser')

  def show_search(self):
    self.tab.set_active_widget(1)
    self.selection_changed()
    self.log_command('Search results')

  def resize_and_show(self, size):
    size = (int(size[0]), int(size[1]))
    out_dir = tempfile.mkdtemp()
    for n,file in enumerate(self.pile):
      outfile = join(out_dir, '{:06d}.jpg'.format(n))
      im = Image.open(file)
      im.thumbnail(size, Image.ANTIALIAS)
      im.save(outfile, 'JPEG')
    lch.reveal_file_in_finder([out_dir])

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
