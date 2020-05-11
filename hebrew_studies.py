"""
   This app started as a simple tool to format URLs into hyperlinks to place inside
  Anki Hebrew flashcards and grew into a database of Hebrew related webpages then
  into a database of Hebrew audio files for the study of Hebrew using the
  grammar book "Ha-yesod The Fundamentals of Hebrew" by Uveeler and Bronznick.

"""

import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import PhotoImage
import tkinter.ttk as ttk
import tkinter.tix as tix
import sqlite3
import webbrowser
import urllib
import os
import re
import pygame

# Set screen constants
WIN_HEIGHT = 650
WIN_WIDTH = 780
BG_COLOR = '#669999'
FG_COLOR = '#ffffcc'
FG_RECORDS = '#ccffff'
FG_A_MEMBER = '#99ff99'
FG_NOT_A_MEMBER = '#800040'

# Widget identifiers
AUDIO_MGR_AUDIO_CBO = 'AudioMgr Audio combobox'
AUDIO_MGR_CATEGORY_CBO = 'AudioMgr Category combobox'
AUDIO_MGR_HEBREW_TEXT = 'AudioMgr Hebrew Text'
AUDIO_MGR_LESSONS_CBO = 'AudioMgr Lessons combobox'
AUDIO_MGR_SEARCH = 'AudioMgr Search box'
URL_MGR_CREATE_HYPERLINK = 'UrlMgr Create Hyperlink'
URL_MGR_HYPERLINK = 'UrlMgr Hyperlink Entry box'
WEB_MGR_CREATE_HYPERLINK = 'WebMgr Create Hyperlink'
WEB_MGR_TOPICS_CBO = 'WebMgr Topics combobox'
WEB_MGR_SEARCH = 'WebMgr Search Box'

# Define the path to the Hebrew SQLite3 database and
# the folder containing the Hebrew audio files
HEBREW_DB = '.\\hebrew_studies.db'
HEBREW_MEDIA = '.\\Media\\'


# Connect to the SQLite3 Hebrew database
SQLITE_DB = sqlite3.connect(HEBREW_DB)
#  Set queries to return values as row objects rather
# than the default tuples.
SQLITE_DB.row_factory = sqlite3.Row
SQL = SQLITE_DB.cursor()


#  The following module globals are assigned
# their referents in the main function.
text_editor_menu = ''
tool_tip = ''
url_mgr = ''
web_mgr = ''
audio_mgr = ''

#_____________________________________
#               main
#_____________________________________
def main():
    """
       Configures the screen, creates the text_editor_menu
     and tool_tip widgets and launches the major
     elements of the application, i.e. UrlMgr, WebMgr
     and AudioMgr.
    """

    #  Make the following accessible to url_mgr, web_mgr
    # and audio_mgr since they all use tool_tips and a
    # text_editor_menu and url_mgr, web_mgr and audio_mgr
    # all manipulate one or more of each other's variables
    # or tkinter widgets.
    global text_editor_menu
    global tool_tip
    global url_mgr
    global web_mgr
    global audio_mgr

    # Configure the screen
    main_win = tix.Tk()
    main_win.geometry(("%dx%d" % (WIN_WIDTH, WIN_HEIGHT)))
    main_win.title('Hebrew Studies')
    main_win.option_add('*Font', 'Helvetica 12')
    main_win.configure(background=BG_COLOR)

    #------- text editor pop-up menu
    text_editor_menu = tk.Menu(main_win,
                               bg=BG_COLOR, fg=FG_COLOR,
                               tearoff=0)
    text_editor_menu.add_command(label="Cut")
    text_editor_menu.add_command(label="Copy")
    text_editor_menu.add_command(label="Paste")
    text_editor_menu.add_command(label="Select All")
    text_editor_menu.add_command(label="Clear")

    #------- tool_tip
    balloon_options = 'font -adobe-helvetica-italic-r-narrow--12-120' + \
                      ' background  #ffff99'
    tool_tip = tix.Balloon(main_win, options=balloon_options)

    # Launch the application
    url_mgr = UrlMgr(main_win)
    web_mgr = WebMgr(main_win)
    audio_mgr = AudioMgr(main_win)

    main_win.mainloop()


#####################################################################
#           Define the functions ahared by the classes
#####################################################################

#_____________________________________
#            clear_text
#_____________________________________
def clear_text(widget):
    """
        Deletes all the text displayed in the widget
       that envoked the pop_up text editor.
    """

    widget.delete(0, 'end')
    print(f'Widget = {widget.whoami}')
    #  If the text being cleared is either the Lessons or Category
    # comboboxes change the color of their labels to indicate that
    # the currently displayed audio file is not a member of a blank
    # lesson or category.
    if widget.whoami == AUDIO_MGR_LESSONS_CBO:
        audio_mgr.lessons_lbl.configure(fg=FG_NOT_A_MEMBER)
    elif widget.whoami == AUDIO_MGR_CATEGORY_CBO:
        audio_mgr.category_lbl.configure(fg=FG_NOT_A_MEMBER)

#_____________________________________
#         contains_text
#_____________________________________
def contains_text(string):
    """
cate     Verifies a string contains one or more alpha-numeric
    characters whether the text is English or Hebrew
    """
    return bool(re.search('[a-zA-Z0-9]+', string)) or \
           bool(re.search('[\u0590-\u05FF]+', string)) or \
           bool(re.search('[\uFB1D-\uFB4F]+', string))

#_____________________________________
#         create_hyperlink
#_____________________________________
def create_hyperlink(event=None):
    """
        Uses the topic and the URL to create an
       HTML formatted hyperlink which can be copied and
       pasted into an Anki flashcard, webpage, etc.
    """
    # Get the widget that triggered the event
    # and its displayed or selected text for
    # the topic and URL.
    widget = event.widget

    if widget.whoami == URL_MGR_CREATE_HYPERLINK:
        url = url_mgr.url.get()
        topic = url_mgr.topic.get().strip()
        topic = topic.capitalize()
    elif widget.whoami == WEB_MGR_CREATE_HYPERLINK:
        url = web_mgr.db_url.get()
        selected_topic = web_mgr.selected_topic.get()
        topic = selected_topic.split('|')
        topic = topic[0].strip().capitalize()
    if contains_text(topic) and contains_text(url):
        url_mgr.hyperlink.set(f'<A HREF="{url}">{topic}</A>')
    else:
        title = 'Insufficient Data'
        msg = ' The Topic and URL fields must contain text\n' +\
              'in order to create a hyperlink.'
        messagebox.showerror(title=title, message=msg)

#_____________________________________
#        display_text_editor_menu
#_____________________________________
def display_text_editor_menu(event):
    """
     Displays the text editor pop-up menu at the widget
    that invoked it and performs the selected action
    on its text.
    """
    global text_editor_menu

    widget = event.widget
    widget.focus_set()
    text_editor_menu.entryconfigure("Cut",
                                    command=lambda: widget.event_generate("<<Cut>>"))
    text_editor_menu.entryconfigure("Copy",
                                    command=lambda: widget.event_generate("<<Copy>>"))
    text_editor_menu.entryconfigure("Paste",
                                    command=lambda: widget.event_generate("<<Paste>>"))
    text_editor_menu.entryconfigure("Select All",
                                    command=lambda: widget.event_generate("<Control-a>"))
    text_editor_menu.entryconfigure("Clear", command=lambda: clear_text(widget))

    text_editor_menu.tk.call("tk_popup", text_editor_menu, event.x_root, event.y_root)

#_____________________________________
#           display_sql_error
#_____________________________________
def display_sql_error(err, sql_stmt):
    """
        Displays the SQL statement and the error it generated.
    """
    title = 'SQLite3 Error'
    msg = ('SQL Error Message: \n'
           f'      {err.args[0]} \n\n'
           f'In SQL Statement:\n {sql_stmt}')
    messagebox.showerror(title=title, message=msg)

   

#_____________________________________
#           search_audio_table
#_____________________________________
def search_audio_table(event=None):
    """
      Queries the database table HEBREW_AUDIO for all the
     records matching the text in the triggering widget and
     populates the Audio list combobox with the results.
    """

    # Get the widget that triggered the event
    widget = event.widget

    #  Check for any selected text in the widget and use
    # that text for the search rather than the full text
    # displayed in the widget.
    if widget.selection_present():
        search = widget.selection_get()
        widget.selection_clear()
    else:
        search = widget.get()
        
    #  If the widget is a combobox it may contain
    # text followed by a '|' and its ID.
    #  Just get the text and remove all leading
    # and following spaces
    if bool(re.match(r'.* \|.*', search)):
        print('found |')
        selection = search.split('|')
        search = selection[0].strip()

    #  Make sure the widget actually contains text before querying
    # the database.
    #  If the triggering widget is the WebMgr Topics combobox set
    # the text in the Audio search entry box to the the text being
    # searched for.
    if contains_text(search):
        if widget.whoami == WEB_MGR_TOPICS_CBO:
            audio_mgr.audio_search.set(search)
        print(f'Searching DB for {search}')
        query = ('SELECT english, audio_id'
                 ' FROM hebrew_audio'
                 f' WHERE english LIKE "%{search}%"'
                 f' OR hebrew LIKE "%{search}%"'
                 '  ORDER BY english;')
        print(query)
        try:
            SQL.execute(query)
            audio_mgr.active_audio_query = query
            audio_list = ['{english}      | {audio_id}'.format(**row)
                          for row in SQL.fetchall()]
            if len(audio_list) > 0:
                audio_mgr.active_audio_query = query
                audio_mgr.audio_list_cbo['values'] = audio_list

                audio_mgr.audio_list_cbo.current(0)
                audio_mgr.audio_list_cbo.event_generate("<<ComboboxSelected>>")
            else:
                title = 'No Records Found'
                msg = f"Query returned no results matching\n '{search}'"
                messagebox.showerror(title=title, message=msg)
        except sqlite3.Error as err:
            display_sql_error(err, query)
    else:
        title = 'Nothing to Search'
        msg = f'No text entered in the \n{widget.whoami}.'
        messagebox.showerror(title=title, message=msg)

