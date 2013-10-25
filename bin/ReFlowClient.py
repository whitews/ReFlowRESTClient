import Tkinter
import ttk
import tkMessageBox
import tkFileDialog
import tkFont
from PIL import Image, ImageTk
import reflowrestclient.utils as rest
import json
import re
import sys
import os
from threading import Thread
VERSION = '0.11b'

if hasattr(sys, '_MEIPASS'):
    # for PyInstaller 2.0
    RESOURCE_DIR = sys._MEIPASS
else:
    # for development
    RESOURCE_DIR = '../resources'

LOGO_PATH = os.path.join(RESOURCE_DIR, 'reflow_text.gif')
if sys.platform == 'win32':
    ICON_PATH = os.path.join(RESOURCE_DIR, 'reflow.ico')

    # Hack for tkFileDialog bug in Windows in Python 2.7.5
    # to avoid IOError on erroneous parsing of file names
    # ...looks like the file names may be passed as Tcl lists???
    import Tkinter
    Tkinter.wantobjects = 0

elif sys.platform == 'darwin':
    ICON_PATH = os.path.join(RESOURCE_DIR, 'reflow.icns')
else:
    sys.exit("Your operating system is not supported.")

BACKGROUND_COLOR = '#ededed'
INACTIVE_BACKGROUND_COLOR = '#e2e2e2'
INACTIVE_FOREGROUND_COLOR = '#767676'
BORDER_COLOR = '#bebebe'
HIGHLIGHT_COLOR = '#5489b9'
ROW_ALT_COLOR = '#f3f6fa'
SUCCESS_FOREGROUND_COLOR = '#00cc00'
ERROR_FOREGROUND_COLOR = '#ff0000'

PAD_SMALL = 3
PAD_MEDIUM = 6
PAD_LARGE = 12
PAD_EXTRA_LARGE = 15

# Headers for the upload queue tree view
QUEUE_HEADERS = [
    'File',
    'Project',
    'Subject',
    'Visit',
    'Specimen',
    'Stimulation',
    'Site Panel',
    'Compensation',
    'Status'
]


class ChosenFile(object):
    def __init__(self, f, checkbox):
        self.file = f
        self.file_path = f.name
        self.file_name = os.path.basename(f.name)
        self.checkbox = checkbox
        self.status = 'Pending'  # other values are 'Error' and 'Complete'
        self.error_msg = ""

        self.project = None
        self.project_pk = None

        self.subject = None
        self.subject_pk = None

        self.visit = None
        self.visit_pk = None

        self.specimen = None
        self.specimen_pk = None

        self.stimulation = None
        self.stimulation_pk = None

        self.site_panel = None
        self.site_panel_pk = None

        self.compensation = None
        self.compensation_pk = None

    def reinitialize(self):
        self.status = 'Pending'  # other values are 'Error' and 'Complete'
        self.error_msg = None

        self.project = None
        self.project_pk = None

        self.subject = None
        self.subject_pk = None

        self.visit = None
        self.visit_pk = None

        self.specimen = None
        self.specimen_pk = None

        self.stimulation = None
        self.stimulation_pk = None

        self.site_panel = None
        self.site_panel_pk = None

        self.compensation = None
        self.compensation_pk = None

        # re-activate the checkbox
        self.checkbox.config(state=Tkinter.ACTIVE)
        self.checkbox.mark_unchecked()


class MyCheckbutton(Tkinter.Checkbutton):
    def __init__(self, *args, **kwargs):
        # We need to save the full path to populate the tree item later
        # Pop the value b/c the parent init is not expecting the kwarg
        self.file_path = kwargs.pop('file_path')

        # we create checkboxes dynamically and need to control the value
        # so we need to access the widget's value using our own attribute
        self.var = kwargs.get('variable', Tkinter.IntVar())
        kwargs['variable'] = self.var
        Tkinter.Checkbutton.__init__(self, *args, **kwargs)

    def is_checked(self):
        return self.var.get()

    def mark_checked(self):
        self.var.set(1)

    def mark_unchecked(self):
        self.var.set(0)


