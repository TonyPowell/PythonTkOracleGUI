from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
import tkinter.ttk as ttk
import tkinter.tix as tix
import cx_Oracle
import hlist_screens as screens
import logging
from subprocess import Popen

# Great a logger for the dbUtil module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(funcName)s:%(message)s')

file_handler = logging.FileHandler('dbUtil.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Comment out the next 3 lines if you don't want log 
# messages displaying on the console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

"""
  Written using Python 3.5.4
                cx_Oracle-6.0.3-cp35-cp35m-win_amd64.whl
"""
debug = False

################################################################################  
#                        Connect to the database
################################################################################
       
def getDSN(varDBName):
    for db in getDBs():
       if db["db"] == varDBName:
         dsn=cx_Oracle.makedsn(db["host"],db["port"],db["SID"])
       return dsn
      
    return None


   
#_______________________________________________________________________________
#                           ConnectionInfo Class
#_______________________________________________________________________________  
class ConnectionInfo(object):
   """ 
     Displays a login dialog box and formats and returns an Oracle database
    connection string from the user input of name, password and database       
   """
   Oracle_connect_string = None
   cx_Oracle_connection_object = None
   current_db = None
   Oracle_version = None
   
   def __init__(self, parent ):  
      self.parent = parent
      #  Create a toplevel widget to contain
      # all the other widgets
      #----------------------------------------------------
      top = self.top = Toplevel(parent) 
      top.title("Login") 
      top.geometry("250x100+300+300")
      top.resizable(width=False,height=False)
      #topFrame = ttk.Frame(top,padding=(3,3,5,5))
      #topFrame.grid(column=0, row=0, sticky=(N,W,E,S))
      
      # Use ttk's Tk themed widget set to configure
      # the appearance of ttk buttons
      #----------------------------------------------------
      style = ttk.Style()
      style.configure("TButton",foreground="midnight blue",
                      font="Times 12")
      
      #Create variables to hold the user input
      #----------------------------------------------------
      self.connect_string = None
      self.conn_user = StringVar()
      self.user_pwd = StringVar()
      self.database = StringVar()
      
      # Set the focus to the top widget, route all events for this
      # application to the top widget and bind the top delete window 
      # button to _cancel
      #----------------------------------------------------
      self.initial_focus =  top  
      top.grab_set()
      top.protocol("WM_DELETE_WINDOW", self._cancel)

      #  Create the widgets for the user, password 
      # and database entries
      #----------------------------------------------------
      self.user_lbl =Label(top, text="User:")
      self.user_entry = Entry(top, width=25,textvariable=self.conn_user)
      # Force keyboard focus to the User entry widget
      self.user_entry.focus_force()
      #Hide the password entry with asterisks
      self.pwd_lbl = Label(top, text="Password:")
      self.pwd_entry = Entry(top, width=25,textvariable=self.user_pwd,show="*")
      self.db_lbl = Label(top, text="Database:")
      self.db_entry = Entry(top, width=25,textvariable=self.database )
      self.connect_string = "Cancel"
      
      # Create the OK and Cancel buttons
      #----------------------------------------------------
      self.ok_btn = ttk.Button(top, text="OK", width=5, command=self._format_conn_string)
      #self.ok_btn.bind("<Return>", self._format_conn_string)
      self.cancel_btn = ttk.Button(top, text="Cancel", width=10, command=self._cancel)
   
      # Arrange the widgets on the login dialog box 
      #----------------------------------------------------
      self.user_lbl.grid(row=0, sticky=W)
      self.user_entry.grid(row=0, column=1)      
      self.pwd_lbl.grid(row=1, sticky=W)
      self.pwd_entry.grid(row=1, column=1)      
      self.db_lbl.grid(row=2, sticky=W)
      self.db_entry.grid(row=2, column=1)
      self.ok_btn.grid(row=3, column=1,sticky=W)
      self.cancel_btn.grid(row=3, column=1,sticky=E)
      

   
   def _format_conn_string(self):  
      self.connect_string = "%s/%s@%s" % (self.conn_user.get(),self.user_pwd.get(),self.database.get())
      self.top.destroy()
      
   def return_value(self):
       return self.connect_string
       
   def _cancel(self, event=None):
      self.connect_string = "Cancel"
      self.top.destroy()
   
#_______________________________________________________________________________  
#                                login
#_______________________________________________________________________________       
def login( connect_string):
   """
      Uses the info the user provided in the ConnectionInfo login dialog box 
     to connect to the Oracle database
   """
    
   current_db = connect_string.split("@")[1]
   try:
      if debug:
        logger.debug('Connecting to {}'.format(current_db))
      conn = cx_Oracle.connect(connect_string)
      # Set the ConnectionInfo attributes that are used by other
      # functions in this module
      ConnectionInfo.cx_Oracle_connection_object = conn
      ConnectionInfo.Oracle_connect_string = connect_string
      ConnectionInfo.current_db = current_db
      try:
          cur = conn.cursor()
          cur.execute("SELECT banner FROM v$version WHERE ROWNUM < 2" )
          version = cur.fetchone()
          ConnectionInfo.Oracle_version = version
          if debug:
              logger.debug('version of {} = {}'.\
                           format(current_db,ConnectionInfo.Oracle_version))
          cur.close()
      except cx_Oracle.Error as exc:
          error, = exc.args          
          title = "Error connecting to " + current_db 
          display_error(title, error.message)
          if debug:
              logger.debug("Oracle error {}".format(error.message))              
          cur.close()
      return conn 
   except cx_Oracle.Error as exc: 
      error, = exc.args
      title = "Error connecting to " + current_db 
      display_error(title, error.message)

      
################################################################################  
#                         Window display functions
################################################################################
#_______________________________________________________________________________
#                              build_screen 
#_______________________________________________________________________________  
def build_screen(screen_def, main_window = False):
   """
       Creates a screen for the Tix Scrolled HList that displays the results
       of the SQL query associated with the "query" key word of the designated
       screen definition
   """
   
       
   if debug:
     logger.debug("debug = {}".format( debug))
     # Check to see if the ConnectionInfo attributes are properly set
     logger.debug("the connection object = {}".\
                   format(ConnectionInfo.cx_Oracle_connection_object))
     logger.debug("the connect string = {}".\
                   format(ConnectionInfo.Oracle_connect_string))
     logger.debug("the current DB = {}".\
                        format(ConnectionInfo.current_db) )
     logger.debug("mainWindow = {}".format(screens.main_window))
     
   #NOTE: screen_def["window"] is bound to the object created by tix.Tk()
   window = screen_def["window"]
   query_displayed = None
   
   if main_window:
       screens.main_window = screen_def['name']
   
   if debug:
      logger.debug("Main Window = {}".format(screens.main_window))
      
   #--------------------------------------------------------------
   #                 Build the HList widget
   # Get the number of columns that will be displayed
   # in the HList 
   num_columns = len(screen_def["columns"])  
   # Set the desired options for the HList widget
   hlist_options = 'hlist.width 130 hlist.height 30' +  \
                   ' hlist.font -adobe-helvetica-bold-r-narrow--12-120' + \
                   ' hlist.background #B8B8B8 hlist.selectMode ' + screen_def["selectMode"] + \
                   ' hlist.columns %d hlist.header 1' % (num_columns +1,) 

   # Create the HList widget
   window.tixHList = tix.ScrolledHList(window,options=hlist_options)
   hlist = window.tixHList.hlist
   # Set the current screen's dictionary keyword "hlist" to point to the
   # newly created HList widget. This allows other parts of this module
   # to access and manipulate it.
   screen_def["hlist"] = hlist
   
   #            Create the headers for the HList widget
   #  The value for the screen_def "columns" key word is a list of tuples consisting 
   # of the Oracle column name and its corresponding header name, i.e. the name that
   # will be displayed in the HList header. Therefore, in the code below column[0] =
   # the Oracle column name and column[1] = the header name
   for column in screen_def["columns"]:
      num_hdr = screen_def["columns"].index(column)                 
      hlist.header_create(num_hdr,itemtype=tix.TEXT,text=column[1])
   #   
   #--------------------------------------------------------------
   
   # Use ttk's Tk themed widget set to configure
   # the appearance of ttk buttons
   style = ttk.Style()
   style.configure("TButton",foreground="midnight blue",
                      font="Times 10")
   style.configure('Red.TButton',foreground="dark red",
                      font="Times 10")       
  
   # Create a balloon tip for the buttons
   balloon_options = 'font -adobe-helvetica-italic-r-narrow--12-120' + \
                ' background  #99CCCC'              
   balloon_tip = tix.Balloon( window, background='lightyellow',
                              options = balloon_options)
   
  
   #--------------------------------------------------------------
   #    Create the "Close", "Refresh" and "Show SQL"  buttons
   #
   # Create a frame widget to group the buttons together
   win_buttons_frm = tix.Frame(window)       

   #Create a button to kill the HList's window         
   close_btn = ttk.Button(win_buttons_frm,text = "Close",
                          style='Red.TButton',
                          command = lambda : close_window(window))
   balloon_tip.bind_widget(close_btn, balloonmsg='Close this window')
 
   if screen_def['name'] != 'DBMSOutput':
        #  Create a button to re-run the query that populates
        # the HList         
        refresh_btn = ttk.Button(win_buttons_frm,text = "Refresh",
                                 command = lambda : refresh_display(screen_def))            
        balloon_tip.bind_widget(refresh_btn,
                                balloonmsg="Refresh the window's data")
        
   #  Create a button to display the query that was run to populate
   # the HList
   show_SQL_btn = ttk.Button(win_buttons_frm,text = "Show SQL",
                             command = lambda :
                                       show_SQL(screen_def,screens.displayed_query))
   balloon_tip.bind_widget(show_SQL_btn,
                    balloonmsg='Display the query executed to populate the window')
   #
   #--------------------------------------------------------------
   
        
   #--------------------------------------------------------------
   #             Create buttons for the external programs
   
   #Create a frame to group the external program buttons together
   prog_buttons_frm = tix.Frame(window)

   #  Create a button to open a SQL*Plus session for the
   # current user in the currently connected database
   sqlplus_btn = ttk.Button(prog_buttons_frm, text = "SQL*Plus",
                            command = lambda  : open_sqlplus(screen_def))
   current_db = ConnectionInfo.current_db.upper()
   current_user = ConnectionInfo.Oracle_connect_string.split("/")[0]
   balloon_tip.bind_widget(sqlplus_btn,
                           balloonmsg="Open SQL*Plus Session for {}@{}".\
                                       format(current_user,current_db))     
   
   #  Create a button to pop the text selected in the HList into Notepad
   edit_btn = ttk.Button(prog_buttons_frm, text = " Notepad ",
                         command = lambda : send_to_editor(screen_def))       
   balloon_tip.bind_widget(edit_btn,
                           balloonmsg='Pop Selected Text into a Notepad')
   #
   #--------------------------------------------------------------
   
   
   #--------------------------------------------------------------
   #              Create the sort widgets
   #
   if screen_def['name'] != 'DBMSOutput':
        #Create a frame to group the sort widgets together
        sort_widgets_frm = tix.Frame(window)
         
        sort_lbl = tix.Label(sort_widgets_frm,
                             font = '-adobe-helvetica-bold-r-narrow--12-120',
                             text="Sort By:")
        
        column_cbo1 = tix.ComboBox(sort_widgets_frm)
        column_cbo1.entry.config(disabledbackground='white',
                                 disabledforeground='black')
        
        column_cbo2 = tix.ComboBox(sort_widgets_frm)
        column_cbo2.entry.config(disabledbackground='white',
                                 disabledforeground='black')
        
        column_cbo3 = tix.ComboBox(sort_widgets_frm)
        column_cbo3.entry.config(disabledbackground='white',
                                 disabledforeground='black')
        
        sort_btn = ttk.Button(sort_widgets_frm,text = "Sort",
                              command = lambda :
                              sort_display(screen_def,columns_dict,
                                           column_cbo1,column_cbo2,
                                           column_cbo3))
        balloon_tip.bind_widget(sort_btn,
                                balloonmsg="Sort the window's data")
        
        clear_sort_btn = ttk.Button(sort_widgets_frm,text = "Clear",
                                    style='Red.TButton',
                                    command = lambda :
                                    clear_sort(column_cbo1,column_cbo2,
                                               column_cbo3))
        balloon_tip.bind_widget(clear_sort_btn,
                                balloonmsg="Clear the sort selections")
        
        #.............................................................  
        #   Populate the combo box widgets used for sorting
        # Build a dictionary with header names as keys and their
        # corresponding Oracle column names as values for the
        # keys
        columns_dict={}
        for column in screen_def["columns"]:
            columns_dict[column[1]]=column[0]
        if debug:   
           logger.debug("columns_dict=".format(columns_dict))
        # For each combobox widget, sequentially add each header name at the end 
        # of the combobox dropdown list. Cast the "header:column" dictionary as
        # a set to order the header names alphabetically
        for headerName in sorted(set(columns_dict.keys())):
            column_cbo1.insert(tix.END,headerName)
            column_cbo2.insert(tix.END,headerName)
            column_cbo3.insert(tix.END,headerName)           
        #.............................................................
   #
   #--------------------------------------------------------------
   
        
   # Create a label to display the number of rows returned from the HList's query
   screen_def["varRows"] = StringVar()
   lblRows = tix.Label(window, 
                       textvariable=screen_def["varRows"],
                       font = '-adobe-helvetica-bold-r-narrow--12-120')
   
   # Attach the menus appropriate for the window    
   attach_menus(screen_def)

  
   #--------------------------------------------------------------  
   #           Arrange all the widgets on the screen
   #
   window.tixHList.pack(expand=1,fill=tix.BOTH,
                             padx=10,pady=10,side=tix.TOP)
   
   win_buttons_frm.pack(side = tix.RIGHT, padx=5 )
   close_btn.pack(side=RIGHT,pady = 5)
   refresh_btn.pack(side=RIGHT)
   show_SQL_btn.pack(side=RIGHT)
   
   prog_buttons_frm.pack(side = tix.RIGHT, padx=5 )
   sqlplus_btn.pack(side=RIGHT)
   edit_btn.pack(side=RIGHT)
   
   sort_widgets_frm.pack(side = tix.RIGHT,padx=5)
   sort_lbl.pack(side = tix.LEFT)
   column_cbo1.pack(side = tix.LEFT)
   column_cbo2.pack(side = tix.LEFT)
   column_cbo3.pack(side = tix.LEFT)
   sort_btn.pack(side=tix.LEFT)
   clear_sort_btn.pack(side=tix.LEFT)
   lblRows.pack(side='left',pady=10,padx=5)
   #
   #--------------------------------------------------------------

   
#-------------------------------------------------------------------------
#           Define the functions called by the screen's buttons   
#-------------------------------------------------------------------------
def close_window(window): 
    window.destroy()

   
def refresh_display(screen_def):
    """
      Deletes the current contents of the window's Tix Scrolled HList
      and repopulates it by rerunning the window's query as defined
      in the window's screen definition
    """
    try:
      screen_def['hlist'].delete_all()
    except:
      pass
    if debug():
      logger.debug("query=",screen_def['query'])     
    displayed_query = display_window(screen_def)

     
def sort_display(screen_def, columns_dict, column1, column2, column3):
    """
      Sorts the results of the gScreens' SQL query that is defined
      in the gScreens "query" item. It simply alters the query's
      "order by" clause based upon the selections in the 3 sort
      combo box widgets.
    """
    #screen_def= getscreen_def(self.windowID)
    col_names=[]
    order_by=""
    # For each combo box widget, grab the Oracle column name 
    # corresponding to the header name displayed in the combo 
    # box's entry subwidget and add it to the col_names list.
    header=column1.entry.get()
    if header != '':
        col_names.append(columns_dict[header]) 
    header=column2.entry.get()
    if header != '':
        col_names.append(columns_dict[header]) 
    header=column3.entry.get()
    if header != '':
        col_names.append(columns_dict[header])
    if len(col_names) == 0:
        display_error("No Sort Selections","No sort citeria selected")
    # Build a string of comma separated Oracle 
    # column names from the col_names list then
    # replace the value for the place holder 
    #"var_order_by" in the gScreens' "query"  
    # with this string after removing the
    # trailing ",".
    while len(col_names) > 0:
        order_by=order_by + col_names.pop(0)+','
    if order_by != "":
        query = screen_def['query'].replace('var_order_by',order_by.strip(','))     
    else:
        query = screen_def['query'].replace('var_order_by',screen_def['order_by'])
        
    display_window(screen_def, query)

     
def clear_sort(column1,column2,column3):
    """
       Clears out the selections in the 3 sort combo box widgets and
      refreshes the HList data with the original "order by" clause
      as defined by the gScreens "order_by" item 
    """       
    column1.entry.config(state=NORMAL)
    column1.entry.delete(0,tix.END)
    column1.entry.config(state=DISABLED)
    
    column2.entry.config(state=NORMAL)
    column2.entry.delete(0,tix.END)
    column2.entry.config(state=DISABLED)
    
    column3.entry.config(state=NORMAL)
    column3.entry.delete(0,tix.END)
    column3.entry.config(state=DISABLED)
    refresh_display(screen_def)


def show_SQL(screen_def, query=None):
   """
       Displays the SQL query that is being executed to populate
       the Tix ScrolledHList of the designated screen
   """
   
   if debug:
      logger.debug('Editor source {}'.format(screen_def['name']))
      logger.debug(screen_def["title"])
   # Write the query to a text file that will opened by the editor   
   try: 
      outputFile=screen_def["outputFile"]
      f=open(outputFile,'w')
      if query != None:
         f.write(query.replace('\t',' '))
      else:
         query = screen_def['query'].replace('var_order_by',screen_def['order_by'])
         f.write(query.replace('\t',' ').replace('  ',' '))
      f.write("\n")  
      f.close()
      if debug:
         logger.debug (screens.editor)
      displayFile = "%s %s" % (screens.editor,outputFile)
      process = Popen(displayFile)
   except Exception as e: 
      if debug:
        logger.exception(str(e)) 
      display_error("show_sql ERROR", str(e))


#_______________________________________________________________________________  
#                                display_window
#_______________________________________________________________________________  
def display_window(screen_def, query=None):
   """
      Creates a window to display the HList if it doesn't already exist 
     and populates the HList with the results of the HList's query.
     Returns the query that it ran.
   """
   if debug:
      # Check to see if the ConnectionInfo attributes are set properly
      logger.debug('The connection object = {}'. \
                   format(ConnectionInfo.cx_Oracle_connection_object))
      logger.debug('The connect string = {}'. \
                   format(ConnectionInfo.Oracle_connect_string))
      logger.debug('The current DB = {}'.format(ConnectionInfo.current_db))

      
   db_connection = ConnectionInfo.cx_Oracle_connection_object  
   # Build the HList if it doesn't already exist
   try:
      screen_def['window'].deiconify()
   except:
      if debug:
         logger.debug('Building display for {}'.format(screen_def['name']))
      screen_def['window'] = tix.Toplevel(width=80)
      screen_def['window'].configure
      build_screen(screen_def)
   
   # Add the database to the HList's title 
   title='{} on {}'.format(screen_def['title'],ConnectionInfo.Oracle_version)
   screen_def['window'].title(title) 
   
   # Clear the current contents of the HList
   screen_def['hlist'].delete_all()
   if query == None: 
         # Get the fields that the SQL query is ordered by from the
         # screen's dictionary definition
         query = screen_def['query'].replace('var_order_by',screen_def['order_by'])   
   
   # Set the column width and get the number of columns to display
   screen_def['hlist'].column_width(0,chars=30)
   total_cols = len(screen_def['columns'])
   
   # Create a cursor and execute the HList's query
   try:
      cur = db_connection.cursor() 
      cur.execute(query) 
      # Step through the rows returned by the query and populate the HList
      i=0
      for row in cur:
         i = i+1
         screen_def['hlist'].add(i,itemtype=tix.TEXT,text=row[0])
         # Step through the columns of the row and insert the data
         for col_num in range(total_cols):
             screen_def['hlist'].item_create(i,col_num,itemtype=tix.TEXT,text=row[col_num])
       
      # Set the row count label to the number of rows returned by the query.
      screen_def['varRows'].set('Total Rows: {}'.format(cur.rowcount)) 

   except Exception as e:
      logger.exception(str(e))
      display_error('display_window Error',str(e))
      screen_def['window'].destroy()
      
   cur.close()
   # Return the SQL statement that was executed
   screens.displayed_query = query

#_______________________________________________________________________________    
#                                display_error  
#_______________________________________________________________________________  
def display_error(title, error_message):
    """
      Displays errors in a tkinter error message box
    """
    messagebox.showerror(title=title, message=error_message)


#_______________________________________________________________________________    
#                                  get_selections
#_______________________________________________________________________________  
def get_selections(screen_def, column_name ):
    """
       Returns the values for the designated column name from the rows
      that were selected in the window's hlist
    """
    if debug:
        logger.debug("Retrieving row selections from window {}".format(screen_def['hlist']))
    hlist = screen_def['hlist'] 
    #  Step through the selected rows and return a list of the column
    # values for the designated column name
    try:
        selected_rows = hlist.info_selection()
        if debug:
            logger.debug('Row selections = {}'.format(selected_rows))
        #  Step through the columns on the screen to find the
        # column number of the desired column name
        #  Recall that column[0] is an Oracle column name and
        # column[1] is its corresponding header name
        for i,column in enumerate(screen_def['columns']):
           if column[0].lower().find(column_name.lower()) == 0:
              column_number = i
        # To retrieve the value of a displayed column we must pass the
        # row number and column number to the hlist item_get function
        column_values = []
        for row_number in selected_rows:
            column_value = hlist.item_cget(row_number,column_number,'-text')  
            column_values.append(column_value.strip())

        if debug:
            logger.debug("Column values = {}".format(column_values))
            
        if len(column_values) == 0: 
            display_error("Selection ERROR","Nothing selected " )
            return None
        else:
            return column_values
    except Exception as e:
        logger.exception(str(e)) 
        display_error("Selection ERROR",str(e))
        return None


#_______________________________________________________________________________    
#                                  get_user_roles
#_______________________________________________________________________________  
def get_user_roles(screen_def):
   """
     Displays all the Oracle roles granted to the selected users
   """
   
   selected_users = get_selections(screen_def,'username')
   if debug:
      logger.debug('selected_users  = ')
      logger.debug((selected_users))
   # If there are selections, concatenate them into a comma
   # separated list 
   if selected_users != None: 
      user_names = "('" + "','".join(selected_users) + "')" 
      if debug:
         logger.debug(("user_names =" + user_names))
         
      # Build a query for all the selected users
      # that will be displayed in a user roles screen
      screen_def = screens.get_screen_def('UserRoles')
      if debug: 
         logger.debug("screen  = {}".format(screen_def['name']))
      screen_def['query'] = \
          """SELECT grantee,
            granted_role,
            admin_option,
            default_role
           FROM dba_role_privs
           WHERE  grantee IN  """ + user_names + """ 
           ORDER BY var_order_by
          """
       
      if debug:
         logger.debug("query = {}".format(screen_def['query']))
         
      # Set the title of the user roles screen and display the results of the 
      # query
      screen_def['title'] = 'Roles granted to selected users'
      display_window(screen_def)    
 

################################################################################  
#                                Menus
################################################################################  
#_______________________________________________________________________________  
#                                attach_menus
#_______________________________________________________________________________    
def attach_menus(screen_def):
    """
       Creates the menus that appear on the window
    """
    
    window = screen_def["window"]
    # Create the window's "menu bar" that all the 
    # dropdown menus will be attached to. 
    window.menu_bar = Menu(window)
    window.config(menu = window.menu_bar)
    # Attach the appropriate menus for the screen
    if screen_def["name"] == screens.main_window: 
       if debug:
          logger.debug("Building Main menus for screen {}". \
                        format(screen_def['name']))
       attach_database_menu(window.menu_bar)
       attach_sysutil_menu(window.menu_bar, screen_def)
       attach_users_menu(window.menu_bar,screen_def)       
    elif screen_def['name'] == 'UserList':       
       users_menu = Menu(window.menu_bar)    
       window.menu_bar.add_cascade(label="User Utilities",
                                   menu=users_menu)
       attach_usersutil_menu(users_menu, screen_def)
    elif screen_def['name'] == 'DBA_Tablespaces':
       tablespace_menu = Menu(window.menu_bar)    
       window.menu_bar.add_cascade(label="Tablespace Utilities",
                                   menu=tablespace_menu)
       attach_tblspc_util_menu(tablespace_menu, screen_def)

#_______________________________________________________________________________  
#                           attach_database_menu
#_______________________________________________________________________________    

def attach_database_menu(menu_bar):
    """
      Builds the database selection dropdown menu and adds it to the 
     menu bar. Selecting from the menu allows the user to switch to
     another database to login to.
    """   
    databases_menu = Menu(menu_bar)    
    menu_bar.add_cascade(label="Databases", menu=databases_menu)     
    for database in screens.getDBs():
        # If there is a "-" in database["db"] then it is 
        # a separator so just set the label option
        if database["db"].find('-') != -1: 
            databases_menu.add_command(label=database["db"])
        else:
            databases_menu.add_command(label=database["db"],
                                     command=lambda dbase=database["db"] : 
                                     switchDB(dbase))
            
#_______________________________________________________________________________  
#                               attach_sysutil_menu
#_______________________________________________________________________________      

def attach_sysutil_menu(menu_bar,screen_def):
    """
       Builds the system utilities dropdown menu of DBA_Tablespaces,
       DBA objects and DBA tools and adds it to the menu bar
    """    
    utilities_menu = Menu(menu_bar)    
    menu_bar.add_cascade(label="Utilities", menu=utilities_menu)     

    #--------------------------------------------------------------
    #         Create the Tablespace dropdown menu 
    #
    tablespaces_menu = Menu(utilities_menu)
    utilities_menu.add_cascade(label="Tablespaces" ,menu = tablespaces_menu)
    # Add menu items to the Tablespaces menu 
    tablespaces_menu.add_command(label="Dba_Tablespaces",
                                 command=lambda :
                                 display_window(screens.get_screen_def('DBA_Tablespaces')))
    attach_tblspc_util_menu(tablespaces_menu, screen_def)
    #--------------------------------------------------------------
    #         Create the DML locks dropdown menu 
    #
    DML_locks_menu = Menu(utilities_menu)
    utilities_menu.add_cascade(label="Locks" , menu = DML_locks_menu)
    DML_locks_menu.add_command(label="DML Locks",
                               command=lambda :
                               display_window(screens.get_screen_def('DML_Locks')))
    DML_locks_menu.add_command(label="Blocking Locks",
                               command=lambda :
                               display_window(screens.get_screen_def('BlockingLocks')))
     
    # Add the DBA Registry selection to the Utilities menu
    utilities_menu.add_command(label="DBA Registry",
                               command=lambda :
                               display_window(screens.get_screen_def('DBA_Registry')))

    #--------------------------------------------------------------
    #         Create the Events dropdown menu 
    #
    events_menu = Menu(utilities_menu)
    utilities_menu.add_cascade(label="Events" , menu = events_menu)
    events_menu.add_command(label="All System Events",
                            command=lambda :
                            display_window(screens.get_screen_def('SysEvents'))) 
    events_menu.add_command(label="System Events Percentages",
                            command=lambda :
                            display_window(screens.get_screen_def('SysEventsPercentages')))
    
    #--------------------------------------------------------------
    #         Create the Logins dropdown menu 
    #
    logins_menu = Menu(utilities_menu)
    utilities_menu.add_cascade(label="Logins" , menu =logins_menu)                         
    logins_menu.add_command(label="Failed Logins",
                            command=lambda :
                            display_window(screens.get_screen_def('FailedLogins')))                    
    logins_menu.add_command(label="Invalid Logins",
                            command=lambda :
                            display_window(screens.get_screen_def('InvalidLogins')))
    
    #--------------------------------------------------------------
    #         Create the Alert Log dropdown menu 
    #    
    alert_log_menu = Menu(utilities_menu)
    utilities_menu.add_cascade(label="Alert Log" , menu =alert_log_menu)
    #  The first parameter passed to the display_alert_log function is the
    # screen_def['name'] of either the alert messages or alert errors screen.
    alert_log_menu.add_command(label="Messages",
                               command=lambda :
                               display_alert_log('AlertLogMsgs',screen_def))                
    alert_log_menu.add_command(label="Errors",
                               command=lambda :
                               display_alert_log('AlertLogErrors',screen_def))
    
#_______________________________________________________________________________  
#                           attach_tblspc_util_menu
#_______________________________________________________________________________    
def attach_tblspc_util_menu(menu_base, screen_def):
    """
        Adds tablespace related options to the the designated menu. These options were
      broken out this way to allow them to be used on various menus on different
      screens.
    """    
    menu_base.add_command(label="Free Space",
                         command=lambda :
                         display_window(screens.get_screen_def('FreeSpace')))



#_______________________________________________________________________________  
#                                attach_users_menu
#_______________________________________________________________________________    
def attach_users_menu(menu_base, screen_def):
    """
       Builds the Users dropdown menu and adds it to the menu bar
    """    
    users_menu = Menu(menu_base)    
    menu_base.add_cascade(label="Users", menu=users_menu)     
                      
    users_menu.add_command(label="All Users",
                           command=lambda :
                           display_window(screens.get_screen_def('UserList')))
    
    attach_usersutil_menu(users_menu, screen_def)
    
#_______________________________________________________________________________  
#                                attach_usersutil_menu
#_______________________________________________________________________________    
def attach_usersutil_menu(menu_base, screen_def):  
    """
        Adds user related options to the the designated menu. These options were
      broken out this way to allow them to be used on various menus on different
      screens.
    """    
    menu_base.add_command(label="User Roles",
                        command=lambda : get_user_roles(screen_def))
#_______________________________________________________________________________  
#                                display_alert_log
#_______________________________________________________________________________    

def display_alert_log(alert_msg_type, screen_def):
    """
        Displays all messages or just error messages in the alert log.
      However many days are entered in the dialog box is how far back
      the alert log display will go. Decimal entries, such as 1.5 or
      even .042, are valid entries for the number of days.
      NOTE: .042 days is approximately 1 hour (60.48 minutes)
    """
    
    window = screen_def['window']
    title = screen_def['name']
    try:    
      days = simpledialog.askfloat(title, "Go back how many days?",
                                   parent=window,
                                   minvalue=0.00, maxvalue=360.0)
      if days is not None: 
         logscreen_def = screens.get_screen_def(alert_msg_type) 
         query = logscreen_def['query'].replace('"varDays',str(days))
         if debug:
             logger.debug('Alert log query = {}'.format(query))
         display_window(logscreen_def,query)
         
    except Exception as e:
        display_error("display_alert_log Error",str(e))
    


   
################################################################################  
#                                Main
################################################################################

if __name__ == "__main__":
   
  #  Set debug to True if you want to display print statements 
  # while debugging and log errors
  debug = True
  
  # Retrieve the screen definition for the 'Sessions' screen, let
  # the program know it will be the main window and bind the
  # screen's key word "window" to a tix toplevel object
  screen_def = screens.get_screen_def('Sessions')
  screens.main_window = screen_def['name']
  screen_def["window"] = tix.Tk()
  main_win = screen_def["window"]
  main_win.iconify()
  
  db_connection = None
  while not db_connection:
    #  Display the login dialog box, retrieve the database login connect 
    # string and wait for the dialog box to be destroyed 
    #  The login box is redidisplayed until the user enters
    # a valid Oracle login without errors or hits the Cancel button
    user_entries = ConnectionInfo(main_win ) 
    main_win.wait_window(user_entries.top)
    connect_string =  user_entries.return_value()
    if debug:
      logger.debug("The returned connect string={}".format(connect_string))
    # If the user didn't hit Cancel try to login to Oracle
    if connect_string != "Cancel": 
       db_connection = login(connect_string)
    else:
       db_connection = connect_string
       
  # If the user didn't hit Cancel, display the main window
  if db_connection == "Cancel":
     main_win.destroy()
  else:
     build_screen(screen_def,True)
     screens.displayed_query = display_window(screen_def)
     mainloop()
 
     
