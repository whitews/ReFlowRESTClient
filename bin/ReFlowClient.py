import Tkinter
import ttk
import tkMessageBox
import tkFileDialog
from PIL import Image, ImageTk
import reflowrestclient.utils as rest
import json
import sys
import os

VERSION = '0.11b'

if hasattr(sys, '_MEIPASS'):
    # for PyInstaller 2.0
    RESOURCE_DIR = sys._MEIPASS
else:
    # for development
    RESOURCE_DIR = '../resources'

LOGO_PATH = os.path.join(RESOURCE_DIR, 'reflow_text.png')
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


class ChosenFile(object):
    def __init__(self, f):
        self.file = f
        self.file_path = f.name
        self.file_name = os.path.basename(f.name)
        self.subject = None
        self.visit = None
        self.specimen = None
        self.stimulation = None
        self.site_panel = None


class MyCheckbutton(Tkinter.Checkbutton):
    def __init__(self, *args, **kwargs):
        self.var = kwargs.get('variable',Tkinter.IntVar())
        kwargs['variable'] = self.var
        Tkinter.Checkbutton.__init__(self, *args, **kwargs)

    def is_checked(self):
        return self.var.get()

    def mark_checked(self):
        self.var.set(1)


class Application(Tkinter.Frame):

    def __init__(self, master):

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

        self.file_list = list()  # list of ChosenFile objects

        self.project_menu = None
        self.project_selection = Tkinter.StringVar()
        self.project_selection.trace("w", self.update_metadata)

        self.site_menu = None
        self.site_selection = Tkinter.StringVar()
        # TODO: site selection needs to update the site panel menu
        self.site_selection.trace("w", self.update_add_to_queue_button_state)

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

        # can't call super on old-style class, call parent init directly
        Tkinter.Frame.__init__(self, master)
        self.master.iconbitmap(ICON_PATH)
        self.master.title('ReFlow Client - ' + VERSION)
        self.master.minsize(width=954, height=640)
        self.master.config(bg=BACKGROUND_COLOR)

        self.menu_bar = Tkinter.Menu(master)
        self.master.config(menu=self.menu_bar)

        self.upload_log_text = None
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
        #self.load_login_frame()
        self.load_main_frame()

    def load_login_frame(self):

        def login():
            self.host = host_entry.get()
            self.username = user_entry.get()
            password = password_entry.get()
            try:
                self.token = rest.login(self.host, self.username, password)
            except Exception, e:
                print e
            if not self.token:
                tkMessageBox.showwarning(
                    'Login Failed',
                    'Are the hostname, username, and password are correct?')
                return
            self.login_frame.destroy()
            self.load_main_frame()

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
            expand=False,
            anchor='n',
            padx=0,
            pady=0)

        # Metadata frame - for choosing project/subject/site etc.
        metadata_frame = Tkinter.Frame(
            top_frame,
            bg=BACKGROUND_COLOR)
        # Start metadata choices, including:
        #    - project
        #    - site
        #    - subject
        #    - visit

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
            bg=BACKGROUND_COLOR)
        project_chooser_label.pack(side='left')
        project_chooser_label_frame.pack(fill='x')

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
            bg=BACKGROUND_COLOR)
        site_chooser_label.pack(side='left')
        site_chooser_label_frame.pack(fill='x')

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
            bg=BACKGROUND_COLOR)
        subject_chooser_label.pack(side='left')
        subject_chooser_label_frame.pack(fill='x')

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
            bg=BACKGROUND_COLOR)
        visit_chooser_label.pack(side='left')
        visit_chooser_label_frame.pack(fill='x')

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
            bg=BACKGROUND_COLOR)
        specimen_chooser_label.pack(side='left')
        specimen_chooser_label_frame.pack(fill='x')

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
            bg=BACKGROUND_COLOR)
        stimulation_chooser_label.pack(side='left')
        stimulation_chooser_label_frame.pack(fill='x')

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
            bg=BACKGROUND_COLOR)
        site_panel_chooser_label.pack(side='left')
        site_panel_chooser_label_frame.pack(fill='x')

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

        self.load_user_projects()
        self.load_specimens()

        metadata_frame.pack(
            fill='x',
            expand=False,
            anchor='n',
            side='left',
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)

        right_frame = Tkinter.Frame(top_frame, bg=BACKGROUND_COLOR)
        right_frame.pack(
            fill='both',
            expand=True,
            anchor='n',
            side='right',
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)

        # session log text box
        log_frame = Tkinter.LabelFrame(
            bottom_frame,
            bg=BACKGROUND_COLOR,
            text='Upload Queue')
        log_vertical_scroll_bar = Tkinter.Scrollbar(
            log_frame,
            orient='vertical')
        log_horizontal_scroll_bar = Tkinter.Scrollbar(
            log_frame,
            orient='horizontal')
        self.upload_log_text = Tkinter.Text(
            log_frame,
            xscrollcommand=log_horizontal_scroll_bar.set,
            yscrollcommand=log_vertical_scroll_bar.set,
            height=10,
            borderwidth=0,
            highlightthickness=0,
            highlightbackground=BORDER_COLOR,
            background=BACKGROUND_COLOR,
            takefocus=False,
            state='disabled')
        log_vertical_scroll_bar.config(
            command=self.upload_log_text.yview)
        log_horizontal_scroll_bar.config(
            command=self.upload_log_text.xview)
        log_vertical_scroll_bar.pack(side='right', fill='y')
        log_horizontal_scroll_bar.pack(side='bottom', fill='x')
        self.set_log_text_styles()
        self.upload_log_text.pack(fill='both', expand=True)
        log_frame.pack(
            fill='both',
            expand=False,
            anchor='s',
            padx=PAD_MEDIUM,
            pady=0)

        # upload button, upload progress bar
        progress_frame = Tkinter.Frame(bottom_frame, bg=BACKGROUND_COLOR)
        self.upload_progress_bar = ttk.Progressbar(progress_frame)
        self.upload_progress_bar.pack(side='bottom', fill='x', expand=True)
        progress_frame.pack(
            fill='x',
            expand=False,
            anchor='s',
            padx=PAD_MEDIUM,
            pady=PAD_SMALL)

        file_upload_frame = Tkinter.Frame(
            right_frame,
            bg=BACKGROUND_COLOR)

        file_upload_frame.pack(
            fill='both',
            expand=True,
            anchor='n',
            side='right',
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)

        # action buttons along the top of the window
        file_chooser_frame = Tkinter.Frame(
            file_upload_frame,
            bg=BACKGROUND_COLOR)

        file_chooser_button_frame = Tkinter.Frame(
            file_chooser_frame,
            bg=BACKGROUND_COLOR)
        file_chooser_button = ttk.Button(
            file_chooser_button_frame,
            text='Choose FCS Files...',
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
            text='Add to Upload Queue',
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
            pady=PAD_SMALL)

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
            anchor='n')

    def clear_selected_files(self):
        for k, v in self.file_list_canvas.children.items():
            if isinstance(v, MyCheckbutton):
                if v.is_checked():
                    v.destroy()

        self.update_add_to_queue_button_state()

    def select_all_files(self):
        for k, v in self.file_list_canvas.children.items():
            if isinstance(v, MyCheckbutton):
                v.mark_checked()
        self.update_add_to_queue_button_state()

    def choose_files(self):
        selected_files = tkFileDialog.askopenfiles('r')
        sorted_file_list = list()

        # clear the canvas
        self.file_list_canvas.delete(Tkinter.ALL)
        for i, f in enumerate(selected_files):
            sorted_file_list.append(f.name)
            chosen_file = ChosenFile(f)
            self.file_list.append(chosen_file)
            cb = MyCheckbutton(
                self.file_list_canvas,
                text=chosen_file.file_name
            )
            self.file_list_canvas.create_window(
                10,
                (20 * i),
                anchor='nw',
                window=cb
            )

        # update scroll region
        self.file_list_canvas.config(
            scrollregion=(0, 0, 1000, len(selected_files)*20))

        sorted_file_list.sort()

        self.update_add_to_queue_button_state()

    def load_user_projects(self):
        try:
            response = rest.get_projects(self.host, self.token)
        except Exception, e:
            print e
            return

        if not 'results' in response['data']:
            return

        self.project_menu['menu'].delete(0, 'end')
        self.site_menu['menu'].delete(0, 'end')
        self.subject_menu['menu'].delete(0, 'end')
        self.visit_menu['menu'].delete(0, 'end')
        for result in response['data']['results']:
            self.project_dict[result['project_name']] = result['id']
        for project_name in sorted(self.project_dict.keys()):
            self.project_menu['menu'].add_command(
                label=project_name,
                command=lambda value=project_name:
                self.project_selection.set(value))

    def load_project_sites(self, project_id):
        response = None
        try:
            response = rest.get_sites(
                self.host,
                self.token,
                project_pk=project_id)
        except Exception, e:
            print e

        if not 'results' in response['data']:
            return

        self.site_menu['menu'].delete(0, 'end')
        self.site_dict.clear()
        for result in response['data']['results']:
            self.site_dict[result['site_name']] = result['id']
        for site_name in sorted(self.site_dict.keys()):
            self.site_menu['menu'].add_command(
                label=site_name,
                command=lambda value=site_name:
                self.site_selection.set(value))

    def load_project_subjects(self, project_id):
        response = None
        try:
            response = rest.get_subjects(
                self.host,
                self.token,
                project_pk=project_id)
        except Exception, e:
            print e

        if not 'results' in response['data']:
            return

        self.subject_menu['menu'].delete(0, 'end')
        self.subject_dict.clear()
        for result in response['data']['results']:
            self.subject_dict[result['subject_code']] = result['id']
        for subject_code in sorted(self.subject_dict.keys()):
            self.subject_menu['menu'].add_command(
                label=subject_code,
                command=lambda value=subject_code:
                self.subject_selection.set(value))

    def load_project_visits(self, project_id):
        response = None
        try:
            response = rest.get_visit_types(
                self.host,
                self.token,
                project_pk=project_id)
        except Exception, e:
            print e

        if not 'results' in response['data']:
            return

        self.visit_menu['menu'].delete(0, 'end')
        self.visit_dict.clear()
        for result in response['data']['results']:
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

        if not 'results' in response['data']:
            return

        self.specimen_menu['menu'].delete(0, 'end')
        for result in response['data']['results']:
            self.specimen_dict[result['specimen_description']] = result['id']
        for specimen in sorted(self.specimen_dict.keys()):
            self.specimen_menu['menu'].add_command(
                label=specimen,
                command=lambda value=specimen:
                self.specimen_selection.set(value))

    def load_stimulations(self):
        try:
            response = rest.get_stimulations(self.host, self.token)
        except Exception, e:
            print e
            return

        if not 'results' in response['data']:
            return

        self.stimulation_menu['menu'].delete(0, 'end')
        for result in response['data']['results']:
            self.stimulation_dict[result['stimulation_name']] = result['id']
        for stimulation in sorted(self.stimulation_dict.keys()):
            self.stimulation_menu['menu'].add_command(
                label=stimulation,
                command=lambda value=stimulation:
                self.stimulation_selection.set(value))

    def load_site_panels(self):
        if not self.site_selection:
            return

        panel_args = [self.host, self.token]
        panel_kwargs = {'site_pk': self.site_selection}
        try:
            response = rest.get_site_panels(*panel_args, **panel_kwargs)
        except Exception, e:
            print e
            return

        if not 'results' in response['data']:
            return

        self.site_panel_menu['menu'].delete(0, 'end')
        self.site_panel_dict.clear()
        for result in response['data']:
            self.site_panel_dict[result['panel_name']] = result['id']
        for panel_name in sorted(self.site_panel_dict.keys()):
            self.site_panel_menu['menu'].add_command(
                label=panel_name,
                command=lambda value=panel_name:
                self.site_panel_selection.set(value))

    def update_metadata(*args):
        self = args[0]

        option_value = self.project_selection.get()

        if option_value in self.project_dict:
            self.load_project_sites(self.project_dict[option_value])
            self.load_project_subjects(self.project_dict[option_value])
            self.load_project_visits(self.project_dict[option_value])
            # TODO: add stimulations here and site panel

        self.update_upload_button_state()

    def update_add_to_queue_button_state(self, event=None):
        active = True

        if not self.site_selection.get() or \
                not self.subject_selection.get() or \
                not self.visit_selection.get() or \
                not self.specimen_selection.get():
            active = False
        if len(self.file_list_canvas.children) == 0:
            active = False

        if active:
            self.add_to_queue_button.config(state='active')
        else:
            self.add_to_queue_button.config(state='disabled')

    def add_to_upload_queue(self):
        pass
        # TODO: implement this after creating the upload queue frame/widgets

    def set_log_text_styles(self):
        self.upload_log_text.tag_config(
            'error',
            foreground=ERROR_FOREGROUND_COLOR)

    def upload_files(self):
        # TODO: get list of files to upload from the upload queue
        upload_file_list = None
        self.upload_progress_bar.config(maximum=len(upload_file_list))

        for f in self.file_list:
            response_dict = rest.post_sample(
                self.host,
                self.token,
                f.name,
                subject_pk=str(f.subject),
                site_panel_pk=str(f.site_panel),
                visit_type_pk=str(f.visit),
                specimen_pk=str(f.specimen),
                stimulation_pk=str(f.stimulation)
            )

            log_text = ''.join(
                [
                    f.name,
                    ' (',
                    str(response_dict['status']),
                    ': ',
                    str(response_dict['reason']),
                    ')\n',
                    json.dumps(response_dict['data'], indent=4),
                    '\n'
                ]
            )
            self.upload_log_text.config(state='normal')

            # TODO: update to color the queue row on success or failure
            if response_dict['status'] == 201:
                #self.file_list_canvas.itemconfig(
                #    i,
                #    fg=SUCCESS_FOREGROUND_COLOR,
                #    selectforeground=SUCCESS_FOREGROUND_COLOR)
                self.upload_log_text.insert('end', log_text)
            elif response_dict['status'] == 400:
                #self.file_list_canvas.itemconfig(
                #    i,
                #    fg=ERROR_FOREGROUND_COLOR,
                #    selectforeground=ERROR_FOREGROUND_COLOR)
                self.upload_log_text.insert('end', log_text, 'error')
            self.upload_log_text.config(state='disabled')

            self.upload_progress_bar.step()
            self.upload_progress_bar.update()


root = Tkinter.Tk()
app = Application(root)
app.mainloop()