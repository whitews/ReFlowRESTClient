import Tkinter
import ttk
import tkMessageBox
import tkFileDialog
import tkFont
from PIL import Image, ImageTk
import json
import re
import sys
import os
import calendar
from threading import Thread
from exceptions import TypeError

import reflowrestclient.utils as rest
import flowio

VERSION = '0.11b'

if hasattr(sys, '_MEIPASS'):
    # for PyInstaller 2.0
    RESOURCE_DIR = sys._MEIPASS
else:
    # for development
    RESOURCE_DIR = '../../resources'

LOGO_PATH = os.path.join(RESOURCE_DIR, 'reflow_text.gif')
if sys.platform == 'win32':
    ICON_PATH = os.path.join(RESOURCE_DIR, 'reflow2.ico')
elif sys.platform == 'darwin':
    ICON_PATH = os.path.join(RESOURCE_DIR, 'reflow.icns')
elif sys.platform == 'linux2':
    ICON_PATH = None  # haven't figured out icons on linux yet : (
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

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 776

PAD_SMALL = 2
PAD_MEDIUM = 4
PAD_LARGE = 8
PAD_EXTRA_LARGE = 14

LABEL_WIDTH = 16

# Headers for the upload queue tree view
QUEUE_HEADERS = [
    'File',
    'Project',
    'Subject',
    'Visit',
    'Specimen',
    'Pre-treatment',
    'Storage',
    'Stimulation',
    'Site Panel',
    'Cytometer',
    'Acquisition Date',
    'Status'
]


class ChosenFile(object):
    def __init__(self, f, checkbox):
        self.file = f
        self.file_path = f.name
        self.file_name = os.path.basename(f.name)

        # test if file is an FCS file, raise TypeError if not
        try:
            self.flow_data = flowio.FlowData(f.name)
        except:
            raise TypeError("File %s is not an FCS file." % self.file_name)

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

        self.pretreatment = None

        self.storage = None

        self.site_panel = None
        self.site_panel_pk = None

        self.cytometer = None
        self.cytometer_pk = None

        self.acq_date = None

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

        # re-activate the checkbox
        self.checkbox.config(state=Tkinter.ACTIVE)
        self.checkbox.mark_unchecked()

    def mark_as_not_matching(self):
        self.checkbox.config(background='#FFAAAA')

    def mark_as_matching(self):
        self.checkbox.config(background='white')

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


def get_calendar(locale, fwday):
    # instantiate proper calendar class
    if locale is None:
        return calendar.TextCalendar(fwday)
    else:
        return calendar.LocaleTextCalendar(fwday, locale)