#_____________________________________
#       search_webpage_table
#_____________________________________
def search_webpage_table(event=None):
    """
      Queries the database table WEBPAGE for all the values in the
     TOPIC column that match the text entered in the triggering
     widget and populates the Topics combobox with the results.
    """

    #  Check for any selected text in the widget that
    # triggered the event and use that text for the
    # search rather than than the full text displayed
    # in the widget.
    widget = event.widget
    if widget.selection_present():
        search = widget.selection_get()
        widget.selection_clear()
    else:
        search = widget.get()
        search = search.split('|')[0].strip()

    print(f'>>> Searching for {search}')
    #  Make sure the widget actually contains text before querying
    # the database.
    #  If the triggering widget is the AudioMgr Topics combobox set
    # the text in the WebMgr search entry box to the the text being
    # searched for.
    if contains_text(search):
        if widget.whoami == AUDIO_MGR_AUDIO_CBO:
            web_mgr.webpage_search.set(search)
        query = ("SELECT topic, url_id"
                 "  FROM webpage "
                 f" WHERE topic LIKE '%{search}%'"
                 "  ORDER BY topic;")
        print(query)
        try:
            SQL.execute(query)
            topics = ['{topic}      | {url_id}'.format(**row)
                      for row in SQL.fetchall()]
            if len(topics) > 0:
                #  Populate the WebMgr Topics combobox, display the count
                # of the total records found and set the Topics combobox
                # to the first item in the topics list
                topics_cbo = web_mgr.topics_cbo
                topics_cbo['values'] = topics
                topics_cbo.set(topics[0])
                topics_cbo.event_generate("<<ComboboxSelected>>")
            else:
                title = 'No Records Found'
                msg = f"Query returned no results matching\n '{search}'"
                messagebox.showerror(title=title, message=msg)
                web_mgr.search_webpage_entry.delete(0, 'end')
        except sqlite3.Error as err:
            display_sql_error(err, query)
    else:
        title = 'Nothing to search.'
        msg = f'No text found in \n{widget.whoami}'
        messagebox.showerror(title=title, message=msg)

#_____________________________________
#           search_website
#_____________________________________
def search_website(event=None):
    """
       Searches different websites depending on the letter hit in
      conjunction with the <Control> key for the audio or English
      translation of the selected Hebrew word or phrase. The webiste
      Doitinhebrew.com can also be searched for English words and
      phrases to get their Hebrew translations.
    """

    #  Get the widget that triggered the event and its displayed text.
    #  The widget's whoami attribute identifies the widget that triggered
    # the event and determines how to process the text before passing
    # it to the website.
    #  The event's keysym identifies the letter that was hit in
    # combination with the Control key. The letter is associated
    # with the specific website to search.

    widget = event.widget
    search_string = widget.get()
    search_source = widget.whoami
    website_id = event.keysym

    #  Step through the website options dictionary and
    # find the webpage corresponding to the control key
    # character entered
    for item in audio_mgr.website_options.items():
        if item[1][0] == website_id:
            webpage = item[1][1]


    #  If the text being searched for on the Doitinhebrew website
    # is not Hebrew then switch to its English webpage
    #if website_id == 'd' and search_source != AUDIO_MGR_HEBREW_TEXT:
    if website_id == 'd' and bool(re.search('[a-zA-Z]+', search_string)):
        webpage = ('https://www.doitinhebrew.com/Translate/'
                   'Default.aspx?l1=en&l2=iw&s=1&txt=')


    # Process the text before passing it to the url
    #
    print(f'>>>>> search_string = {search_string} website ID = {website_id}')
    print(contains_text(search_string))
    if contains_text(search_string):
        if search_source == AUDIO_MGR_HEBREW_TEXT:
            # Strip off the gender if found.
            # It will be the last letter 'ז' or  'נ' preceeded
            # by a space. Remember, Hebrew is read the opposite
            # direction of English, i.e. from left to right.
            last_letter = len(search_string) -1
            if search_string[last_letter] == 'ז' and \
               search_string[last_letter - 1] == ' ':
                search_string = search_string.rstrip('ז')
            elif search_string[last_letter] == 'נ' and \
                 search_string[last_letter - 1] == ' ':
                search_string = search_string.rstrip('נ')

            #  Some Hebrew entries also contain the plural form
            # but only the singular form will be searched for
            search_string = audio_mgr.remove_plural(search_string)
        else:
            if widget.selection_present():
                search_string = widget.selection_get()
                print(f'selected text = {search_string}')
                widget.selection_clear()
            if bool(re.match(r'.* \|.*', search_string)):
                string_list = search_string.split('|')
                
        if audio_mgr.is_hebrew(search_string):
            search_string = audio_mgr.remove_niqqud(search_string) 

        #  Launch the selected webpage
        #  No search string is passed to the Lexilogos
        # websites. Don't know how.
        if website_id in ('k', 'l'):
            webbrowser.open_new(webpage)
        elif search_string:
            search_string = search_string.strip()
            webpage = webpage + search_string
            if website_id == 'f':
                webpage = webpage + '/he/'
            print(f"Searching {webpage} \n")
            webbrowser.open_new(webpage)
    else:
        title = 'Nothing to search'
        msg = f'No text found in {search_source}'
        messagebox.showerror(title=title, message=msg)

#####################################################################
#                        Define the Classes
#####################################################################

#====================================================================
#                           UrlMgr
#====================================================================
class UrlMgr():
    """
       Adds URL's to the database and creates hyperlinks for
      inserting into Anki flashcards
    """
    def __init__(self, main):

        #==================== Create the widgets ====================
        #------- hyperlink frame
        self.link_frame = tk.Frame(main, bg=BG_COLOR,
                                   relief=tk.GROOVE, borderwidth=3)
        #------- topic entry box
        self.topic = tk.StringVar()
        self.topic_entry = tk.Entry(self.link_frame, width=36,
                                    textvariable=self.topic)
        self.topic_entry.whoami = 'Topic Entry box'

        tool_tip.bind_widget(self.topic_entry,
                             balloonmsg='Subject matter of the URL contents')

        #------- URL entry box
        self.url = tk.StringVar()
        self.url_entry = tk.Entry(self.link_frame, width=46,
                                  textvariable=self.url)
        self.url_entry.whoami = 'URLMgr URL Entry box'

        tool_tip.bind_widget(self.url_entry,
                             balloonmsg='Right click for Copy/Paste Menu')

        #------- hyperlink entry box
        self.hyperlink = tk.StringVar()
        self.hyperlink_entry = tk.Entry(self.link_frame, width=30,
                                        textvariable=self.hyperlink)
        self.hyperlink_entry.whoami = URL_MGR_HYPERLINK

        tool_tip.bind_widget(self.hyperlink_entry,
                             balloonmsg='Right click for Copy/Paste Menu')

        #------- decode url button
        self.decode_url_btn = tk.Button(self.link_frame, text="Decode % URL",
                                        fg=FG_COLOR, bg=BG_COLOR,
                                        command=self.decode_url_percent)
        tip = ('Translates the percent encoded \n'
               'Hebrew into Hebrew characters')
        tool_tip.bind_widget(self.decode_url_btn,
                             balloonmsg=tip)

        #------- create_hyperlink button
        self.create_hyperlink_btn = tk.Button(self.link_frame, text="Create Hyperlink",
                                              fg=FG_COLOR, bg=BG_COLOR)
        self.create_hyperlink_btn.whoami = URL_MGR_CREATE_HYPERLINK
        self.create_hyperlink_btn.bind("<Button-1><ButtonRelease-1>",
                                       create_hyperlink)

        tip = (' Formats a hyperlink from the Topic and URL that can\n'
               ' be inserted into a webpage, Anki flashcard, etc.')
        tool_tip.bind_widget(self.create_hyperlink_btn, balloonmsg=tip)

        #------- add_url_to_db button
        self.add_url_to_db_btn = tk.Button(self.link_frame, text="Add URL to DB",
                                           fg=FG_COLOR, bg=BG_COLOR,
                                           command=self.add_url_to_db)

        tip = 'Inserts the Topic and URL into\n' + \
              'the WEBPAGE database table.'
        tool_tip.bind_widget(self.add_url_to_db_btn, balloonmsg=tip)



        # Bind all the Entry widgets to the cut-and-paste pop-up menu
        self.url_entry.bind_class("Entry", "<Button-3><ButtonRelease-3>",
                                  display_text_editor_menu)


        #=========== Arrange the widgets on the screen ==============
        # Link frame
        self.link_frame.place(relx=.025, rely=0.025,
                              relheight=.35, relwidth=.95,
                              anchor=tk.NW)

        tk.Label(main, text=' URLs ', fg=FG_COLOR, bg=BG_COLOR)\
                 .place(relx=.06, rely=0.01, anchor=tk.NW)

        # Topic entry box
        tk.Label(self.link_frame, text='Topic',
                 fg=FG_COLOR, bg=BG_COLOR).place(x=10, y=10)
        self.topic_entry.place(x=10, y=35, relwidth=.675)

        # URL entry box
        tk.Label(self.link_frame, text='URL',
                 fg=FG_COLOR, bg=BG_COLOR).place(x=10, y=60)
        self.url_entry.place(x=10, y=87, relwidth=.975)

        # Hyperlink entry box
        tk.Label(self.link_frame, text='Hyperlink',
                 fg=FG_COLOR, bg=BG_COLOR).place(x=10, y=110)
        self.hyperlink_entry.place(x=10, y=135, relwidth=.975)

        # Decode_url button
        self.decode_url_btn.place(relx=.245, y=175)

        # create_hyperlink button
        self.create_hyperlink_btn.place(relx=.421, y=175)

        # Add_URL_to_DB button
        self.add_url_to_db_btn.place(relx=.606, y=175)

    #_____________________________________
    #            add_url_to_db
    #_____________________________________
    def add_url_to_db(self):
        """
           Gets the displayed website name, topic and URL
          and inserts the data into the database WEBPAGE table.
        """
        #  Make sure the necessary data, i.e. the topic and URL,
        # are entered before proceeding
        topic = self.topic.get()
        url = self.url.get()
        if contains_text(topic) and \
           contains_text(url):
            try:
                sql_stmt = ('INSERT INTO webpage(topic, url)'
                            f' VALUES("{topic}","{url}");')
                print(sql_stmt)
                SQL.execute(sql_stmt)
                SQLITE_DB.commit()
                title = 'URL Added to Database'
                msg = f"Successfully executed following SQL:\n {sql_stmt}"
                messagebox.showinfo(title=title, message=msg)
            except sqlite3.Error as err:
                display_sql_error(err, sql_stmt)
        else:
            title = 'Insufficient Data'
            msg = 'The URL and Topic fields must contain data.'
            messagebox.showerror(title=title, message=msg)


    #_____________________________________
    #            decode_url_percent
    #_____________________________________
    def decode_url_percent(self):
        """
           Decodes the Hebrew characters in an URL that are percent encoded
          so that they appear as Hebrew characters.
        """
        decoded_url = urllib.parse.unquote(self.url.get())
        self.url.set(decoded_url)


    #-------------------------------------
    #            get_websites
    #-------------------------------------
    def get_websites(self):
        """
           Retrieves the names of the websites from the database table
          WEBSITES and populates the Websites combo box.
        """
        try:
            query = 'SELECT name FROM website ORDER BY name;'
            SQL.execute(query)
            return [row['name'] for row in SQL.fetchall()]
        except sqlite3.Error as err:
            display_sql_error(err, query)