class Application(Tkinter.Frame):

    def __init__(self, master):

        style = ttk.Style()
        style.configure(
            'Treeview',
            borderwidth=1,
            font=('TkDefaultFont', 12, 'normal'))

        self.host = None
        self.username = None
        self.token = None

        # Using the names (project, site, etc.) as the key, pk as the value
        # for the choice dictionaries below.
        # The names need to be unique (and they should be) and
        # it's more convenient to lookup by key using the name.
        self.project_dict = dict()
        self.site_dict = dict()
        self.subject_dict = dict()
        self.visit_dict = dict()
        self.site_panel_dict = dict()
        self.specimen_dict = dict()
        self.stimulation_dict = dict()
        self.compensation_dict = dict()

        # dict of ChosenFile objects, key is file path, value is ChosenFile
        self.file_dict = dict()

        # start the metadata menus
        self.project_menu = None
        self.project_selection = Tkinter.StringVar()
        self.project_selection.trace("w", self.update_metadata)

        self.site_menu = None
        self.site_selection = Tkinter.StringVar()
        self.site_selection.trace("w", self.update_site_metadata)

        self.subject_menu = None
        self.subject_selection = Tkinter.StringVar()
        self.subject_selection.trace(
            "w",
            self.update_add_to_queue_button_state)

        self.visit_menu = None
        self.visit_selection = Tkinter.StringVar()
        self.visit_selection.trace("w", self.update_add_to_queue_button_state)

        self.specimen_menu = None
        self.specimen_selection = Tkinter.StringVar()
        self.specimen_selection.trace(
            "w",
            self.update_add_to_queue_button_state)

        self.stimulation_menu = None
        self.stimulation_selection = Tkinter.StringVar()
        self.stimulation_selection.trace(
            "w",
            self.update_add_to_queue_button_state)

        self.site_panel_menu = None
        self.site_panel_selection = Tkinter.StringVar()
        self.site_panel_selection.trace(
            "w",
            self.update_add_to_queue_button_state)

        self.compensation_menu = None
        self.compensation_selection = Tkinter.StringVar()

        # can't call super on old-style class, call parent init directly
        Tkinter.Frame.__init__(self, master)
        self.master.iconbitmap(ICON_PATH)
        self.master.title('ReFlow Client - ' + VERSION)
        self.master.minsize(width=960, height=640)
        self.master.config(bg=BACKGROUND_COLOR)

        self.menu_bar = Tkinter.Menu(master)
        self.master.config(menu=self.menu_bar)

        self.upload_button = None
        self.clear_selected_queue_button = None
        self.queue_tree = None
        self.upload_progress_bar = None
        self.add_to_queue_button = None
        self.file_list_canvas = None

        self.s = ttk.Style()
        self.s.map(
            'Inactive.TButton',
            foreground=[('disabled', INACTIVE_FOREGROUND_COLOR)])

        self.pack()

        self.login_frame = Tkinter.Frame(bg=BACKGROUND_COLOR)
        self.logo_image = ImageTk.PhotoImage(Image.open(LOGO_PATH))
        self.load_login_frame()
        #self.load_main_frame()

    def load_login_frame(self):

        def login(*args):
            host_text = host_entry.get()
            self.username = user_entry.get()
            password = password_entry.get()

            # remove 'http://' or trailing slash from host text if present
            matches = re.search('^(https://)?([^/]+)(/)*', host_text)

            try:
                self.host = matches.groups()[1]
                self.token = rest.get_token(self.host, self.username, password)
            except Exception, e:
                print e
            if not self.token:
                tkMessageBox.showwarning(
                    'Login Failed',
                    'Are the hostname, username, and password are correct?')
                return
            self.login_frame.destroy()
            self.master.unbind('<Return>')
            self.load_main_frame()

        self.master.bind('<Return>', login)

        logo_label = Tkinter.Label(self.login_frame, image=self.logo_image)
        logo_label.config(bg=BACKGROUND_COLOR)
        logo_label.pack(side='top', pady=PAD_EXTRA_LARGE)

        host_entry_frame = Tkinter.Frame(self.login_frame, bg=BACKGROUND_COLOR)
        host_label = Tkinter.Label(
            host_entry_frame,
            text='Hostname',
            bg=BACKGROUND_COLOR,
            width=8,
            anchor='e')
        host_label.pack(side='left')
        host_entry = Tkinter.Entry(
            host_entry_frame,
            highlightbackground=BACKGROUND_COLOR,
            width=24)
        host_entry.pack(padx=PAD_SMALL)
        host_entry_frame.pack(pady=PAD_SMALL)

        user_entry_frame = Tkinter.Frame(self.login_frame, bg=BACKGROUND_COLOR)
        user_label = Tkinter.Label(
            user_entry_frame,
            text='Username',
            bg=BACKGROUND_COLOR,
            width=8,
            anchor='e')
        user_label.pack(side='left')
        user_entry = Tkinter.Entry(
            user_entry_frame,
            highlightbackground=BACKGROUND_COLOR,
            width=24)
        user_entry.pack(padx=PAD_SMALL)
        user_entry_frame.pack(pady=PAD_SMALL)

        password_entry_frame = Tkinter.Frame(
            self.login_frame,
            bg=BACKGROUND_COLOR)
        password_label = Tkinter.Label(
            password_entry_frame,
            text='Password',
            bg=BACKGROUND_COLOR,
            width=8,
            anchor='e')
        password_label.pack(side='left')
        password_entry = Tkinter.Entry(
            password_entry_frame,
            show='*',
            highlightbackground=BACKGROUND_COLOR,
            width=24)
        password_entry.pack(padx=PAD_SMALL)
        password_entry_frame.pack(pady=PAD_SMALL)

        login_button_frame = Tkinter.Frame(
            self.login_frame,
            bg=BACKGROUND_COLOR)
        login_button_label = Tkinter.Label(
            login_button_frame,
            bg=BACKGROUND_COLOR)
        login_button = ttk.Button(
            login_button_label,
            text='Login',
            command=login)
        login_button.pack()
        login_button_label.pack(side='right')
        login_button_frame.pack(fill='x')

        self.login_frame.place(in_=self.master, anchor='c', relx=.5, rely=.5)

    def load_main_frame(self):
        main_frame = Tkinter.Frame(self.master, bg=BACKGROUND_COLOR)
        main_frame.pack(
            fill='both',
            expand=True,
            anchor='n',
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)

        top_frame = Tkinter.LabelFrame(
            main_frame,
            bg=BACKGROUND_COLOR)
        top_frame.pack(
            fill='both',
            expand=True,
            anchor='n',
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)
        top_frame.config(text="Choose & Categorize Files")

        bottom_frame = Tkinter.Frame(main_frame, bg=BACKGROUND_COLOR)
        bottom_frame.pack(
            fill='both',
            expand=True,
            anchor='n',
            padx=0,
            pady=0)

        # Metadata frame - for choosing project/subject/site etc.
        metadata_frame = Tkinter.Frame(
            top_frame,
            bg=BACKGROUND_COLOR)

        # overall project frame (on bottom left of main window)
        project_frame = Tkinter.Frame(
            metadata_frame,
            bg=BACKGROUND_COLOR)

        # project label frame (top of project chooser frame)
        project_chooser_label_frame = Tkinter.Frame(
            project_frame,
            bg=BACKGROUND_COLOR)
        project_chooser_label = Tkinter.Label(
            project_chooser_label_frame,
            text='Project:',
            bg=BACKGROUND_COLOR,
            width=12,
            anchor=Tkinter.E)
        project_chooser_label.pack(side='left')
        project_chooser_label_frame.pack(side='left', fill='x')

        # project chooser listbox frame (bottom of project chooser frame)
        project_chooser_frame = Tkinter.Frame(
            project_frame,
            bg=BACKGROUND_COLOR)
        self.project_menu = Tkinter.OptionMenu(
            project_chooser_frame,
            self.project_selection,
            '')
        self.project_menu.config(
            bg=BACKGROUND_COLOR,
            width=36)
        self.project_menu.pack(fill='x', expand=True)
        project_chooser_frame.pack(fill='x', expand=True)

        project_frame.pack(side='top', fill='x', expand=True)

        # overall site frame (on bottom, 2nd from left of main window
        site_frame = Tkinter.Frame(metadata_frame, bg=BACKGROUND_COLOR)

        # site label frame (top of site chooser frame)
        site_chooser_label_frame = Tkinter.Frame(
            site_frame,
            bg=BACKGROUND_COLOR)
        site_chooser_label = Tkinter.Label(
            site_chooser_label_frame,
            text='Site:',
            bg=BACKGROUND_COLOR,
            width=12,
            anchor=Tkinter.E)
        site_chooser_label.pack(side='left')
        site_chooser_label_frame.pack(side='left', fill='x')

        # site chooser listbox frame (bottom of site chooser frame)
        site_chooser_frame = Tkinter.Frame(
            site_frame,
            bg=BACKGROUND_COLOR)
        self.site_menu = Tkinter.OptionMenu(
            site_chooser_frame,
            self.site_selection,
            '')
        self.site_menu.config(bg=BACKGROUND_COLOR)
        self.site_menu.pack(fill='x', expand=True)
        site_chooser_frame.pack(fill='x', expand=True)

        site_frame.pack(side='top', fill='x', expand=True)

        # overall subject frame (on bottom, 2nd from left of main window
        subject_frame = Tkinter.Frame(metadata_frame, bg=BACKGROUND_COLOR)

        # subject label frame (top of subject chooser frame)
        subject_chooser_label_frame = Tkinter.Frame(
            subject_frame,
            bg=BACKGROUND_COLOR)
        subject_chooser_label = Tkinter.Label(
            subject_chooser_label_frame,
            text='Subject:',
            bg=BACKGROUND_COLOR,
            width=12,
            anchor=Tkinter.E)
        subject_chooser_label.pack(side='left')
        subject_chooser_label_frame.pack(side='left', fill='x')

        # subject chooser listbox frame (bottom of subject chooser frame)
        subject_chooser_frame = Tkinter.Frame(
            subject_frame,
            bg=BACKGROUND_COLOR)
        self.subject_menu = Tkinter.OptionMenu(
            subject_chooser_frame,
            self.subject_selection,
            '')
        self.subject_menu.config(bg=BACKGROUND_COLOR)
        self.subject_menu.pack(fill='x', expand=True)
        subject_chooser_frame.pack(fill='x', expand=True)

        subject_frame.pack(side='top', fill='x', expand=True)

        # overall visit frame
        visit_frame = Tkinter.Frame(metadata_frame, bg=BACKGROUND_COLOR)

        # visit label frame (top of visit chooser frame)
        visit_chooser_label_frame = Tkinter.Frame(
            visit_frame,
            bg=BACKGROUND_COLOR)
        visit_chooser_label = Tkinter.Label(
            visit_chooser_label_frame,
            text='Visit:',
            bg=BACKGROUND_COLOR,
            width=12,
            anchor=Tkinter.E)
        visit_chooser_label.pack(side='left')
        visit_chooser_label_frame.pack(side='left', fill='x')

        # visit chooser listbox frame (bottom of visit chooser frame)
        visit_chooser_frame = Tkinter.Frame(visit_frame, bg=BACKGROUND_COLOR)
        self.visit_menu = Tkinter.OptionMenu(
            visit_chooser_frame,
            self.visit_selection,
            '')
        self.visit_menu.config(bg=BACKGROUND_COLOR)
        self.visit_menu.pack(fill='x', expand=True)
        visit_chooser_frame.pack(fill='x', expand=True)

        visit_frame.pack(side='top', fill='x', expand=True)

        # overall specimen frame
        specimen_frame = Tkinter.Frame(
            metadata_frame,
            bg=BACKGROUND_COLOR)

        # specimen label frame (top of specimen chooser frame)
        specimen_chooser_label_frame = Tkinter.Frame(
            specimen_frame,
            bg=BACKGROUND_COLOR)
        specimen_chooser_label = Tkinter.Label(
            specimen_chooser_label_frame,
            text='Specimen:',
            bg=BACKGROUND_COLOR,
            width=12,
            anchor=Tkinter.E)
        specimen_chooser_label.pack(side='left')
        specimen_chooser_label_frame.pack(side='left', fill='x')

        # specimen chooser listbox frame (bottom of specimen chooser frame)
        specimen_chooser_frame = Tkinter.Frame(
            specimen_frame,
            bg=BACKGROUND_COLOR)
        self.specimen_menu = Tkinter.OptionMenu(
            specimen_chooser_frame,
            self.specimen_selection,
            '')
        self.specimen_menu.config(bg=BACKGROUND_COLOR)
        self.specimen_menu.pack(fill='x', expand=True)
        specimen_chooser_frame.pack(fill='x', expand=True)

        specimen_frame.pack(side='top', fill='x', expand=True)

        # overall stimulation frame
        stimulation_frame = Tkinter.Frame(
            metadata_frame,
            bg=BACKGROUND_COLOR)

        # stimulation label frame (top of stimulation chooser frame)
        stimulation_chooser_label_frame = Tkinter.Frame(
            stimulation_frame,
            bg=BACKGROUND_COLOR)
        stimulation_chooser_label = Tkinter.Label(
            stimulation_chooser_label_frame,
            text='Stimulation:',
            bg=BACKGROUND_COLOR,
            width=12,
            anchor=Tkinter.E)
        stimulation_chooser_label.pack(side='left')
        stimulation_chooser_label_frame.pack(side='left', fill='x')

        # stimulation chooser listbox frame
        # (bottom of stimulation chooser frame)
        stimulation_chooser_frame = Tkinter.Frame(
            stimulation_frame,
            bg=BACKGROUND_COLOR)
        self.stimulation_menu = Tkinter.OptionMenu(
            stimulation_chooser_frame,
            self.stimulation_selection,
            '')
        self.stimulation_menu.config(bg=BACKGROUND_COLOR)
        self.stimulation_menu.pack(fill='x', expand=True)
        stimulation_chooser_frame.pack(fill='x', expand=True)

        stimulation_frame.pack(side='top', fill='x', expand=True)

        # overall site_panel frame
        site_panel_frame = Tkinter.Frame(
            metadata_frame,
            bg=BACKGROUND_COLOR)

        # site_panel label frame (top of site_panel chooser frame)
        site_panel_chooser_label_frame = Tkinter.Frame(
            site_panel_frame,
            bg=BACKGROUND_COLOR)
        site_panel_chooser_label = Tkinter.Label(
            site_panel_chooser_label_frame,
            text='Site Panel:',
            bg=BACKGROUND_COLOR,
            width=12,
            anchor=Tkinter.E)
        site_panel_chooser_label.pack(side='left')
        site_panel_chooser_label_frame.pack(side='left', fill='x')

        # site_panel chooser listbox frame
        # (bottom of site_panel chooser frame)
        site_panel_chooser_frame = Tkinter.Frame(
            site_panel_frame,
            bg=BACKGROUND_COLOR)
        self.site_panel_menu = Tkinter.OptionMenu(
            site_panel_chooser_frame,
            self.site_panel_selection,
            '')
        self.site_panel_menu.config(bg=BACKGROUND_COLOR)
        self.site_panel_menu.pack(fill='x', expand=True)
        site_panel_chooser_frame.pack(fill='x', expand=True)

        site_panel_frame.pack(side='top', fill='x', expand=True)

        # overall compensation frame
        compensation_frame = Tkinter.Frame(
            metadata_frame,
            bg=BACKGROUND_COLOR)

        # compensation label frame (top of compensation chooser frame)
        compensation_chooser_label_frame = Tkinter.Frame(
            compensation_frame,
            bg=BACKGROUND_COLOR)
        compensation_chooser_label = Tkinter.Label(
            compensation_chooser_label_frame,
            text='Compensation:',
            bg=BACKGROUND_COLOR,
            width=12,
            anchor=Tkinter.E)
        compensation_chooser_label.pack(side='left')
        compensation_chooser_label_frame.pack(side='left', fill='x')

        # compensation chooser listbox frame
        # (bottom of compensation chooser frame)
        compensation_chooser_frame = Tkinter.Frame(
            compensation_frame,
            bg=BACKGROUND_COLOR)
        self.compensation_menu = Tkinter.OptionMenu(
            compensation_chooser_frame,
            self.compensation_selection,
            '')
        self.compensation_menu.config(bg=BACKGROUND_COLOR)
        self.compensation_menu.pack(fill='x', expand=True)
        compensation_chooser_frame.pack(fill='x', expand=True)

        compensation_frame.pack(side='top', fill='x', expand=True)

        self.load_user_projects()
        self.load_specimens()

        metadata_frame.pack(
            fill='x',
            expand=False,
            anchor='n',
            side='left',
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)

        # start file chooser widgets
        file_chooser_frame = Tkinter.Frame(
            top_frame,
            bg=BACKGROUND_COLOR)

        file_chooser_button_frame = Tkinter.Frame(
            file_chooser_frame,
            bg=BACKGROUND_COLOR)
        file_chooser_button = ttk.Button(
            file_chooser_button_frame,
            text='Choose Files...',
            command=self.choose_files)
        file_clear_selection_button = ttk.Button(
            file_chooser_button_frame,
            text='Clear Selected',
            command=self.clear_selected_files)
        file_clear_all_button = ttk.Button(
            file_chooser_button_frame,
            text='Select All',
            command=self.select_all_files)
        self.add_to_queue_button = ttk.Button(
            file_chooser_button_frame,
            text='Add to Queue',
            state='disabled',
            style='Inactive.TButton',
            command=self.add_to_upload_queue)
        file_chooser_button.pack(side='left')
        file_clear_selection_button.pack(side='left')
        file_clear_all_button.pack(side='left')
        self.add_to_queue_button.pack(side='right')
        file_chooser_button_frame.pack(
            anchor='n',
            fill='x',
            expand=False,
        )

        file_list_frame = Tkinter.Frame(
            file_chooser_frame,
            bg=BACKGROUND_COLOR,
            highlightcolor=HIGHLIGHT_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1)
        file_scroll_bar = Tkinter.Scrollbar(
            file_list_frame,
            orient='vertical')
        self.file_list_canvas = Tkinter.Canvas(
            file_list_frame,
            yscrollcommand=file_scroll_bar.set,
            relief='flat',
            borderwidth=0)
        self.file_list_canvas.bind('<MouseWheel>', self._on_mousewheel)
        file_scroll_bar.config(command=self.file_list_canvas.yview)
        file_scroll_bar.pack(side='right', fill='y')
        self.file_list_canvas.pack(
            fill='both',
            expand=True
        )
        file_list_frame.pack(
            fill='both',
            expand=True)
        file_chooser_frame.pack(
            fill='both',
            expand=True,
            anchor='n',
            side='right',
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)

        # start upload queue stuff
        upload_queue_frame = Tkinter.LabelFrame(
            bottom_frame,
            bg=BACKGROUND_COLOR,
            text='Upload Queue',
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)

        upload_queue_button_frame = Tkinter.Frame(
            upload_queue_frame,
            bg=BACKGROUND_COLOR)
        self.upload_button = ttk.Button(
            upload_queue_button_frame,
            text='Upload',
            style='Inactive.TButton',
            command=self.upload_files)
        self.upload_button.pack(side='left', expand=False)
        self.clear_selected_queue_button = ttk.Button(
            upload_queue_button_frame,
            text='Clear Selected',
            style='Inactive.TButton',
            command=self.clear_selected_queue)
        self.clear_selected_queue_button.pack(side='left', expand=False)
        display_error_button = ttk.Button(
            upload_queue_button_frame,
            text='View Errors',
            command=self.display_error)
        display_error_button.pack(side='left', expand=False)
        upload_queue_button_frame.pack(
            fill='x',
            expand=False,
            anchor='n',
            padx=0,
            pady=PAD_SMALL)

        # using a Treeview to mimic a table, no table in Tkinter/ttk
        self.queue_tree = ttk.Treeview(
            upload_queue_frame,
            columns=QUEUE_HEADERS,
            show="headings")
        queue_vertical_scroll_bar = ttk.Scrollbar(
            upload_queue_frame,
            orient="vertical",
            command=self.queue_tree.yview)
        self.queue_tree.config(
            yscrollcommand=queue_vertical_scroll_bar.set)
        self.queue_tree.pack(
            side='left',
            fill='both',
            expand=True,
            anchor='w')
        queue_vertical_scroll_bar.pack(
            side='right',
            fill='y')
        for header in QUEUE_HEADERS:
            self.queue_tree.heading(header, text=header.title())
            self.queue_tree.column(header, width=25)

        # setup Treeview tag styles, it's the only way to change colors/fonts
        # Note: it changes the entire row, individual cells cannot be
        # formatted
        self.queue_tree.tag_configure(
            tagname='pending',
            font=('TkDefaultFont', 12, 'bold'))
        self.queue_tree.tag_configure(
            tagname='error',
            font=('TkDefaultFont', 12, 'bold'),
            foreground='red')
        self.queue_tree.tag_configure(
            tagname='complete',
            font=('TkDefaultFont', 12, 'italic'),
            foreground='#555555')

        upload_queue_frame.pack(
            fill='both',
            expand=True,
            padx=PAD_MEDIUM,
            pady=0)

        # Progress bar
        progress_frame = Tkinter.Frame(bottom_frame, bg=BACKGROUND_COLOR)
        self.upload_progress_bar = ttk.Progressbar(progress_frame)
        self.upload_progress_bar.pack(side='bottom', fill='x', expand=True)
        progress_frame.pack(
            fill='x',
            expand=False,
            anchor='s',
            padx=PAD_MEDIUM,
            pady=PAD_SMALL)

    def _on_mousewheel(self, event):
        self.file_list_canvas.yview_scroll(-event.delta, "units")

    def clear_selected_files(self):
        cb_to_delete = []
        for k, cb in self.file_list_canvas.children.items():
            if isinstance(cb, MyCheckbutton):
                if cb.is_checked() and cb.cget('state') != Tkinter.DISABLED:
                    cb_to_delete.append(cb)

        if len(cb_to_delete) == 0:
            self.update_add_to_queue_button_state()
            return

        for cb in cb_to_delete:
            cb.destroy()

        # and re-order items to not leave blank spaces
        i = 0
        cb_dict = self.file_list_canvas.children
        for cb in sorted(cb_dict.values(), key=lambda x: x.cget('text')):
            if isinstance(cb, MyCheckbutton):
                self.file_list_canvas.create_window(
                    10,
                    (20 * i),
                    anchor='nw',
                    window=cb
                )
                i += 1

        self.update_add_to_queue_button_state()

    def select_all_files(self):
        for k, v in self.file_list_canvas.children.items():
            if isinstance(v, MyCheckbutton):
                v.mark_checked()
        self.update_add_to_queue_button_state()

    def choose_files(self):
        selected_files = tkFileDialog.askopenfiles('r')

        if len(selected_files) < 1:
            return

        # clear the canvas
        self.file_list_canvas.delete(Tkinter.ALL)
        for k in self.file_list_canvas.children.keys():
            del(self.file_list_canvas.children[k])

        for i, f in enumerate(selected_files):
            cb = MyCheckbutton(
                self.file_list_canvas,
                text=os.path.basename(f.name),
                file_path=f.name
            )
            # bind to our canvas mouse function
            # to keep scrolling working when the mouse is over a checkbox
            cb.bind('<MouseWheel>', self._on_mousewheel)
            self.file_list_canvas.create_window(
                10,
                (20 * i),
                anchor='nw',
                window=cb
            )

            chosen_file = ChosenFile(f, cb)

            self.file_dict[chosen_file.file_path] = chosen_file

        # update scroll region
        self.file_list_canvas.config(
            scrollregion=(0, 0, 1000, len(selected_files)*20))

        self.update_add_to_queue_button_state()

    def load_user_projects(self):
        try:
            response = rest.get_projects(self.host, self.token)
        except Exception, e:
            print e
            return

        if not 'data' in response:
            return

        self.project_menu['menu'].delete(0, 'end')
        self.site_menu['menu'].delete(0, 'end')
        self.subject_menu['menu'].delete(0, 'end')
        self.visit_menu['menu'].delete(0, 'end')
        self.stimulation_menu['menu'].delete(0, 'end')
        self.site_panel_menu['menu'].delete(0, 'end')
        self.compensation_menu['menu'].delete(0, 'end')

        for result in response['data']:
            self.project_dict[result['project_name']] = result['id']
        for project_name in sorted(self.project_dict.keys()):
            self.project_menu['menu'].add_command(
                label=project_name,
                command=lambda value=project_name:
                self.project_selection.set(value))

    def load_project_sites(self, project_id):
        self.site_menu['menu'].delete(0, 'end')
        self.site_selection.set('')
        self.site_dict.clear()

        response = None
        try:
            response = rest.get_sites(
                self.host,
                self.token,
                project_pk=project_id)
        except Exception, e:
            print e

        if not 'data' in response:
            return

        for result in response['data']:
            self.site_dict[result['site_name']] = result['id']
        for site_name in sorted(self.site_dict.keys()):
            self.site_menu['menu'].add_command(
                label=site_name,
                command=lambda value=site_name:
                self.site_selection.set(value))

    def load_project_subjects(self, project_id):
        self.subject_menu['menu'].delete(0, 'end')
        self.subject_selection.set('')
        self.subject_dict.clear()

        response = None
        try:
            response = rest.get_subjects(
                self.host,
                self.token,
                project_pk=project_id)
        except Exception, e:
            print e

        if not 'data' in response:
            return

        for result in response['data']:
            self.subject_dict[result['subject_code']] = result['id']
        for subject_code in sorted(self.subject_dict.keys()):
            self.subject_menu['menu'].add_command(
                label=subject_code,
                command=lambda value=subject_code:
                self.subject_selection.set(value))

    def load_project_visits(self, project_id):
        self.visit_menu['menu'].delete(0, 'end')
        self.visit_selection.set('')
        self.visit_dict.clear()

        response = None
        try:
            response = rest.get_visit_types(
                self.host,
                self.token,
                project_pk=project_id)
        except Exception, e:
            print e

        if not 'data' in response:
            return

        for result in response['data']:
            self.visit_dict[result['visit_type_name']] = result['id']
        for visit_type_name in sorted(self.visit_dict.keys()):
            self.visit_menu['menu'].add_command(
                label=visit_type_name,
                command=lambda value=visit_type_name:
                self.visit_selection.set(value))

    def load_specimens(self):
        try:
            response = rest.get_specimens(self.host, self.token)
        except Exception, e:
            print e
            return

        if not 'data' in response:
            return

        for result in response['data']:
            self.specimen_dict[result['specimen_description']] = result['id']
        for specimen in sorted(self.specimen_dict.keys()):
            self.specimen_menu['menu'].add_command(
                label=specimen,
                command=lambda value=specimen:
                self.specimen_selection.set(value))

    def load_stimulations(self, project_id):
        self.stimulation_menu['menu'].delete(0, 'end')
        self.stimulation_selection.set('')
        self.stimulation_dict.clear()

        try:
            response = rest.get_stimulations(
                self.host,
                self.token,
                project_pk=project_id)
        except Exception, e:
            print e
            return

        if not 'data' in response:
            return

        for result in response['data']:
            self.stimulation_dict[result['stimulation_name']] = result['id']
        for stimulation in sorted(self.stimulation_dict.keys()):
            self.stimulation_menu['menu'].add_command(
                label=stimulation,
                command=lambda value=stimulation:
                self.stimulation_selection.set(value))

    def update_site_metadata(self, *args, **kwargs):
        self.site_panel_menu['menu'].delete(0, 'end')
        self.site_panel_selection.set('')
        self.site_panel_dict.clear()

        self.compensation_menu['menu'].delete(0, 'end')
        self.compensation_selection.set('')
        self.compensation_dict.clear()

        if not self.site_selection.get():
            return
        site_pk = self.site_dict[self.site_selection.get()]
        rest_args = [self.host, self.token]
        rest_kwargs = {'site_pk': site_pk}
        try:
            response = rest.get_site_panels(*rest_args, **rest_kwargs)
        except Exception, e:
            print e
            return

        if not 'data' in response:
            return

        for result in response['data']:
            self.site_panel_dict[result['name']] = result['id']
        for panel_name in sorted(self.site_panel_dict.keys()):
            self.site_panel_menu['menu'].add_command(
                label=panel_name,
                command=lambda value=panel_name:
                self.site_panel_selection.set(value))

        try:
            response = rest.get_compensations(*rest_args, **rest_kwargs)
        except Exception, e:
            print e
            return

        if not 'data' in response:
            return

        for result in response['data']:
            self.compensation_dict[result['original_filename']] = result['id']
        for comp_filename in sorted(self.compensation_dict.keys()):
            self.compensation_menu['menu'].add_command(
                label=comp_filename,
                command=lambda value=comp_filename:
                self.compensation_selection.set(value))

    def update_metadata(*args):
        self = args[0]

        option_value = self.project_selection.get()

        if option_value in self.project_dict:
            self.load_project_sites(self.project_dict[option_value])
            self.load_project_subjects(self.project_dict[option_value])
            self.load_project_visits(self.project_dict[option_value])
            self.load_stimulations(self.project_dict[option_value])

        self.update_add_to_queue_button_state()

    def update_add_to_queue_button_state(self, *args, **kwargs):
        active = True

        if not self.site_selection.get() or \
                not self.subject_selection.get() or \
                not self.visit_selection.get() or \
                not self.specimen_selection.get() or \
                not self.stimulation_selection.get() or \
                not self.site_panel_selection.get():
            active = False
        if len(self.file_list_canvas.children) == 0:
            active = False

        if active:
            self.add_to_queue_button.config(state='active')
        else:
            self.add_to_queue_button.config(state='disabled')

    def add_to_upload_queue(self):
        for k, v in self.file_list_canvas.children.items():
            if isinstance(v, MyCheckbutton):
                if v.is_checked() and v.cget('state') != Tkinter.DISABLED:
                    # populate the ChosenFile attributes
                    c_file = self.file_dict[v.file_path]

                    c_file.project = self.project_selection.get()
                    c_file.project_pk = self.project_dict[c_file.project]

                    c_file.subject = self.subject_selection.get()
                    c_file.subject_pk = self.subject_dict[c_file.subject]

                    c_file.visit = self.visit_selection.get()
                    c_file.visit_pk = self.visit_dict[c_file.visit]

                    c_file.specimen = self.specimen_selection.get()
                    c_file.specimen_pk = self.specimen_dict[c_file.specimen]

                    c_file.stimulation = self.stimulation_selection.get()
                    c_file.stimulation_pk = \
                        self.stimulation_dict[c_file.stimulation]

                    c_file.site_panel = self.site_panel_selection.get()
                    c_file.site_panel_pk = \
                        self.site_panel_dict[c_file.site_panel]

                    c_file.compensation = self.compensation_selection.get()
                    if c_file.compensation:
                        c_file.compensation_pk = \
                            self.compensation_dict[c_file.compensation]

                    # Populate our tree item,
                    item = list()
                    item.append(c_file.file_name)
                    item.append(c_file.project)
                    item.append(c_file.subject)
                    item.append(c_file.visit)
                    item.append(c_file.specimen)
                    item.append(c_file.stimulation)
                    item.append(c_file.site_panel)
                    item.append(c_file.compensation)
                    item.append(c_file.status)

                    # check if the item is already in the queue
                    # and remove it if it is
                    if self.queue_tree.exists(c_file.file_path):
                        self.queue_tree.delete(c_file.file_path)

                    # add item to the tree, the id will be the file's
                    # full path so we can identify tree items with the same
                    # file name
                    self.queue_tree.insert(
                        '',
                        'end',
                        values=item,
                        tags='pending',
                        iid=c_file.file_path)

                    # finally, disable our checkboxes
                    v.config(state=Tkinter.DISABLED)

        self._auto_resize_queue_columns()

    def _auto_resize_queue_columns(self):
        """
        automagically set the column widths
        """

        # get_children returns a tuple of item IDs from the tree
        tree_items = self.queue_tree.get_children()

        total_width = 0
        col_widths = {}
        for i, value in enumerate(QUEUE_HEADERS):
            col_widths[i] = 0

        for item in tree_items:
            for i, value in enumerate(self.queue_tree.item(item)['values']):
                width = tkFont.Font().measure(value)
                header_width = tkFont.Font().measure(QUEUE_HEADERS[i])
                # don't make the column smaller than the header text
                if header_width > width:
                    width = header_width
                if width > col_widths[i]:
                    col_widths[i] = width

        total_width = sum(col_widths.values())

        # get the tree's width
        tree_width = self.queue_tree.winfo_width()

        # see if there's any extra space leftover
        # and distribute equally across the columns
        extra = 0
        if tree_width > total_width:
            extra = int(
                (tree_width - total_width)/len(col_widths))
            # the extra width may not quite cover the whole
            # tree width if the column count doesn't evenly
            # divide the leftover space (we floored the value)
            # add the extra extra to the first column
            if tree_width > total_width + (extra * len(col_widths)):
                col_widths[0] = \
                    col_widths[0] + \
                    tree_width - \
                    (total_width + (extra * len(col_widths)))

        # apply our auto-generated column widths
        for i, value in enumerate(tree_items):
            self.queue_tree.column(
                QUEUE_HEADERS[i],
                width=col_widths[i]+extra)

    def clear_selected_queue(self):
        # get_children returns a tuple of item IDs from the tree
        tree_items = self.queue_tree.selection()

        # the items are the tree rows
        for item in tree_items:
            # the items are the row IDs, which we set as the file's full path
            try:
                chosen_file = self.file_dict[item]
            except Exception, e:
                print e
                break

            # user may have cleared the checkbox by now,
            # if so, we'll delete this file from our list,
            # if not, re-initialize the checkbox
            if chosen_file.checkbox in self.file_list_canvas.children.values():
                chosen_file.reinitialize()
            else:
                del(self.file_dict[item])
            self.queue_tree.delete(item)

    def display_error(self):
        # get_children returns a tuple of item IDs from the tree
        tree_items = self.queue_tree.selection()
        message_list = []

        # the items are the tree rows
        for item in tree_items:
           # the items are the row IDs, which we set as the file's full path
            try:
                chosen_file = self.file_dict[item]
            except Exception, e:
                print e
                break

            if chosen_file.error_msg:
                message_list.append(
                    "%s:\n\t%s" % (chosen_file.file_name, chosen_file.error_msg)
                )
        if len(tree_items) == 0:
            message_list.append("No items selected")
        elif len(message_list) == 0:
            message_list.append("No errors")

        message_win = Tkinter.Toplevel()
        message_win.title('Errors')
        message_win.minsize(width=480, height=320)
        message_win.config(bg=BACKGROUND_COLOR)

        message_label = Tkinter.Label(
            message_win,
            text="\n\n".join(message_list),
            bg=BACKGROUND_COLOR,
            justify=Tkinter.LEFT)
        message_label.pack(
            anchor='nw',
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM
        )

        # make sure there's a way to destroy the dialog
        message_button = ttk.Button(
            message_win,
            text='OK',
            command=message_win.destroy)
        message_button.pack()

    def upload_files(self):
        t = Thread(target=self._upload_files)
        t.start()

    def _upload_files(self):
        # get_children returns a tuple of item IDs from the tree
        tree_items = self.queue_tree.get_children()

        # use the item IDs as keys, file names as values
        # we'll check the row's status value to upload only 'Pending' files
        upload_list = []

        # the items are the tree rows
        for item in tree_items:
            # the row's values are in the order we created them in
            # the status is the last column
            if self.queue_tree.item(item)['values'][-1] == 'Pending':
                # the file path is the item
                upload_list.append(item)

        self.upload_progress_bar.config(maximum=len(upload_list))
        self.add_to_queue_button.config(state='disabled')
        self.upload_button.config(state='disabled')
        self.clear_selected_queue_button.config(state='disabled')
        for item in upload_list:
            try:
                chosen_file = self.file_dict[item]
            except Exception, e:
                print e

            if not chosen_file.project or \
                    not chosen_file.subject_pk or \
                    not chosen_file.site_panel_pk or \
                    not chosen_file.specimen_pk or \
                    not chosen_file.file_path or \
                    not chosen_file.stimulation_pk or \
                    not chosen_file.visit_pk:
                break

            rest_args = [
                self.host,
                self.token,
                chosen_file.file_path
            ]
            rest_kwargs = {
                'subject_pk': str(chosen_file.subject_pk),
                'site_panel_pk': str(chosen_file.site_panel_pk),
                'visit_type_pk': str(chosen_file.visit_pk),
                'specimen_pk': str(chosen_file.specimen_pk),
                'stimulation_pk': str(chosen_file.stimulation_pk)
            }

            if chosen_file.compensation_pk:
                rest_kwargs['compensation_pk'] = \
                    str(chosen_file.compensation_pk)

            response_dict = rest.post_sample(
                *rest_args,
                **rest_kwargs
            )

            log_text = ''.join(
                [
                    chosen_file.file_name,
                    ' (',
                    str(response_dict['status']),
                    ': ',
                    str(response_dict['reason']),
                    ')\n',
                    json.dumps(response_dict['data'], indent=4),
                    '\n'
                ]
            )

            print log_text

            if response_dict['status'] == 201:
                status = 'Complete'
            elif response_dict['status'] == 400:
                chosen_file.error_msg = "\n".join(
                    json.loads(response_dict['data']).values()[0])
                status = 'Error'
            else:
                status = 'Error'

            self.queue_tree.item(item, tags=status.lower())
            # cannot set the values directly, must get them and reset
            values = list(self.queue_tree.item(item, 'values'))
            values[-1] = status
            # re-populate the values
            self.queue_tree.item(item, values=values)

            # update our ChosenFile object
            chosen_file.status = status

            self.upload_progress_bar.step()
            self.upload_progress_bar.update()

        self.update_add_to_queue_button_state()
        self.upload_button.config(state='active')
        self.clear_selected_queue_button.config(state='active')


root = Tkinter.Tk()
app = Application(root)
app.mainloop()