class Calendar(ttk.Frame):
    """
    Simple calendar using ttk Treeview together with calendar and datetime
    classes.

    Graciously borrowed from:
    http://svn.python.org/projects/sandbox/trunk/ttk-gsoc/samples/ttkcalendar.py
    """
    datetime = calendar.datetime.datetime
    timedelta = calendar.datetime.timedelta

    def __init__(self, master=None, variable=None, **kw):
        """
        WIDGET-SPECIFIC OPTIONS

            locale, firstweekday, year, month, selectbackground,
            selectforeground
        """
        # remove custom options from kw before initializating ttk.Frame
        fwday = kw.pop('firstweekday', calendar.MONDAY)
        year = kw.pop('year', self.datetime.now().year)
        month = kw.pop('month', self.datetime.now().month)
        locale = kw.pop('locale', None)
        sel_bg = kw.pop('selectbackground', '#ecffc4')
        sel_fg = kw.pop('selectforeground', '#05640e')

        self._date = self.datetime(year, month, 1)
        self._selection = None  # no date selected

        ttk.Frame.__init__(self, master, **kw)

        self._variable = variable

        self._cal = get_calendar(locale, fwday)

        self.__setup_styles()       # creates custom styles
        self.__place_widgets()      # pack/grid used widgets
        self.__config_calendar()    # adjust calendar columns and setup tags
        # configure a canvas, and proper bindings, for selecting dates
        self._font = tkFont.Font()
        self._canvas = Tkinter.Canvas(
            self._calendar,
            background=sel_bg,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="black")
        self._canvas.text = self._canvas.create_text(
            0,
            0,
            fill=sel_fg,
            anchor='w')

        self.__setup_selection()

        # store items ids, used for insertion later
        self._items = [self._calendar.insert(
            '', 'end', values='') for _ in range(6)]
        # insert dates in the currently empty calendar
        self._build_calendar()

        # set the minimal size for the widget
        self._calendar.bind('<Map>', self.__minsize)

    def __setitem__(self, item, value):
        if item in ('year', 'month'):
            raise AttributeError("attribute '%s' is not writeable" % item)
        elif item == 'selectbackground':
            self._canvas['background'] = value
        elif item == 'selectforeground':
            self._canvas.itemconfigure(self._canvas.text, item=value)
        else:
            ttk.Frame.__setitem__(self, item, value)

    def __getitem__(self, item):
        if item in ('year', 'month'):
            return getattr(self._date, item)
        elif item == 'selectbackground':
            return self._canvas['background']
        elif item == 'selectforeground':
            return self._canvas.itemcget(self._canvas.text, 'fill')
        else:
            r = ttk.tclobjs_to_py({item: ttk.Frame.__getitem__(self, item)})
            return r[item]

    def __setup_styles(self):
        # custom ttk styles
        style = ttk.Style(self.master)
        arrow_layout = lambda direction: (
            [
                (
                    'Button.focus',
                    {
                        'children': [('Button.%sarrow' % direction, None)]
                    }
                )
            ]
        )
        style.layout('L.TButton', arrow_layout('left'))
        style.layout('R.TButton', arrow_layout('right'))

    def __place_widgets(self):
        # header frame and its widgets
        hframe = ttk.Frame(self)
        lbtn = ttk.Button(hframe, style='L.TButton', command=self._prev_month)
        rbtn = ttk.Button(hframe, style='R.TButton', command=self._next_month)
        self._header = ttk.Label(hframe, width=15, anchor='center')
        # the calendar
        self._calendar = ttk.Treeview(show='', selectmode='none', height=7)

        # pack the widgets
        hframe.pack(in_=self, side='top', pady=4, anchor='center')
        lbtn.grid(in_=hframe)
        self._header.grid(in_=hframe, column=1, row=0, padx=12)
        rbtn.grid(in_=hframe, column=2, row=0)
        self._calendar.pack(in_=self, expand=1, fill='both', side='bottom')

    def __config_calendar(self):
        cols = self._cal.formatweekheader(3).split()
        self._calendar['columns'] = cols
        self._calendar.tag_configure('header', background='grey90')
        self._calendar.insert('', 'end', values=cols, tag='header')
        # adjust its columns width
        font = tkFont.Font()
        max_width = max(font.measure(col) for col in cols)
        for col in cols:
            self._calendar.column(
                col,
                width=max_width,
                minwidth=max_width,
                anchor='e')

    def __setup_selection(self):
        self._canvas.bind(
            '<ButtonPress-1>',
            lambda evt: self._canvas.place_forget())
        self._calendar.bind(
            '<Configure>',
            lambda evt: self._canvas.place_forget())
        self._calendar.bind('<ButtonPress-1>', self._pressed)

    def __minsize(self, evt):
        width, height = self._calendar.master.geometry().split('x')
        height = height[:height.index('+')]
        self._calendar.master.minsize(width, height)

    def _build_calendar(self):
        year, month = self._date.year, self._date.month

        # update header text (Month, YEAR)
        header = self._cal.formatmonthname(year, month, 0)
        self._header['text'] = header.title()

        # update calendar shown dates
        cal = self._cal.monthdayscalendar(year, month)
        for indx, item in enumerate(self._items):
            week = cal[indx] if indx < len(cal) else []
            fmt_week = [('%02d' % day) if day else '' for day in week]
            self._calendar.item(item, values=fmt_week)

    def _show_selection(self, text, bbox):
        """Configure canvas for a new selection."""
        x, y, width, height = bbox

        text_width = self._font.measure(text)

        canvas = self._canvas
        canvas.configure(width=width, height=height-1)
        canvas.coords(canvas.text, width - text_width - 2, height / 2)
        canvas.itemconfigure(canvas.text, text=text)
        canvas.place(in_=self._calendar, x=x-1, y=y-1)

    def clear_selection(self):
        """Clear current selection."""
        self._selection = None
        self._canvas.place_forget()

    # Callbacks

    def _pressed(self, evt):
        """Clicked somewhere in the calendar."""
        x, y, widget = evt.x, evt.y, evt.widget
        item = widget.identify_row(y)
        column = widget.identify_column(x)

        if not column or not item in self._items:
            # clicked in the weekdays row or just outside the columns
            return

        item_values = widget.item(item)['values']
        if not len(item_values):  # row is empty for this month
            return

        text = item_values[int(column[1]) - 1]
        if not text:  # date is empty
            return

        bbox = widget.bbox(item, column)
        if not bbox:  # calendar not visible yet
            return

        # update and then show selection
        text = '%02d' % text
        self._selection = (text, item, column)
        self._show_selection(text, bbox)
        if self._variable:
            self._variable.set(
                "%d-%d-%d" % (
                    self._date.year,
                    self._date.month,
                    int(self._selection[0])))

    def _prev_month(self):
        """Updated calendar to show the previous month."""
        self._canvas.place_forget()

        self._date = self._date - self.timedelta(days=1)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        self._build_calendar()  # reconstuct calendar

    def _next_month(self):
        """Update calendar to show the next month."""
        self._canvas.place_forget()

        year, month = self._date.year, self._date.month
        self._date = self._date + self.timedelta(
            days=calendar.monthrange(year, month)[1] + 1)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        self._build_calendar()  # reconstruct calendar

    # Properties

    @property
    def selection(self):
        """Return a datetime representing the current selected date."""
        if not self._selection:
            return None

        year, month = self._date.year, self._date.month
        return self.datetime(year, month, int(self._selection[0]))


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
        self.cytometer_dict = dict()
        self.specimen_dict = dict()
        self.stimulation_dict = dict()

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

        self.pretreatment_menu = None
        self.pretreatment_selection = Tkinter.StringVar()
        self.pretreatment_selection.trace(
            "w",
            self.update_add_to_queue_button_state)

        self.storage_menu = None
        self.storage_selection = Tkinter.StringVar()
        self.storage_selection.trace(
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
            self.site_selection_changed)

        self.cytometer_menu = None
        self.cytometer_selection = Tkinter.StringVar()
        self.cytometer_selection.trace(
            "w",
            self.update_add_to_queue_button_state)

        self.acquisition_cal = None
        self.acquisition_date_selection = Tkinter.StringVar()
        self.acquisition_date_selection.trace(
            "w",
            self.update_add_to_queue_button_state)

        # can't call super on old-style class, call parent init directly
        Tkinter.Frame.__init__(self, master)
        if sys.platform == 'linux2':
            pass
        else:
            self.master.iconbitmap(ICON_PATH)
        self.master.title('ReFlow Client - ' + VERSION)
        self.master.minsize(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.master.config(bg=BACKGROUND_COLOR)

        self.menu_bar = Tkinter.Menu(master)
        self.master.config(menu=self.menu_bar)

        self.upload_button = None
        self.clear_selected_queue_button = None
        self.queue_tree = None
        self.upload_progress_bar = None
        self.view_metadata_button = None
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

        # overall project frame
        project_frame = Tkinter.Frame(
            metadata_frame,
            bg=BACKGROUND_COLOR)

        # project label frame
        project_chooser_label_frame = Tkinter.Frame(
            project_frame,
            bg=BACKGROUND_COLOR)
        project_chooser_label = Tkinter.Label(
            project_chooser_label_frame,
            text='Project:',
            bg=BACKGROUND_COLOR,
            width=LABEL_WIDTH,
            anchor=Tkinter.E)
        project_chooser_label.pack(side='left')
        project_chooser_label_frame.pack(side='left', fill='x')

        # project chooser listbox frame
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

        # overall site frame
        site_frame = Tkinter.Frame(metadata_frame, bg=BACKGROUND_COLOR)

        # site label frame
        site_chooser_label_frame = Tkinter.Frame(
            site_frame,
            bg=BACKGROUND_COLOR)
        site_chooser_label = Tkinter.Label(
            site_chooser_label_frame,
            text='Site:',
            bg=BACKGROUND_COLOR,
            width=LABEL_WIDTH,
            anchor=Tkinter.E)
        site_chooser_label.pack(side='left')
        site_chooser_label_frame.pack(side='left', fill='x')

        # site chooser listbox frame
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

        # overall subject frame
        subject_frame = Tkinter.Frame(metadata_frame, bg=BACKGROUND_COLOR)

        # subject label frame
        subject_chooser_label_frame = Tkinter.Frame(
            subject_frame,
            bg=BACKGROUND_COLOR)
        subject_chooser_label = Tkinter.Label(
            subject_chooser_label_frame,
            text='Subject:',
            bg=BACKGROUND_COLOR,
            width=LABEL_WIDTH,
            anchor=Tkinter.E)
        subject_chooser_label.pack(side='left')
        subject_chooser_label_frame.pack(side='left', fill='x')

        # subject chooser listbox frame
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

        # visit label frame
        visit_chooser_label_frame = Tkinter.Frame(
            visit_frame,
            bg=BACKGROUND_COLOR)
        visit_chooser_label = Tkinter.Label(
            visit_chooser_label_frame,
            text='Visit:',
            bg=BACKGROUND_COLOR,
            width=LABEL_WIDTH,
            anchor=Tkinter.E)
        visit_chooser_label.pack(side='left')
        visit_chooser_label_frame.pack(side='left', fill='x')

        # visit chooser listbox frame
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

        # specimen label frame
        specimen_chooser_label_frame = Tkinter.Frame(
            specimen_frame,
            bg=BACKGROUND_COLOR)
        specimen_chooser_label = Tkinter.Label(
            specimen_chooser_label_frame,
            text='Specimen:',
            bg=BACKGROUND_COLOR,
            width=LABEL_WIDTH,
            anchor=Tkinter.E)
        specimen_chooser_label.pack(side='left')
        specimen_chooser_label_frame.pack(side='left', fill='x')

        # specimen chooser listbox frame
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

        # overall pretreatment frame
        pretreatment_frame = Tkinter.Frame(
            metadata_frame,
            bg=BACKGROUND_COLOR)

        # pretreatment label frame
        pretreatment_chooser_label_frame = Tkinter.Frame(
            pretreatment_frame,
            bg=BACKGROUND_COLOR)
        pretreatment_chooser_label = Tkinter.Label(
            pretreatment_chooser_label_frame,
            text='Pre-treatment:',
            bg=BACKGROUND_COLOR,
            width=LABEL_WIDTH,
            anchor=Tkinter.E)
        pretreatment_chooser_label.pack(side='left')
        pretreatment_chooser_label_frame.pack(side='left', fill='x')

        # pretreatment chooser listbox frame
        pretreatment_chooser_frame = Tkinter.Frame(
            pretreatment_frame,
            bg=BACKGROUND_COLOR)
        self.pretreatment_menu = Tkinter.OptionMenu(
            pretreatment_chooser_frame,
            self.pretreatment_selection,
            '')
        self.pretreatment_menu.config(bg=BACKGROUND_COLOR)
        self.pretreatment_menu.pack(fill='x', expand=True)
        pretreatment_chooser_frame.pack(fill='x', expand=True)

        pretreatment_frame.pack(side='top', fill='x', expand=True)

        # overall storage frame
        storage_frame = Tkinter.Frame(
            metadata_frame,
            bg=BACKGROUND_COLOR)

        # storage label frame
        storage_chooser_label_frame = Tkinter.Frame(
            storage_frame,
            bg=BACKGROUND_COLOR)
        storage_chooser_label = Tkinter.Label(
            storage_chooser_label_frame,
            text='Storage:',
            bg=BACKGROUND_COLOR,
            width=LABEL_WIDTH,
            anchor=Tkinter.E)
        storage_chooser_label.pack(side='left')
        storage_chooser_label_frame.pack(side='left', fill='x')

        # storage chooser listbox frame
        storage_chooser_frame = Tkinter.Frame(
            storage_frame,
            bg=BACKGROUND_COLOR)
        self.storage_menu = Tkinter.OptionMenu(
            storage_chooser_frame,
            self.storage_selection,
            '')
        self.storage_menu.config(bg=BACKGROUND_COLOR)
        self.storage_menu.pack(fill='x', expand=True)
        storage_chooser_frame.pack(fill='x', expand=True)

        storage_frame.pack(side='top', fill='x', expand=True)

        # overall stimulation frame
        stimulation_frame = Tkinter.Frame(
            metadata_frame,
            bg=BACKGROUND_COLOR)

        # stimulation label frame
        stimulation_chooser_label_frame = Tkinter.Frame(
            stimulation_frame,
            bg=BACKGROUND_COLOR)
        stimulation_chooser_label = Tkinter.Label(
            stimulation_chooser_label_frame,
            text='Stimulation:',
            bg=BACKGROUND_COLOR,
            width=LABEL_WIDTH,
            anchor=Tkinter.E)
        stimulation_chooser_label.pack(side='left')
        stimulation_chooser_label_frame.pack(side='left', fill='x')

        # stimulation chooser listbox frame
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

        # site_panel label frame
        site_panel_chooser_label_frame = Tkinter.Frame(
            site_panel_frame,
            bg=BACKGROUND_COLOR)
        site_panel_chooser_label = Tkinter.Label(
            site_panel_chooser_label_frame,
            text='Site Panel:',
            bg=BACKGROUND_COLOR,
            width=LABEL_WIDTH,
            anchor=Tkinter.E)
        site_panel_chooser_label.pack(side='left')
        site_panel_chooser_label_frame.pack(side='left', fill='x')

        # site_panel chooser listbox frame
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

        # overall cytometer frame
        cytometer_frame = Tkinter.Frame(
            metadata_frame,
            bg=BACKGROUND_COLOR)

        # cytometer label frame
        cytometer_chooser_label_frame = Tkinter.Frame(
            cytometer_frame,
            bg=BACKGROUND_COLOR)
        cytometer_chooser_label = Tkinter.Label(
            cytometer_chooser_label_frame,
            text='Cytometer:',
            bg=BACKGROUND_COLOR,
            width=LABEL_WIDTH,
            anchor=Tkinter.E)
        cytometer_chooser_label.pack(side='left')
        cytometer_chooser_label_frame.pack(side='left', fill='x')

        # cytometer chooser listbox frame
        cytometer_chooser_frame = Tkinter.Frame(
            cytometer_frame,
            bg=BACKGROUND_COLOR)
        self.cytometer_menu = Tkinter.OptionMenu(
            cytometer_chooser_frame,
            self.cytometer_selection,
            '')
        self.cytometer_menu.config(bg=BACKGROUND_COLOR)
        self.cytometer_menu.pack(fill='x', expand=True)
        cytometer_chooser_frame.pack(fill='x', expand=True)

        cytometer_frame.pack(side='top', fill='x', expand=True)

        # overall acquisition date frame
        acquisition_date_frame = Tkinter.Frame(
            metadata_frame,
            bg=BACKGROUND_COLOR)

        # acq date label frame
        acquisition_date_chooser_label_frame = Tkinter.Frame(
            acquisition_date_frame,
            bg=BACKGROUND_COLOR)
        acquisition_date_chooser_label = Tkinter.Label(
            acquisition_date_chooser_label_frame,
            text='Acquisition Date:',
            bg=BACKGROUND_COLOR,
            width=LABEL_WIDTH,
            anchor=Tkinter.E)
        acquisition_date_chooser_label.pack(
            side='top',
            fill=Tkinter.BOTH,
            anchor=Tkinter.N)
        acquisition_date_chooser_label_frame.pack(
            side='left',
            fill=Tkinter.BOTH,
            anchor=Tkinter.N)

        # acquisition_date chooser frame
        acquisition_date_chooser_frame = Tkinter.Frame(
            acquisition_date_frame,
            bg=BACKGROUND_COLOR)
        self.acquisition_cal = Calendar(
            master=acquisition_date_chooser_frame,
            variable=self.acquisition_date_selection,
            firstweekday=calendar.SUNDAY,
        )
        self.acquisition_cal.pack(expand=1, fill='both')
        acquisition_date_chooser_frame.pack(fill='x', expand=True)

        acquisition_date_frame.pack(side='top', fill='x', expand=True)

        self.load_user_projects()
        self.load_specimens()
        self.load_pretreatment()
        self.load_storage()

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
        self.view_metadata_button = ttk.Button(
            file_chooser_button_frame,
            text='View Metadata',
            command=self.view_metadata)
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
        self.view_metadata_button.pack(side='right')
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
            self.queue_tree.column(
                header,
                minwidth=0,
                width=25,
                stretch=Tkinter.TRUE)

        # setup Treeview tag styles, it's the only way to change colors/fonts
        # Note: it changes the entire row, individual cells cannot be
        # formatted
        self.queue_tree.tag_configure(
            tagname='pending',
            font=('TkDefaultFont', 11, 'bold'))
        self.queue_tree.tag_configure(
            tagname='error',
            font=('TkDefaultFont', 11, 'bold'),
            foreground='red')
        self.queue_tree.tag_configure(
            tagname='complete',
            font=('TkDefaultFont', 11, 'italic'),
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
            file_path = cb.file_path
            del(self.file_dict[file_path])
            cb.destroy()

        # and re-order items to not leave blank spaces
        i = 0
        cb_dict = self.file_list_canvas.children
        for cb in sorted(cb_dict.values(), key=lambda x: x.cget('text')):
            if isinstance(cb, MyCheckbutton):
                self.file_list_canvas.create_window(
                    10,
                    (24 * i),
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
        # Some Tkinter bug in Windows where askopenfiles throws an IOError
        # Looks like this will be fixed in the next Python release 2.7.7 ???
        # See http://bugs.python.org/issue5712
        if sys.platform == 'win32':
            selected_files = []
            selected_file_paths = tkFileDialog.askopenfilenames()
            f = Tkinter.Frame()
            selected_file_paths = f.tk.splitlist(selected_file_paths)
            for path in selected_file_paths:
                f = open(path)
                selected_files.append(f)
        else:
            selected_files = tkFileDialog.askopenfiles('r')

        if len(selected_files) < 1:
            return

        # clear the canvas and the relevant file_dict keys
        self.file_list_canvas.delete(Tkinter.ALL)
        for k in self.file_list_canvas.children.keys():
            file_path = self.file_list_canvas.children[k].file_path
            del(self.file_dict[file_path])
            del(self.file_list_canvas.children[k])

        for i, f in enumerate(selected_files):
            cb = MyCheckbutton(
                self.file_list_canvas,
                text=os.path.basename(f.name),
                file_path=f.name
            )

            try:
                chosen_file = ChosenFile(f, cb)
            except TypeError:
                del cb
                continue

            # bind to our canvas mouse function
            # to keep scrolling working when the mouse is over a checkbox
            cb.bind('<MouseWheel>', self._on_mousewheel)
            self.file_list_canvas.create_window(
                10,
                (24 * i),
                anchor='nw',
                window=cb
            )

            self.file_dict[chosen_file.file_path] = chosen_file

        # update scroll region
        self.file_list_canvas.config(
            scrollregion=(0, 0, 1000, len(selected_files)*20))

        # clear the acquisition date and subject
        self.subject_selection.set('')
        self.acquisition_date_selection.set('')
        self.acquisition_cal.clear_selection()

        self.mark_site_panel_matches()
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
        self.cytometer_menu['menu'].delete(0, 'end')

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

    def load_pretreatment(self):
        pretreatment_list = ['In vitro', 'Ex vivo']
        self.pretreatment_menu['menu'].delete(0, 'end')
        for item in pretreatment_list:
            self.pretreatment_menu['menu'].add_command(
                label=item,
                command=lambda value=item:
                self.pretreatment_selection.set(value))

    def load_storage(self):
        storage_list = ['Fresh', 'Cryopreserved']
        self.storage_menu['menu'].delete(0, 'end')
        for item in storage_list:
            self.storage_menu['menu'].add_command(
                label=item,
                command=lambda value=item:
                self.storage_selection.set(value))

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

        self.cytometer_menu['menu'].delete(0, 'end')
        self.cytometer_selection.set('')
        self.cytometer_dict.clear()

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
            response = rest.get_cytometers(*rest_args, **rest_kwargs)
        except Exception, e:
            print e
            return

        if not 'data' in response:
            return

        for result in response['data']:
            self.cytometer_dict[result['cytometer_name']] = result['id']
        for panel_name in sorted(self.cytometer_dict.keys()):
            self.cytometer_menu['menu'].add_command(
                label=panel_name,
                command=lambda value=panel_name:
                self.cytometer_selection.set(value))

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
                not self.pretreatment_selection.get() or \
                not self.storage_selection.get() or \
                not self.stimulation_selection.get() or \
                not self.site_panel_selection.get() or \
                not self.cytometer_selection.get() or \
                not self.acquisition_date_selection.get():
            active = False
        if len(self.file_list_canvas.children) == 0:
            active = False

        if active:
            self.add_to_queue_button.config(state='active')
        else:
            self.add_to_queue_button.config(state='disabled')

    def mark_site_panel_matches(self):
        """
        Change text color of FCS files' in file chooser frame based
        on whether the file matches the selected site panel
        """
        site_panel_selection = self.site_panel_selection.get()
        if not site_panel_selection:
            return

        site_panel_pk = self.site_panel_dict[site_panel_selection]

        for fcs_file in self.file_dict:
            param_dict = {}
            metadata = self.file_dict[fcs_file].flow_data.text
            for key in metadata:
                matches = re.search('^P(\d+)([N,S])$', key, flags=re.IGNORECASE)
                if matches:
                    channel_number = int(matches.group(1))
                    n_or_s = str.lower(matches.group(2))
                    if not param_dict.has_key(channel_number):
                        param_dict[channel_number] = {}
                    param_dict[channel_number][n_or_s] = metadata[key]
            is_match = rest.is_site_panel_match(
                self.host,
                self.token,
                site_panel_pk,
                param_dict)

            if is_match:
                self.file_dict[fcs_file].mark_as_matching()
            else:
                self.file_dict[fcs_file].mark_as_not_matching()

    def site_selection_changed(self, *args, **kwargs):
        self.mark_site_panel_matches()
        self.update_add_to_queue_button_state(*args, **kwargs)

    def view_metadata(self):
        message_win = Tkinter.Toplevel()
        meta_frame = Tkinter.Frame(message_win)
        meta_scroll_bar = Tkinter.Scrollbar(
            meta_frame,
            orient='vertical')
        metadata_text = Tkinter.Text(
            meta_frame,
            bg=BACKGROUND_COLOR,
            yscrollcommand=meta_scroll_bar.set)
        metadata_text.tag_configure('alt-row', background=ROW_ALT_COLOR)
        metadata_text.tag_configure('file-name', font=('TkDefaultFont', 18, 'bold'))

        for k, v in self.file_list_canvas.children.items():
            if isinstance(v, MyCheckbutton):
                if v.is_checked() and v.cget('state') != Tkinter.DISABLED:
                    # get metadata for only the selected checkboxes
                    chosen_file = self.file_dict[v.file_path]
                    metadata_text.insert(Tkinter.END, chosen_file.file_name, ("file-name"))
                    metadata_text.insert(Tkinter.END, '\n')
                    metadata_dict = chosen_file.flow_data.text
                    for i, key in enumerate(sorted(metadata_dict)):
                        line_start = metadata_text.index(Tkinter.INSERT)
                        metadata_text.insert(Tkinter.END, key + ": ")
                        metadata_text.insert(
                            Tkinter.END,
                            unicode(metadata_dict[key], errors='replace'))
                        metadata_text.insert(Tkinter.END, '\n')
                        if i % 2:
                            metadata_text.tag_add("alt-row", line_start, "end")
                        else:
                            metadata_text.tag_remove("alt-row", line_start, "end")

        meta_scroll_bar.config(command=metadata_text.yview)
        meta_scroll_bar.pack(side='right', fill='y')
        metadata_text.config(
            state=Tkinter.DISABLED,
            background="white",
            highlightthickness=1,
            highlightbackground=BORDER_COLOR)

        meta_frame.pack(
            fill=Tkinter.BOTH,
            expand=Tkinter.TRUE,
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)

        message_win.title('Metadata')
        message_win.minsize(width=480, height=320)
        message_win.config(bg=BACKGROUND_COLOR)

        metadata_text.pack(
            anchor='nw',
            fill=Tkinter.BOTH,
            expand=Tkinter.TRUE,
            padx=0,
            pady=0
        )

        # make sure there's a way to destroy the dialog
        message_button = ttk.Button(
            message_win,
            text='OK',
            command=message_win.destroy)
        message_button.pack(
            anchor=Tkinter.E,
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)

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

                    c_file.pretreatment = self.pretreatment_selection.get()

                    c_file.storage = self.storage_selection.get()

                    c_file.stimulation = self.stimulation_selection.get()
                    c_file.stimulation_pk = \
                        self.stimulation_dict[c_file.stimulation]

                    c_file.site_panel = self.site_panel_selection.get()
                    c_file.site_panel_pk = \
                        self.site_panel_dict[c_file.site_panel]

                    c_file.cytometer = self.cytometer_selection.get()
                    c_file.cytometer_pk = \
                        self.cytometer_dict[c_file.cytometer]

                    c_file.acq_date = self.acquisition_date_selection.get()

                    # Populate our tree item,
                    item = list()
                    item.append(c_file.file_name)
                    item.append(c_file.project)
                    item.append(c_file.subject)
                    item.append(c_file.visit)
                    item.append(c_file.specimen)
                    item.append(c_file.pretreatment)
                    item.append(c_file.storage)
                    item.append(c_file.stimulation)
                    item.append(c_file.site_panel)
                    item.append(c_file.cytometer)
                    item.append(c_file.acq_date)
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

    def clear_selected_queue(self):
        # get_children returns a tuple of item IDs from the tree
        tree_items = self.queue_tree.selection()

        # the items are the tree rows
        for item in tree_items:
            # the items are the row IDs, which we set as the file's full path
            try:
                chosen_file = self.file_dict[item]
            except Exception, e:
                self.queue_tree.delete(item)
                continue

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
            # only upload files with status=="Pending"
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
                continue

            if not chosen_file.project or \
                    not chosen_file.subject_pk or \
                    not chosen_file.site_panel_pk or \
                    not chosen_file.cytometer_pk or \
                    not chosen_file.acq_date or \
                    not chosen_file.specimen_pk or \
                    not chosen_file.pretreatment or \
                    not chosen_file.storage or \
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
                'cytometer_pk': str(chosen_file.cytometer_pk),
                'visit_type_pk': str(chosen_file.visit_pk),
                'specimen_pk': str(chosen_file.specimen_pk),
                'pretreatment': str(chosen_file.pretreatment),
                'storage': str(chosen_file.storage),
                'stimulation_pk': str(chosen_file.stimulation_pk),
                'acquisition_date': str(chosen_file.acq_date)
            }

            try:
                response_dict = rest.post_sample(
                    *rest_args,
                    **rest_kwargs
                )
            except Exception, e:
                print e

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