#====================================================================
#                           WebMgr
#====================================================================
class WebMgr():
    """
       Searches and displays webpages saved to the
      database. Allows the modification and deletion
      of webpages, the linking of webpages to audio
      files displayed in the audio manager and the
      creation of hyperlinks from the displayed
      webpages.
    """
    def __init__(self, main):
        #==================== Create the widgets ====================
        #------- webpages frame
        self.web_frame = tk.Frame(main, bg=BG_COLOR,
                                  relief=tk.GROOVE, borderwidth=3)

        #------- database URL entry box
        # This widget has to be created before the
        #topics combobox which attemps to populate it
        self.db_url = tk.StringVar()
        self.db_url_entry = tk.Entry(self.web_frame, width=70,
                                     textvariable=self.db_url,
                                     cursor="hand2")
        self.db_url_entry.whoami = 'Webpage URL Entry box'

        # Whenever the URL is clicked bring up it's webpage
        self.db_url_entry.bind("<Button-1>", self.display_webpage)

        tool_tip.bind_widget(self.db_url_entry,
                             balloonmsg='Click to display webpage')

        #------- Total topics label
        self.total_topics = tk.StringVar()
        self.total_topics_lbl = tk.Label(self.web_frame, anchor="e",
                                         textvariable=self.total_topics,
                                         fg=FG_RECORDS, bg=BG_COLOR)

        #------- topics combobox
        self.topics = self.get_topics()
        self.selected_topic = tk.StringVar()
        self.topic_index = tk.IntVar()
        self.topics_cbo = ttk.Combobox(self.web_frame, width=70,
                                       textvariable=self.selected_topic,
                                       values=self.topics)
        self.topics_cbo.whoami = WEB_MGR_TOPICS_CBO

        #  Whenever a topic is selected retrieve
        # the appropriate url
        #  Mouse right-click searches the database for
        # the corresponding Hebrew audio
        #  <Control d> searches the Doitinhebrew website
        # for the displayed English text
        self.topics_cbo.bind('<<ComboboxSelected>>', self.get_url)
        self.topics_cbo.bind("<Button-3><ButtonRelease-3>",
                             search_audio_table)
        self.topics_cbo.bind("<Control d>", search_website)

        #  Whenever the topics combo box is populated set
        # the displayed topic to the first item in the list
        # and generate a combo selected event
        self.topics_cbo.current(0)
        self.topics_cbo.event_generate("<<ComboboxSelected>>")

        tip = '  Select item to display URL\n' +\
              '  Mouse <Right-click> to search for relevant audio\n' +\
              'files displayed below in the Audio frame.\n' + \
              '  <Control-d> to search Doitinhebrew.com for the\n' + \
              'Hebrew translation of the displayed English.'
        tool_tip.bind_widget(self.topics_cbo, balloonmsg=tip)

        #------- refresh_topics button
        self.refresh_icon = PhotoImage(file="refresh5.png")
        self.refresh_btn = tk.Button(self.web_frame,
                                     fg=FG_COLOR, bg=BG_COLOR,
                                     image=self.refresh_icon,
                                     command=self.refresh_topics)
        tip = 'Queries database to display all topics'
        tool_tip.bind_widget(self.refresh_btn, balloonmsg=tip)

        #------- search_webpage entry box
        self.webpage_search = tk.StringVar()
        self.search_webpage_entry = tk.Entry(self.web_frame, width=50,
                                             textvariable=self.webpage_search)
        self.search_webpage_entry.whoami = WEB_MGR_SEARCH

        self.search_webpage_entry.bind('<Return>', search_webpage_table)

        #  If  <Control d> is entered, search the Doitinhebrew
        # website for the displayed Hebrew text
        self.search_webpage_entry.bind("<Control d>", search_website)


        tip = (' Hit <ENTER> to query database topics for search text.\n '
               ' <Control-d> to search Doitinhebrew.com for the\n'
               'Hebrew translation of the English search text.')
        tool_tip.bind_widget(self.search_webpage_entry, balloonmsg=tip)

        #------- create_hyperlink button
        self.create_hyperlink_btn = tk.Button(self.web_frame,
                                              text="Create Hyperlink",
                                              fg=FG_COLOR, bg=BG_COLOR)

        self.create_hyperlink_btn.whoami = WEB_MGR_CREATE_HYPERLINK
        self.create_hyperlink_btn.bind("<Button-1><ButtonRelease-1>",
                                       create_hyperlink)

        tip = (' Formats a hyperlink from the Topic and URL that \n'
               'can be inserted into a webpage, Anki flashcard, etc..\n'
               'Displayed above in the URL frame.')

        tool_tip.bind_widget(self.create_hyperlink_btn,
                             balloonmsg=tip)

        #------- execute_webpage_option option menu
        self.webpage_options = tk.StringVar()
        self.webpage_options.set("Options")
        self.execute_webpage_option_optmnu = \
                tk.OptionMenu(self.web_frame,
                              self.webpage_options,
                              "Save changes to displayed webpage",
                              "Delete displayed webpage",
                              "Link webpage to displayed Hebrew audio",
                              "Remove webpage link to displayed Hebrew audio",
                              command=self.execute_webpage_option)
        self.execute_webpage_option_optmnu.configure(fg=FG_COLOR, bg=BG_COLOR,
                                                     activebackground=BG_COLOR)
        self.execute_webpage_option_optmnu["menu"].config(fg=FG_COLOR, bg=BG_COLOR)

        tip = 'Updates the TOPIC and URL columns in the \n' +\
              'WEBPAGE table to the edited values.'


        #=========== Arrange the widgets on the screen ==============
        # Web frame
        self.web_frame.place(relx=.025, rely=0.4125,
                             relheight=.225, relwidth=.95,
                             anchor=tk.NW)

        tk.Label(main, text=' Webpages ', fg=FG_COLOR, bg=BG_COLOR)\
                 .place(relx=.06, rely=0.395, anchor=tk.NW)

        # Topics combo box
        tk.Label(self.web_frame, text='Topic    |   Link ID',
                 fg=FG_COLOR, bg=BG_COLOR).place(x=15, y=10)
        self.topics_cbo.place(x=15, y=35, relwidth=.42)

        # Total topics label
        self.total_topics_lbl.place(relx=.24, y=10, relwidth=.2)

        # Refresh topics button
        self.refresh_btn.place(relx=.45, y=35)

        # DB URL entry box
        tk.Label(self.web_frame, text='URL',
                 fg=FG_COLOR, bg=BG_COLOR).place(x=15, y=70)
        self.db_url_entry.place(x=15, y=95, relwidth=.77)

        # Search_webpage entry box
        tk.Label(self.web_frame, text='Search',
                 fg=FG_COLOR, bg=BG_COLOR).place(relx=.54, y=10)
        self.search_webpage_entry.place(relx=.54, y=35, relwidth=.25)

        # Create_hyperlink button
        self.create_hyperlink_btn.place(relx=.81, y=90)

        # execute_webpage_option option menu
        tk.Label(self.web_frame, text='Webpage',
                 fg=FG_COLOR, bg=BG_COLOR).place(relx=.825, y=4)
        self.execute_webpage_option_optmnu.place(relx=.81, y=28)


    #_____________________________________
    #           display_webpage
    #_____________________________________
    def display_webpage(self, event=None):
        """
        Envokes the web browser to display the URL displayed in the
        URL entry box
        """
        webpage = self.db_url.get()
        if webpage:
            webbrowser.open_new(webpage)
        else:
            msg = "No URL entry"
            messagebox.showinfo('No Web Page', msg)


    #_____________________________________
    #        execute_webpage_option
    #_____________________________________
    def execute_webpage_option(self, option):
        """
           Does one of the following:
           Updates the databse WEBPAGE table to whatever values
          that have been edited in the Topics combobox and URL
          entry box.
           Deletes the webpage from the database.
           Links the displayed webpage to the audio
          displayed in Audio frame.
           Unlinks the displayed webpage from the audio
          displayed in Audio frame.
        """
        self.webpage_options.set("Options")
        current_topic = self.topics_cbo.get()
        url = self.db_url.get()
        selection = current_topic.split('|')
        topic = selection[0].strip()
        url_id = selection[1].strip()
        reset_index = True
        try:
            if option.startswith('Save'):
                sql_stmt = (" UPDATE webpage"
                            f" SET topic = '{topic}',"
                            f"  url = '{url}' "
                            f" WHERE url_id = {url_id};")
                SQL.execute(sql_stmt)
                SQLITE_DB.commit()
                title = 'Database Successfully Updated'
                msg = f'SQL = {sql_stmt}'
                messagebox.showinfo(title=title, message=msg)
            elif option.startswith('Delete'):
                msg = f"Delete '{topic} | URL_ID {url_id}'?"
                if messagebox.askyesno('Verify', msg, icon='warning'):
                    sql_stmt = ('DELETE FROM webpage'
                                f'  WHERE url_id = {url_id};')
                    SQL.execute(sql_stmt)
                    SQLITE_DB.commit()
                    title = f"'{topic} | {url_id}' Successfully Deleted"
                    msg = f'SQL = {sql_stmt}'
                    messagebox.showinfo(title=title, message=msg)
            elif option.startswith('Link'):
                current_audio = audio_mgr.audio_list_cbo.get().split('|')
                audio_id = current_audio[1].strip()
                sql_stmt = ("INSERT INTO audio_url(audio_id, url_id) "
                            f" VALUES('{audio_id}','{url_id}');")
                SQL.execute(sql_stmt)
                SQLITE_DB.commit()
                reset_index = False
            elif option.startswith('Remove'):
                current_audio = audio_mgr.audio_list_cbo.get().split('|')
                audio_id = current_audio[1].strip()
                sql_stmt = (" DELETE FROM audio_url"
                            f" WHERE audio_id = '{audio_id}'"
                            f"  AND url_id = '{url_id}';")
                SQL.execute(sql_stmt)
                SQLITE_DB.commit()
                reset_index = False
            if reset_index:
                current_index = self.topic_index.get()
                print(f'>>> Current index={current_index}')
                self.refresh_topics()
                self.topics_cbo.current(current_index)
                self.topics_cbo.event_generate("<<ComboboxSelected>>")
        except sqlite3.Error as err:
            display_sql_error(err, sql_stmt)


    #_____________________________________
    #            get_topics
    #_____________________________________
    def get_topics(self):
        """
           Retrieves the values from the TOPIC and URL_ID columns
          of the WEBPAGE table to populate the Topics combo box.
        """
        try:
            query = ('SELECT topic, url_id '
                     ' FROM webpage '
                     ' ORDER BY topic;')
            SQL.execute(query)
            return ['{topic}      | {url_id}'.format(**row)
                    for row in SQL.fetchall()]
        except sqlite3.Error as err:
            display_sql_error(err, query)


    #_____________________________________
    #            get_url
    #_____________________________________
    def get_url(self, event=None):
        """
          Retrieves the values of the URL and WEBSITE columns
         from the WEBPAGE table for the specified url_id in the
         Topics combobox and displays it in the URL entry box.
        """

        widget = event.widget
        selection = widget.get().split('|')
        url_id = selection[1].strip()
        self.topic_index.set(widget.current())
        query = ('SELECT url'
                 ' FROM webpage'
                 f' WHERE url_id = {url_id};')

        print('Executing url query:')
        print(query)
        try:
            SQL.execute(query)
            row = SQL.fetchone()
            self.db_url.set(row['url'])
            #self.db_website.set(row['website_id'])
            print(f'Query returned : url={self.db_url.get()}')
            current = self.topics_cbo.current() + 1
            self.total_topics.set(f'#{current} of  {len(self.topics_cbo["values"])}')
        except sqlite3.Error as err:
            display_sql_error(err, query)

    #_____________________________________
    #           refresh_topics
    #_____________________________________
    def refresh_topics(self):
        """
          Queries the database for all the values in the TOPIC column
         of the WEBPAGE table and populates the Topics combobox with
         the results.
        """
        print('Refreshing topics')
        #  Clear out the current entries in the Webpage widgets before
        # refreshing the data
        self.db_url_entry.delete(0, 'end')
        self.topics_cbo.set('')
        self.search_webpage_entry.delete(0, 'end')

        # Refresh and set topics to the first item in the list
        self.topics_cbo['values'] = self.get_topics()
        self.topics_cbo.current(0)
        #self.total_topics.set(f'Total {len(self.topics_cbo["values"])}')
        self.topics_cbo.event_generate("<<ComboboxSelected>>")


#====================================================================
#                           AudioMgr
#====================================================================
class AudioMgr():
    """
        Adds Hebrew audio files and their corresponding Hebrew
       text and English translations to the database.
    """
    def __init__(self, main):
        #  Intialize the Pygame mixer to
        # play the Hebrew audio files.
        pygame.mixer.init()

        #  Track the query that generated
        # the current audio list displayed
        # in the audio list combobox
        self.active_audio_query = tk.StringVar()

        #  Dictionary of searchable websites and the control key character
        # that invokes them. Adding to this dictionary will automatically
        # update the Website menu and the event bindings for the Hebrew_text
        # widget but not the display_webpage_menu function which has to be
        # edited maually.
        # Couldn't figure out that part.
        self.website_options = \
          {'Bing':('b', 'https://www.bing.com/translator/?from=he&to=en&text='),
           'DoitinHebrew':('d', ('https://www.doitinhebrew.com/Translate/'
                                 'Default.aspx?kb=IL%20Hebrew%20Phonetic&l1=iw&'
                                 'l2=en&txt=')),
           'Forvo':('f', 'https://he.forvo.com/search/'),
           'Google':('g', ('https://translate.google.com/'
                           '#view=home&op=translate&sl=iw&tl=en&text=')),
           'Lexilogos':('l', ('https://www.lexilogos.com/'
                              'english/hebrew_dictionary.htm')),
           'Milog':('m', 'https://milog.co.il/'),
           'Morfix':('o', 'https://www.morfix.co.il/'),
           'Pealim':('p', 'https://www.pealim.com/search/?q='),
           'Reverso':('r', 'https://dictionary.reverso.net/hebrew-english/'),
           'Hebrew Keyboard':('k', 'https://www.lexilogos.com/keyboard/hebrew.htm')
          }

        #==================== Create the widgets ====================
        #------- audio frame
        self.audio_frame = tk.Frame(main, bg=BG_COLOR, relief=tk.GROOVE,
                                    borderwidth=3)

        #------- website pop-up menu
        self.website_menu = tk.Menu(self.audio_frame,
                                    bg=BG_COLOR, fg=FG_COLOR,
                                    tearoff=0)
        # Build the menu from the website_options dictionary
        for key in self.website_options.keys():
            self.website_menu.add_command(label=f"{key}")

        #------- Hebrew text entry box
        self.hebrew = tk.StringVar()
        self.hebrew_text = tk.Entry(self.audio_frame, width=75,
                                    textvariable=self.hebrew)
        self.hebrew_text.config(font=("Arial", 18))
        self.hebrew_text.whoami = AUDIO_MGR_HEBREW_TEXT

        #  Bind control key combinations to search for the
        # displayed Hebrew text on the following websites:
        #  <Control d> for Doitinhebrew    (doitinhebrew.com)
        #  <Control f> for Forvo           (he.forvo.com)
        #  <Control h> for Hebrew keyboard (lexilogos.com/keyboard)
        #  <Control l> for Lexilogos       (lexilogos.com)
        #  <Control m> for Milog           (milog.co.il)
        #  <Control o> for Morfix          (morfix.co.il)
        #  <Control p> for Pealim          (pealim.com)

        #  Add the Hebrew_text event bindings using the website_options
        # dictionary
        for item in self.website_options.items():
            self.hebrew_text.bind(f"<Control-{item[1][0]}>", search_website)

        self.hebrew_text.bind("<Double-Button-1>", self.display_webpage_menu)

        tip = ('Mouse <Right-click> for text editor menu\n'
               '  Search the following websites for the displayed Hebrew:\n'
               'Mouse <Double-Left-click> for website menu\n'
               '                         or\n'
               '<Control-b> to search Bing.com.\n'
               '<Control-d> to search Doitinhebrew.com.\n'
               '<Control-f> to search Forvo.com\n'
               '<Control-g> to search Google.com\n'
               '<Control-k> for Hebrew keyboard\n'
               '<Control-l> to search Lexilogos.com\n'
               '<Control-m> to search Milog.co.il\n'
               '<Control-o> to search Morfix.co.il\n'
               '<Control-p> to seach Pealim.com ')
        tool_tip.bind_widget(self.hebrew_text, balloonmsg=tip)


        #------- audio file entry box
        self.audio_file = tk.StringVar()
        self.audio_file_entry = tk.Entry(self.audio_frame, width=75,
                                         textvariable=self.audio_file,
                                         cursor="hand2")
        self.audio_file_entry.whoami = 'AudioMgr Audio File'

        # Whenever the audio file entry is clicked play the audio
        self.audio_file_entry.bind("<Button-1>", self.play_audio)

        #  Whenever a return is hit in the audio file entry box
        # pull up a file dialog box in order to choose an audio
        # file from the HEBREW_MEDIA folder.
        self.audio_file_entry.bind("<Return>", self.select_audio_file)

        tip = (' Click file to play audio. \n'
               ' Hit <ENTER> to invoke a file dialog box\n'
               'for selecting audio file.')
        tool_tip.bind_widget(self.audio_file_entry,
                             balloonmsg=tip)

        #------- New English entry box
        self.new_english = tk.StringVar()
        self.new_english_entry = tk.Entry(self.audio_frame, width=25,
                                          textvariable=self.new_english)
        self.new_english_entry.whoami = 'AudioMgr New English Entry'

        #  Whenever the new_english entry box is clicked clear out any text
        # that might be in the Hebrew entry box and the audio file entry box.
        # Also, clear the current selection in the Audio list combobox.
        self.new_english_entry.bind("<Button-1>", self.clear_current_audio)


        tool_tip.bind_widget(self.new_english_entry,
                             balloonmsg=(' Enter English for new audio file\n'
                                         'then Hebrew and Audio File'))

        #------- Lessons combobox
        self.lessons = self.get_lessons()
        self.lesson = tk.StringVar()
        self.lessons_cbo = ttk.Combobox(self.audio_frame, width=30,
                                        textvariable=self.lesson,
                                        values=self.lessons)
        self.lessons_cbo.whoami = AUDIO_MGR_LESSONS_CBO

        #  Whenever a lesson is selected retrieve
        # the Hebrew word and audio file name
        self.lessons_cbo.bind('<<ComboboxSelected>>', self.get_lesson)

        self.lessons_cbo.bind('<Return>', self.get_lesson)
        self.lessons_cbo.bind("<Button-3><ButtonRelease-3>",
                              self.display_lesson_webpage)

        tip = ("  Select lesson to get members or enter text \n"
               "to create a new lesson.\n"
               "  Mouse <Right-click> for lesson's webpage.")

        self.lessons_lbl = tk.Label(self.audio_frame, text='Lesson',
                                    fg=FG_NOT_A_MEMBER, bg=BG_COLOR)
        tool_tip.bind_widget(self.lessons_cbo, balloonmsg=tip)

        #------- lesson audio optionMenu
        self.lesson_options = tk.StringVar()
        self.lesson_options.set("Options")
        self.lesson_audio_optmnu = tk.OptionMenu(self.audio_frame, self.lesson_options,
                                                 "Add displayed audio to Lesson",
                                                 "Remove displayed audio from Lesson",
                                                 command=self.execute_lesson_option)
        self.lesson_audio_optmnu.configure(fg=FG_COLOR, bg=BG_COLOR,
                                           activebackground=BG_COLOR)
        self.lesson_audio_optmnu["menu"].config(fg=FG_COLOR, bg=BG_COLOR)

        #------- category combobox
        self.categories = self.get_categories()
        self.category = tk.StringVar()
        self.category_cbo = ttk.Combobox(self.audio_frame, width=30,
                                         textvariable=self.category,
                                         values=self.categories)
        self.category_cbo.whoami = AUDIO_MGR_CATEGORY_CBO

        self.category_cbo.bind('<<ComboboxSelected>>', self.get_category_members)
        self.category_cbo.bind('<Return>', self.get_category_members)
        self.category_cbo.bind("<Button-3><ButtonRelease-3>", display_text_editor_menu)

        tip = ('Select category to get category members\n'
               'or enter text to create a new category.\n')

        tool_tip.bind_widget(self.category_cbo, balloonmsg=tip)

        #------- Category label
        self.category_lbl = tk.Label(self.audio_frame, text='Category',
                                     fg=FG_NOT_A_MEMBER, bg=BG_COLOR)

        #------- Total words label
        self.total_words = tk.StringVar()
        self.total_words_lbl = tk.Label(self.audio_frame,
                                        textvariable=self.total_words,
                                        fg=FG_RECORDS, bg=BG_COLOR)

        #<h2 id="audiocbo">		Audio list combobox</h2>
      
        #------- Audio list combobox
        self.audio_list = self.get_audio_list()
        self.selected_audio = tk.StringVar()
        self.audio_index = tk.IntVar()
        self.audio_list_cbo = ttk.Combobox(self.audio_frame, width=30,
                                           textvariable=self.selected_audio,
                                           values=self.audio_list)
        self.audio_list_cbo.whoami = 'AudioMgr Audio combobox'

        #  Whenever an item in the audio list combobox is selected,
        # retrieve the Hebrew text and audio file name from the
        # database and populate the Hebrew and audio file entry boxes.
        #  Any webpages that are linked to the item automatically
        # populate the Topics combobox in the Webpages frame.
        self.audio_list_cbo.bind('<<ComboboxSelected>>', self.get_hebrew)

        #  Set the displayed text in the audio list combobox
        # to the first item in the audio list and trigger
        # a ComboboxSelected event which will populate the
        # Hebrew and audio file entry boxes.
        self.audio_list_cbo.current(0)
        self.audio_list_cbo.event_generate("<<ComboboxSelected>>")

        #  Bind the widget to control key combinationa that will
        # search the Doitinhebrew website for the Hebrew translation
        # of the displayed English text and the database WEBPAGE
        # table's TOPICS column for matching English text.
        self.audio_list_cbo.bind("<Control d>", search_website)
        self.audio_list_cbo.bind('<Control w>', search_webpage_table)
        #  Whenever the mouse's right button is clicked step through
        # the audio list and play its associated audio file.
        self.audio_list_cbo.bind("<Button-3><ButtonRelease-3>",
                                 self.step_through_audio)

        tip = ("Select item to display Hebrew text and audio file.\n"
               "<Control w> searches for webpage topics in the database that match\n"
               "                     all the audio text or just the highlighted portion \n"
               "                     of the text. Displayed above in the Webpages frame.\n"
               "<Control -d> searches DoitinHebrew.com for the displayed English.\n"
               "<Right-click> mouse steps through the dropdown list and plays the \n"
               "                     associated audio file.")
        tool_tip.bind_widget(self.audio_list_cbo, balloonmsg=tip)


        #------- refresh_audio button
        self.refresh_icon = PhotoImage(file="refresh5.png")
        self.refresh_audio_btn = tk.Button(self.audio_frame, image=self.refresh_icon,
                                           fg=FG_COLOR, bg=BG_COLOR,
                                           command=self.refresh_audio)
        tool_tip.bind_widget(self.refresh_audio_btn,
                             balloonmsg=' Retrieves all audio files \nfrom the database.')



        #------- audio_search entry box
        self.audio_search = tk.StringVar()
        self.search_audio_entry = tk.Entry(self.audio_frame, width=25,
                                           textvariable=self.audio_search)
        self.search_audio_entry.whoami = 'AudioMgr Search box'

        self.search_audio_entry.bind('<Return>', search_audio_table)

        self.search_audio_entry.bind("<Control d>", search_website)

        tip = ('Hit <ENTER> to query database for text.\n '
               '<Control-d> to search Doitinhebrew.com.')
        tool_tip.bind_widget(self.search_audio_entry, balloonmsg=tip)


        #------- audio options menu
        self.audio_options = tk.StringVar()
        self.audio_options.set("Options")
        self.audio_options_optmnu = tk.OptionMenu(self.audio_frame, self.audio_options,
                                                  "Save changes to displayed Audio ",
                                                  "Delete displayed Audio ",
                                                  command=self.execute_audio_option)
        self.audio_options_optmnu.configure(fg=FG_COLOR, bg=BG_COLOR,
                                            activebackground=BG_COLOR)
        self.audio_options_optmnu["menu"].config(fg=FG_COLOR, bg=BG_COLOR)

        #------- add_audio_to_db button
        self.add_audio_to_db_btn = tk.Button(self.audio_frame,
                                             text="Add New Audio\n to DB",
                                             fg=FG_COLOR, bg=BG_COLOR,
                                             command=self.add_audio_to_db)
        tip = (' Adds the newly entered audio data into the  \n'
               'database. \n'
               ' NOTE: Also adds it to the displayed Lesson.')
        tool_tip.bind_widget(self.add_audio_to_db_btn,
                             balloonmsg=tip)

        #------- category audio option menu
        self.category_options = tk.StringVar()
        self.category_options.set("Options")
        self.category_audio_optmnu = tk.OptionMenu(self.audio_frame, self.category_options,
                                                   "Add displayed audio to Category",
                                                   "Remove displayed audio from Category",
                                                   command=self.execute_category_option)
        self.category_audio_optmnu.configure(fg=FG_COLOR, bg=BG_COLOR,
                                             activebackground=BG_COLOR)
        self.category_audio_optmnu["menu"].config(fg=FG_COLOR, bg=BG_COLOR)


        #=========== Arrange the widgets on the screen ==============
        # Audio frame
        self.audio_frame.place(relx=.025, rely=0.675,
                               relheight=.3, relwidth=.95,
                               anchor=tk.NW)

        tk.Label(main, text=' Audio ', fg=FG_COLOR, bg=BG_COLOR)\
                 .place(relx=.06, rely=0.656, anchor=tk.NW)

        # Hebrew text entry
        tk.Label(self.audio_frame, text='Hebrew',
                 fg=FG_COLOR, bg=BG_COLOR).place(x=15, y=68)
        self.hebrew_text.place(x=15, y=93, relwidth=.35)

        # Audio_file entry box
        tk.Label(self.audio_frame, text='Audio File',
                 fg=FG_COLOR, bg=BG_COLOR).place(relx=.4, y=68)
        self.audio_file_entry.place(relx=.4, y=93, relwidth=.425)

        # audio options menu
        tk.Label(self.audio_frame, text='Audio',
                 fg=FG_COLOR, bg=BG_COLOR).place(relx=.88, y=61)
        self.audio_options_optmnu.place(relx=.8475, y=86)

        # Audio list combo box
        tk.Label(self.audio_frame, text='Audio  |   Audio ID',
                 fg=FG_COLOR, bg=BG_COLOR).place(x=15, y=10)
        self.total_words_lbl.place(relx=.225, y=10)
        self.audio_list_cbo.place(x=15, y=35, relwidth=.3)

        # Refresh audio button
        self.refresh_audio_btn.place(relx=.33, y=35)

        # Search_audio entry box
        tk.Label(self.audio_frame, text='Search',
                 fg=FG_COLOR, bg=BG_COLOR).place(relx=.4, y=10)
        self.search_audio_entry.place(relx=.4, y=35, relwidth=.2)

        # lessons combo box
        self.lessons_lbl.place(relx=.625, y=10)
        self.lessons_cbo.place(relx=.625, y=35, relwidth=.2)

        # add_remove_audio_to_lesson  button
        tk.Label(self.audio_frame, text='Audio / Lesson',
                 fg=FG_COLOR, bg=BG_COLOR).place(relx=.84, y=3)
        self.lesson_audio_optmnu.place(relx=.8475, y=28)

        # Category combobox
        self.category_lbl.place(relx=.57, y=130)
        self.category_cbo.place(relx=.57, y=155, relwidth=.25)

        # Add_remove_category option menu
        tk.Label(self.audio_frame, text='Audio / Category',
                 fg=FG_COLOR, bg=BG_COLOR).place(relx=.825, y=124)
        self.category_audio_optmnu.place(relx=.845, y=150)

        # New English entry box
        tk.Label(self.audio_frame, text='English for New Audio',
                 fg=FG_COLOR, bg=BG_COLOR).place(x=15, y=130)
        self.new_english_entry.place(x=15, y=155, relwidth=.25)

        # Add_audio_to_DB button
        self.add_audio_to_db_btn.place(relx=.29, y=135)

    #_____________________________________
    #       add_audio_to_db
    #_____________________________________
    def add_audio_to_db(self):
        """
         Grabs the values in the new English, Hebrew and audio file
        entry boxes and inserts them in the HEBREW_AUDIO table.
         Also adds the audio to the whatever lesson ,if any, is
        displayed in the Lesson combobox.
        """
        #  Retrieve the contents of all the widgets whose data are
        # necessary to populate the HEBREW_AUDIO table and insure
        # that they actually contain text.
        english_text = self.new_english.get()
        hebrew_text = self.hebrew.get()
        audio_file_name = self.audio_file.get()
        lesson_name = self.lesson.get()

        if contains_text(hebrew_text) and contains_text(english_text) \
                                      and contains_text(audio_file_name):
            try:
                #  If the Lesson widget doesn't contain text then simply
                # insert the necessary data into the HEBREW_AUDIO table
                # otherwise process the Lesson name in order to add its
                # lesson ID to the INSERT statement.

                if not contains_text(lesson_name):
                    sql_stmt = \
                      ('INSERT INTO hebrew_audio(english, hebrew, audio_file)'
                       f' VALUES("{english_text}", "{hebrew_text}", "{audio_file_name}");')
                else:
                    #  If the lesson name isn't in the LESSON table
                    # it must be a new lesson so add it. In any event,
                    # get the lesson's lesson ID.
                    sql_stmt = ("SELECT lesson_id"
                                " FROM lesson"
                                f" WHERE name ='{lesson_name}';")
                    SQL.execute(sql_stmt)
                    row = SQL.fetchone()
                    if row is None:
                        sql_stmt = ("INSERT INTO lesson(name)"
                                    f"  VALUES('{lesson_name}');")
                        SQL.execute(sql_stmt)
                        SQLITE_DB.commit()
                        sql_stmt = ("SELECT lesson_id"
                                    " FROM lesson"
                                    f" WHERE name ='{lesson_name}';")
                        SQL.execute(sql_stmt)
                        row = SQL.fetchone()
                        #  Since a new lesson was created add it
                        # to the Lesson dropdown list.
                        self.lessons_cbo['values'] = self.get_lessons()
                    lesson_id = row['lesson_id']
                    sql_stmt = \
                      ('INSERT INTO hebrew_audio(english, hebrew, audio_file, lesson_id)'
                       f' VALUES("{english_text}", "{hebrew_text}", "{audio_file_name}",'
                       f'{lesson_id} );')
                print(sql_stmt)
                SQL.execute(sql_stmt)
                SQLITE_DB.commit()
                title = 'Audio Data Added to Database'
                msg = f"Successfully executed the following SQL:\n {sql_stmt}"
                messagebox.showinfo(title=title, message=msg)
                #  Refresh the audio list so that the newly
                # added audio will appear in the list.
                #  Set the currently audio to the new audio.
                self.refresh_audio(self.active_audio_query)
                for i, audio in enumerate(self.audio_list_cbo['values']):
                    audio_item = audio.split('|')
                    audio_text = audio_item[0].strip()
                    if audio_text == english_text:
                        self.audio_list_cbo.current(i)
                self.audio_list_cbo.event_generate("<<ComboboxSelected>>")
            except sqlite3.Error as err:
                display_sql_error(err, sql_stmt)
        else:
            title = 'Insufficient Data'
            msg = ('The English for New Audio, Hebrew and '
                   'Audio File fields must contain data.')
            messagebox.showerror(title=title, message=msg)

    #_____________________________________
    #       clear_current_audio
    #_____________________________________
    def clear_current_audio(self, event=None):
        """
           Clears out any text that might be in the Hebrew and
          audio file entry boxes and the current selection in
          the Audio list combobox. This clears all fields in
          preparation for creating a new entry to insert into
          the database HEBREW_AUDIO table.
        """
        self.hebrew_text.delete(0, 'end')
        self.audio_file_entry.delete(0, 'end')
        self.audio_list_cbo.set('')

    #_____________________________________
    #       display_lesson_webpage
    #_____________________________________
    def display_lesson_webpage(self, event=None):
        """
          Envokes the web browser to display the webpage
         of the lesson displayed in the Lesson combobox.
        """
        print(f'lesson = {self.lesson.get()}')

        webpage = self.lesson.get()
        if webpage:
            webpage = HEBREW_MEDIA + webpage.replace(' ', '_') +'.html'
            if os.path.exists(webpage):
                print(f'webpage={webpage}')
                webbrowser.open_new(webpage)
            else:
                msg = f'Webpage NOT found:\n {webpage}.'
                messagebox.showinfo('No Web Page', msg)
        else:
            msg = "No URL entry"
            messagebox.showinfo('No Web Page', msg)

    #_____________________________________
    #        display_webpage_menu
    #_____________________________________
    def display_webpage_menu(self, event):
        """
         Displays the webpage pop-up menu at the widget
        that invoked it and launches the selected webpage.
        """

        widget = event.widget
        widget.focus_set()

        #  NOTE: Tried doing this in a loop stepping through the website_options
        # dictionary but the only webpage that would come up was the last one in
        # the list regardless of what webpage that was selected. Even using the
        # same ctrl_key variable name and reassigning its value for each webpage
        # did the same thing so I had to use a different ctrl_key variable name
        # for each page. Have no idea what's going on here.

        bing_key = f'<Control-{self.website_options["Bing"][0]}>'
        self.website_menu.entryconfigure("Bing",
                                         command=lambda: widget.event_generate(bing_key))

        doit_key = f'<Control-{self.website_options["DoitinHebrew"][0]}>'
        self.website_menu.entryconfigure("DoitinHebrew",
                                         command=lambda: widget.event_generate(doit_key))

        forvo_key = f'<Control-{self.website_options["Forvo"][0]}>'
        self.website_menu.entryconfigure("Forvo",
                                         command=lambda: widget.event_generate(forvo_key))

        google_key = f'<Control-{self.website_options["Google"][0]}>'
        self.website_menu.entryconfigure("Google",
                                         command=lambda: widget.event_generate(google_key))

        lexi_key = f'<Control-{self.website_options["Lexilogos"][0]}>'
        self.website_menu.entryconfigure("Lexilogos",
                                         command=lambda: widget.event_generate(lexi_key))

        milog_key = f'<Control-{self.website_options["Milog"][0]}>'
        self.website_menu.entryconfigure("Milog",
                                         command=lambda: widget.event_generate(milog_key))

        morfix_key = f'<Control-{self.website_options["Morfix"][0]}>'
        self.website_menu.entryconfigure("Morfix",
                                         command=lambda: widget.event_generate(morfix_key))

        pealim_key = f'<Control-{self.website_options["Pealim"][0]}>'
        self.website_menu.entryconfigure("Pealim",
                                         command=lambda: widget.event_generate(pealim_key))

        reverso_key = f'<Control-{self.website_options["Reverso"][0]}>'
        self.website_menu.entryconfigure("Reverso",
                                         command=lambda: widget.event_generate(reverso_key))

        keybd_key = f'<Control-{self.website_options["Hebrew Keyboard"][0]}>'
        self.website_menu.entryconfigure("Hebrew Keyboard",
                                         command=lambda: widget.event_generate(keybd_key))


        self.website_menu.tk.call("tk_popup", self.website_menu, event.x_root, event.y_root)

    #_____________________________________
    #       execute_audio_option
    #_____________________________________
    def execute_audio_option(self, option):
        """
          Depending on the option selected updates the HEBREW_AUDIO table to
         reflect whatever has been edited  in the Audio portion of the Audio
         list combox, the Hebrew and audio_file entry boxes for the displayed
         Audio ID or removes the audio file data from the database.
        """

        self.audio_options.set("Options")
        selected_audio = self.selected_audio.get()
        try:
            if   '|' not in selected_audio:
                title = 'No Audio Selected'
                msg = (' Nothing selected in the '
                       'Audio | Audio ID combo box.')
                messagebox.showerror(title=title, message=msg)
            else:
                selection = selected_audio.split('|')
                english = selection[0].strip()
                audio_id = selection[1].strip()
                hebrew = self.hebrew_text.get()
                audio_file = self.audio_file_entry.get()
                if option.startswith('Save'):
                    sql_stmt = (" UPDATE hebrew_audio "
                                f"  SET english = '{english}',  hebrew = '{hebrew}',"
                                f"    audio_file = '{audio_file}'"
                                f" WHERE audio_id = {audio_id} ;")
                    SQL.execute(sql_stmt)
                    SQLITE_DB.commit()
                    title = f'AUDIO_ID {audio_id} Successfully Updated'
                    msg = f'Executed SQL:\n {sql_stmt}'
                    messagebox.showinfo(title=title, message=msg)
                elif option.startswith('Delete'):
                    msg = f"Delete '{english}  AUDIO_ID {audio_id}'?"
                    if messagebox.askyesno('Verify', msg, icon='warning'):
                        sql_stmt = ('DELETE FROM hebrew_audio '
                                    f'  WHERE audio_id = {audio_id};')
                        SQL.execute(sql_stmt)
                        SQLITE_DB.commit()
                        title = f'{english} AUDIO_ID {audio_id} Successfully Deleted'
                        msg = f"Executed SQL:\n {sql_stmt}"
                        messagebox.showinfo(title=title, message=msg)
                #  Grab the index of the currently selected item in the Audio list combobox.
                #  Using the combobox's current() function after text has been edited in
                # the combobox returns -1 so use the audio_index variable which was created
                # to solve that problem. Refresh the combobox so that its dropdown list
                # reflects the database changes and set the combobox back to where it was.
                # If an item was deleted then the item below it will be displayed.
                current_index = self.audio_index.get()
                print('========================================================')
                print('Index of {current_index} in query \n{self.active_audio_query}')
                self.refresh_audio(self.active_audio_query)
                self.audio_list_cbo.current(current_index)

                max_words = len(self.audio_list_cbo['values'])

                self.audio_list_cbo.event_generate("<<ComboboxSelected>>")
        except sqlite3.Error as err:
            display_sql_error(err, sql_stmt)

    #_____________________________________
    #    execute_category_option
    #_____________________________________
    def execute_category_option(self, option):
        """
           Adds or removes the displayed Audio ID from the category
          displayed in the Category combobox. An Audio ID
          can be a member of multiple categories.
        """

        #  Before proceeding make sure an audio has been selected
        # and the category combobox contains text that was either
        # selected or manually entered to create a new category.
        #  Any selected audio will have the format
        #       'text | audio id number'

        self.category_options.set("Options")
        selected_audio = self.selected_audio.get()
        category_name = self.category.get()
        if  '|' not in selected_audio:
            title = 'No Audio Selected'
            msg = 'Nothing selected in the English | Audio ID combo box.'
            messagebox.showerror(title=title, message=msg)
        elif category_name == '':
            title = 'No Category Entered'
            msg = 'Nothing selected or entered in the Category combo box.'
            messagebox.showerror(title=title, message=msg)
        elif option.startswith('Remove') and \
                 self.category_lbl["foreground"] == FG_NOT_A_MEMBER:
            title = 'Removal Unnecessary.'
            msg = f"Category '{category_name}' doesn't include Audio '{selected_audio}'."
            messagebox.showerror(title=title, message=msg)
        else:
            selection = selected_audio.split('|')
            print(selection)
            english = selection[0].strip()
            audio_id = selection[1].strip()
            category_table = category_name.replace(' ', '_')
            if option.startswith('Remove'):
                try:
                    sql_stmt = (f'DELETE FROM {category_table} '
                                f'  WHERE audio_id = {audio_id};')
                    SQL.execute(sql_stmt)
                    self.category_cbo['values'] = self.get_categories()
                    self.category_lbl.configure(fg=FG_NOT_A_MEMBER)
                    title = 'Database Successfully Updated'
                    msg = (f"Deleted '{english}' AUDIO_ID {audio_id}"
                           " from category: {category_table}")
                    messagebox.showinfo(title=title, message=msg)
                except sqlite3.Error as err:
                    display_sql_error(err, sql_stmt)
            elif option.startswith('Add'):
                #  If the category table does not exist create it since
                # it must be a new category. Add the new category's name
                # to the databse CATEGORY table which is a list of all
                # the category tables.
                try:
                    try:
                        sql_stmt = f'INSERT INTO {category_table} VALUES({audio_id});'
                        SQL.execute(sql_stmt)
                        SQLITE_DB.commit()
                    except sqlite3.OperationalError as err:
                        if err.args[0].find('no such table') > -1:
                            create_table = (f'CREATE TABLE {category_table} '
                                            ' (audio_id INTEGER PRIMARY KEY,'
                                            '  FOREIGN KEY (audio_id)'
                                            '  REFERENCES hebrew_audio(audio_id));')

                            print(create_table)
                            SQL.execute(create_table)
                            SQL.execute(f"INSERT INTO category VALUES('category_table');")
                            SQL.execute(sql_stmt)
                            SQLITE_DB.commit()
                except sqlite3.Error as err:
                    display_sql_error(err, sql_stmt)
                else:
                    title = 'Database Successfully Updated'
                    msg = (f"Added '{english}' AUDIO_ID {audio_id}"
                           f" to category: {category_table}")
                    messagebox.showinfo(title=title, message=msg)
                    self.category_cbo['values'] = self.get_categories()
                    self.category_lbl.configure(fg=FG_A_MEMBER)

    #_____________________________________
    #    execute_lesson_option
    #_____________________________________
    def execute_lesson_option(self, option):
        """
           Adds or removes whatever audio file that is selected in
          the Audio list combobox from the lesson displayed in the
          Lesson combobox.
           Since this app was originally written for studying just
          one book, i.e.
                 Ha-yesod
                 The Fundamentals of Hebrew
                       by Uveeler and Bronznick
          a Hebrew word can be in only one lesson referenced by the
          it's LESSON_ID column. So actually, the lesson is added to
          the audio and not vice versa.
        """

        #  Make sure an audio file has been selected.
        #  Any selected audio will have the format
        #       'text | audio id number'
        #  Make sure the lesson combobox contains text
        # and the selected audio is already included in
        # the lesson if it is to be removed from the lesson.

        self.lesson_options.set("Options")
        lesson_name = self.lesson.get()
        selected_audio = self.selected_audio.get()
        if   '|' not in selected_audio:
            title = 'No Audio Selected'
            msg = 'Nothing selected in the English | Audio ID combo box.'
            messagebox.showerror(title=title, message=msg)
        elif lesson_name == '':
            title = 'No Lesson Entered'
            msg = 'Nothing entered or selected in the Lesson combo box.'
            messagebox.showerror(title=title, message=msg)
        elif option.startswith('Remove') and \
                self.lessons_lbl["foreground"] == FG_NOT_A_MEMBER:
            title = 'Removal Unnecessary.'
            msg = f"Lesson '{lesson_name}' doesn't include Audio '{selected_audio}'."
            messagebox.showerror(title=title, message=msg)
        else:
            selection = selected_audio.split('|')
            english = selection[0].strip()
            audio_id = selection[1].strip()
            try:
                if option.startswith('Remove'):
                    sql_stmt = ("UPDATE hebrew_audio"
                                " SET lesson_id = NULL"
                                f"  WHERE audio_id = '{audio_id}';")
                elif option.startswith('Add'):
                    #  If the lesson isn't in the
                    # LESSON table, add it.
                    sql_stmt = ("Select lesson_id"
                                " FROM lesson"
                                f" WHERE name = '{lesson_name}';")
                    SQL.execute(sql_stmt)
                    if SQL.fetchone() is None:
                        sql_stmt = ("INSERT INTO lesson(name)"
                                    f" VALUES('{lesson_name}');")
                        SQL.execute(sql_stmt)
                        SQLITE_DB.commit()
                    sql_stmt = ("UPDATE hebrew_audio"
                                "  SET lesson_id = "
                                "   (SELECT lesson_id"
                                "    FROM lesson"
                                f"   WHERE name ='{lesson_name}') "
                                f"WHERE audio_id = {audio_id};")
                print(sql_stmt)
                SQL.execute(sql_stmt)
                SQLITE_DB.commit()
                title = 'Database Successfully Updated'
                if option.startswith('Add'):
                    msg = (f"Added '{english}' AUDIO_ID {audio_id} "
                           f"to Lesson '{lesson_name}'")
                    self.lessons_lbl.configure(fg=FG_A_MEMBER)
                elif option.startswith('Remove'):
                    msg = (f"Removed '{english}' AUDIO_ID {audio_id} "
                           f"from Lesson '{lesson_name}'")
                    self.lessons_lbl.configure(fg=FG_NOT_A_MEMBER)
                messagebox.showinfo(title=title, message=msg)

                #  If a new lesson was created, this will add it
                # to the Lesson dropdown list.
                self.lessons_cbo['values'] = self.get_lessons()
            except sqlite3.Error as err:
                display_sql_error(err, sql_stmt)

    #_____________________________________
    #       get_associated_webpages
    #_____________________________________
    def get_associated_webpages(self, audio_keywords, audio_id):
        """
            Retrieves the URL IDs from the AUDIO_URL table that are
           associated with the AUDIO_ID of the English keyword or
           phrase displayed in the Audio combobox
        """
        query = ("SELECT topic, url_id "
                 "FROM webpage"
                 " WHERE url_id IN"
                 "      (SELECT url_id"
                 "       FROM audio_url"
                 f"      WHERE audio_id = '{audio_id}')"
                 " ORDER BY topic;")
        print(query)
        try:
            SQL.execute(query)
            topics = ['{topic}      | {url_id}'.format(**row)
                      for row in SQL.fetchall()]
            print(f"Associated topics = {topics}")
            if len(topics) > 0:
                web_mgr.topics_cbo['values'] = topics
                web_mgr.topics_cbo.set(topics[0])
                web_mgr.topics_cbo.set('')
                web_mgr.db_url_entry.delete(0, 'end')
                web_mgr.topics_cbo.set(topics[0])
                web_mgr.topics_cbo.event_generate("<<ComboboxSelected>>")

                web_mgr.search_webpage_entry.delete(0, 'end')
                web_mgr.webpage_search.set(f"{audio_keywords}")
        except sqlite3.Error as err:
            display_sql_error(err, query)

    #_____________________________________
    #         get_audio_list
    #_____________________________________
    def get_audio_list(self, active_query=None, event=None):
        """
            Queries the ENGLISH and AUDIO_ID columns of the database
           table HEBREW_AUDIO to populate the Audio list combo box.
        """

        if active_query:
            query = active_query
        else:
            query = ('SELECT english, audio_id '
                     ' FROM hebrew_audio '
                     ' ORDER BY english;')
        try:
            SQL.execute(query)
            self.active_audio_query = query
            return ['{english}      | {audio_id}'.format(**row)
                    for row in SQL.fetchall()]
        except sqlite3.Error as err:
            display_sql_error(err, query)

    #_____________________________________
    #           get_categories
    #_____________________________________
    def get_categories(self):
        """
           Retrieves the values from the NAME column of the
          CATEGORY table to populate the category combo box.
        """

        sql_stmt = \
        """
        SELECT name
          FROM category
          ORDER BY name;
        """
        try:
            SQL.execute(sql_stmt)
            return [row['name'] for row in SQL.fetchall()]
        except sqlite3.Error as err:
            display_sql_error(err, sql_stmt)

    #_____________________________________
    #        get_category_members
    #_____________________________________
    def get_category_members(self, event=None):
        """
            When a category is selected in the category combobox, retieves a
         list of all the AUDIO_IDs in the associated category table and populates
         the Audio list combo box with the results.
        """

        # Get the widget that triggered the event and its displayed text.
        widget = event.widget
        category = widget.selection_get()

        #  The category names displayed in the category combox have
        # corresponding table names in the database,
        #   However, since table names contain underscores instead of
        # spaces replace the spaces with underscores in the category
        # table name.
        category_table = category.replace(' ', '_')
        query = ("SELECT english, ha.audio_id"
                 f" FROM hebrew_audio ha, {category_table} ct"
                 "   WHERE ha.audio_id = ct.audio_id"
                 "   ORDER BY english;")
        print(query)
        self.search_audio_entry.delete(0, 'end')
        try:
            SQL.execute(query)
            self.active_audio_query = query
            audio_list = ['{english}      | {audio_id}'.format(**row)
                          for row in SQL.fetchall()]
            print(audio_list)
            #  If any matching results were found populate the Audio combobox
            # otherwise display an error
            if len(audio_list) > 0:
                self.active_audio_query = query
                self.audio_list_cbo.set('')
                self.hebrew_text.delete(0, 'end')
                self.audio_file_entry.delete(0, 'end')
                self.audio_list_cbo['values'] = audio_list

                self.audio_list_cbo.current(0)
                self.audio_list_cbo.event_generate("<<ComboboxSelected>>")
            else:
                title = 'Search Failed'
                msg = f'No items found matching {category}'
                messagebox.showerror(title=title, message=msg)
        except sqlite3.Error as err:
            display_sql_error(err, query)

    #_____________________________________
    #            get_hebrew
    #_____________________________________
    def get_hebrew(self, event=None):
        """
            When a selection is made in the Audio combobox, retrieves
           the values from the HEBREW, AUDIO_FILE and LESSON_ID columns
           of the HEBREW_AUDIO table to populate the Hebrew and Audio File
           entry boxes and the Lessons combobox entry field.
        """
        #  Get the widget that triggered the event
        # and its text
        widget = event.widget
        selection = widget.get().split('|')
        audio_keywords = selection[0].strip()
        audio_id = selection[1].strip()

        self.audio_index.set(widget.current())
        print('###################################')
        print(f'Current index = {widget.current()}')

        sql_stmt = ('SELECT hebrew, audio_file, lesson_id '
                    ' FROM hebrew_audio '
                    f' WHERE audio_id = {audio_id};')

        print('Executing  query:')
        print(sql_stmt)
        try:
            SQL.execute(sql_stmt)
            row = SQL.fetchone()
            print(f'Row = {row}')
            self.hebrew.set(row['hebrew'])
            self.audio_file.set(row['audio_file'])

            #  Find the name of the lesson in the LESSON table
            # corresponding to the LESSON_ID if present.
            if row['lesson_id'] is None:
                self.lessons_lbl.configure(fg=FG_NOT_A_MEMBER)
            else:
                sql_stmt = ('SELECT l.name'
                            ' FROM lesson l, hebrew_audio ha'
                            ' WHERE l.lesson_id = ha.lesson_id'
                            f'  AND ha.lesson_id = {row["lesson_id"]};')
                SQL.execute(sql_stmt)
                row = SQL.fetchone()
                self.lessons_lbl.configure(fg=FG_A_MEMBER)
                self.lesson.set(row['name'])
            self.new_english.set('')
            category_table = self.category.get()
            print(f'Category table = {category_table}')
            if len(category_table) > 0:
                category_table = self.category.get().replace(' ', '_')
                sql_stmt = (f"SELECT audio_id FROM {category_table}"
                            f" WHERE audio_id = '{audio_id}';")
                print(f'SQL = {sql_stmt}')
                SQL.execute(sql_stmt)
                row = SQL.fetchone()
                if row:
                    print(f"Found {row['audio_id']}")
                    self.category_lbl.configure(fg=FG_A_MEMBER)
                else:
                    self.category_lbl.configure(fg=FG_NOT_A_MEMBER)
            current_word = widget.current() + 1
            max_words = len(widget['values'])
            self.total_words.set(f'#{current_word} of {max_words}')

            self.get_associated_webpages(audio_keywords, audio_id)


        except sqlite3.Error as err:
            display_sql_error(err, sql_stmt)


       # if hebrew_in_category(audio_id, category.get()):
       #     pass
        print(f'Query returned : hebrew={self.hebrew.get()} '
              f'audio_file={self.audio_file.get()}')

    #_____________________________________
    #             get_lesson
    #_____________________________________
    def get_lesson(self, event=None):
        """
            When a lesson is selected in the Lessons combobox, queries the
          LESSON column of the WEBPAGE table that matches that lesson
          and populates the Audio list combo box with the results.
        """

        # Get the widget that triggered the event and its displayed text.
        widget = event.widget
        lesson = widget.selection_get()
        query = ("SELECT english, audio_id"
                 " FROM hebrew_audio ha, lesson l"
                 f" WHERE l.name = '{lesson}'"
                 "   AND ha.lesson_id = l.lesson_id"
                 " ORDER BY english;")
        print(query)
        self.search_audio_entry.delete(0, 'end')
        try:
            SQL.execute(query)
            audio_list = ['{english}      | {audio_id}'.format(**row)
                          for row in SQL.fetchall()]
            print(audio_list)
            #  If any matching results were found populate the Audio combobox
            # otherwise display an error
            if len(audio_list) > 0:
                self.active_audio_query = query

                print(f'get_lesson Active audio query = {self.active_audio_query}')
                self.audio_list_cbo['values'] = audio_list
                self.audio_list_cbo.current(0)
                self.audio_list_cbo.event_generate("<<ComboboxSelected>>")
            else:
                title = 'Search Failed'
                msg = f'No items found matching {lesson}'
                messagebox.showerror(title=title, message=msg)
        except sqlite3.Error as err:
            display_sql_error(err, query)

    #_____________________________________
    #             get_lessons
    #_____________________________________
    def get_lessons(self):
        """
            Retrieves the values from the LESSON column of the
           HEBREW_AUDIO table to populate the lessons combo box.
        """

        query = \
        """
        SELECT name
          FROM lesson
          ORDER BY name;
        """
        try:
            SQL.execute(query)
            lessons = [row['name'] for row in SQL.fetchall()]
            # Sort the Ha-yesod lessons by the lesson number
            lessons.sort(key=lambda x: float(x.strip('Ha-yesod')))
            return lessons
        except sqlite3.Error as err:
            display_sql_error(err, query)

    #_____________________________________
    #           is_hebrew
    #_____________________________________
    def is_hebrew(self, string):
        """
          If the string contains just one Hebrew character
         the assumption is that it's Hebrew text.
        """
        if  bool(re.search('[\u0590-\u05FF]+', string)) or \
            bool(re.search('[\uFB1D-\uFB4F]+', string)):
            return True
        else:
            return False
   

    #_____________________________________
    #             play_audio
    #_____________________________________
    def play_audio(self, event=None):
        """
           Plays the audio of the file displayed in the audio file entry box. The
           audio file must be in the folder specified by the HEBREW_MEDIA constant.
        """
        audio = self.audio_file.get()

        if bool(re.match('.*.mp3', audio)) or \
           bool(re.match('.*.wav', audio)):
            try:
                hebrew_audio = HEBREW_MEDIA + audio
                print(hebrew_audio)
                clock = pygame.time.Clock()
                pygame.mixer.music.load(hebrew_audio)
                pygame.mixer.music.play()
                # Allows the audio to complete without interruption
                while pygame.mixer.music.get_busy():
                    clock.tick(1000)
            except RuntimeError as err:
                title = 'Pygame Error'
                msg = f'Error Message:\n {err.args[0]}'
                messagebox.showerror(title=title, message=msg)
            except Exception as err:
                title = 'Play_Audio Function Error'
                msg = f'Error Message:\n {err.args[0]}'
                messagebox.showerror(title=title, message=msg)

    #_____________________________________
    #        refresh_audio
    #_____________________________________
    def refresh_audio(self, active_query=None):
        """
          Refreshes the values in the Audio combobox by rerunning
         the SQL query specified by the active_query argument.
          If there is no active_query argument then all the values
         in the HEBREW_AUDIO table will be returned.
        """
        # Clear those widgets that aren't normally overwritten
        # by refreshing the Audio combobox
        self.new_english_entry.delete(0, 'end')
        print(f'refresh_audio Active audio query = {active_query}')

        # Re-populate the Audio combobox
        self.audio_list_cbo['values'] = self.get_audio_list(active_query)
        #  In case the active query was a search that returned 1 item and
        # the next command was to delete that item, just retrieve all the
        # items from the audio database.
        if len(self.audio_list_cbo['values']) == 0:
            self.audio_list_cbo['values'] = self.get_audio_list()
            active_query = None
        if not active_query:
            self.audio_list_cbo.current(0)
            self.audio_list_cbo.event_generate("<<ComboboxSelected>>")

    #_____________________________________
    #           remove_niqqud
    #_____________________________________
    def remove_niqqud(self, string):
        """
          Removes all the diacritical vowel marks from the Hebrew text.
         Oddly enough, in the case of some websites, including the niqqud
         doesn't enhance the accurracy of the search but actually throws
         it off.
        """
        niqqud = ['\u05B0','\u05B1','\u05B2','\u05B3','\u05B4',
                  '\u05B5','\u05B6','\u05B7','\u05B8','\u05B9',
                  '\u05BA','\u05BB','\u05BC','\u05BD']

        for n in niqqud:
           string = string.replace(n,'')
        
        print(string)  
        return string.strip()

    #_____________________________________
    #        remove_plural
    #_____________________________________
    def remove_plural(self, hebrew):
        """
           In some of the Hebrew entries in the Hebrew entry box
          the plural form of the word is enclosed in parentheses.
           Remove the plural form from the text so that the singular
          form of the word is searched for on the website.
          NOTE: Due to the weird results I got when cutting and
          pasting Hebrew characters surrounded by parentheses which
          looked perfectly normal and then trying to match left and
          right parentheses, I test for all possibilities,
          i.e. (*), (*(, )*).
        """
        # Left parenthesis search
        pl = re.compile(r'\(')
        # Right parenthesis search
        pr = re.compile(r'\)')

        print('Searching for and removing plurals.')
        pls = pl.search(hebrew)
        prs = pr.search(hebrew)
        if pls:
            print(f"hebrew = '{hebrew}'")
            print(f"Found left parenthesis '{pls.group()}'")
            if prs:
                print(f"Found right parenthesis '{prs.group()}'")
                search = re.sub(r'\(.*\)', '', hebrew)
                search = search.strip()
                print(f"Edit results: '{search}'")
                return search
            else:
                search = re.sub(r'\(.*\(', '', hebrew)
                search = search.strip()
                print(f"Edit results: '{search}'")
                return search
        elif prs:
            print(f"hebrew = '{hebrew}'")
            print(f"Found right parenthesis '{prs.group()}'")
            search = re.sub(r'\).*\)', '', hebrew) #r'\([^)]*\
            search = re.sub(r'(.*?)\s?\).*?\)', r'\1', hebrew)
            search = search.strip()
            print(f"Edit results: '{search}'")
            return search
        else:
            return hebrew.strip()

    #_____________________________________
    #        select_audio_file
    #_____________________________________
    def select_audio_file(self, event=None):
        """
            Opens a file dialog box to select an audio file for a new
          audio file or replace an audio file for an existing entry.
        """
        # Get the widget that triggered the event and its displayed text.
        widget = event.widget
        audio_file_name = widget.get()
        print(f'Widget name = {widget.widgetName} Audio file = {audio_file_name}')

        filepath = \
          filedialog.askopenfilename(initialdir="Media",
                                     filetypes=(("Mp3 files", "*.mp3")
                                                , ("HTML files", "*.html;*.htm")
                                                , ("All files", "*.*")))
        print(filepath)
        audio_file_name = os.path.split(filepath)[1]
        print(audio_file_name)
        audio_mgr.audio_file.set(audio_file_name)

    #_____________________________________
    #       step_through_audio
    #_____________________________________
    def step_through_audio(self, event=None):
        """
           Each right-click of the mouse in the Audio list combobox entry box
          plays the audio file currently displayed in the audio entry box
          and steps to the next item in the dropdown list of the Audio list
          combobox.
           When it reaches the end of the list it loops back to the beginning.
        """
        self.play_audio()
        next_index = self.audio_index.get() + 1
        if next_index < len(self.audio_list_cbo['values']):
            self.audio_list_cbo.current(next_index)
        else:
            self.audio_list_cbo.current(0)
        self.audio_list_cbo.event_generate("<<ComboboxSelected>>")


#############################
#           Main
#############################
if __name__ == '__main__':
    main()
