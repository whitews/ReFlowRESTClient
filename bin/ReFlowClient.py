import Tkinter as tk
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


class Application(tk.Frame):

    def __init__(self, master):
        # a bit weird, but we'll use the names (project, site, etc.) as the key, pk as the value
        # for the four choice dictionaries below.
        # we need the names to be unique (and they should be) and
        # it's more convenient to lookup by key using the name to find the selection.
        self.project_dict = dict()
        self.site_dict = dict()
        self.subject_dict = dict()
        self.visit_dict = dict()
        self.panel_dict = dict()
        self.specimen_dict = dict()
        self.stimulation_dict = dict()

        # can't call super on old-style class, call parent init directly
        tk.Frame.__init__(self, master)
        self.master.iconbitmap(ICON_PATH)
        self.master.title('ReFlow Client - ' + VERSION)
        self.master.minsize(width=954, height=640)
        self.master.config(bg=BACKGROUND_COLOR)

        self.menuBar = tk.Menu(master)
        self.master.config(menu=self.menuBar)

        self.s = ttk.Style()
        self.s.map('Inactive.TButton', foreground=[('disabled', INACTIVE_FOREGROUND_COLOR)])

        self.pack()
        self.loadLoginFrame()
        #self.loadMainFrame()

    def loadLoginFrame(self):
        self.loginFrame = tk.Frame(bg=BACKGROUND_COLOR)

        self.logoImage = ImageTk.PhotoImage(Image.open(LOGO_PATH))
        self.logoLabel = tk.Label(self.loginFrame, image=self.logoImage)
        self.logoLabel.config(bg=BACKGROUND_COLOR)
        self.logoLabel.pack(side='top', pady=PAD_EXTRA_LARGE)

        self.hostEntryFrame = tk.Frame(self.loginFrame, bg=BACKGROUND_COLOR)
        self.hostLabel = tk.Label(
            self.hostEntryFrame,
            text='Hostname',
            bg=BACKGROUND_COLOR,
            width=8,
            anchor='e')
        self.hostLabel.pack(side='left')
        self.hostEntry = tk.Entry(
            self.hostEntryFrame,
            highlightbackground=BACKGROUND_COLOR,
            width=24)
        self.hostEntry.pack(padx=PAD_SMALL)
        self.hostEntryFrame.pack(pady=PAD_SMALL)

        self.userEntryFrame = tk.Frame(self.loginFrame, bg=BACKGROUND_COLOR)
        self.userLabel = tk.Label(
            self.userEntryFrame,
            text='Username',
            bg=BACKGROUND_COLOR,
            width=8,
            anchor='e')
        self.userLabel.pack(side='left')
        self.userEntry = tk.Entry(
            self.userEntryFrame,
            highlightbackground=BACKGROUND_COLOR,
            width=24)
        self.userEntry.pack(padx=PAD_SMALL)
        self.userEntryFrame.pack(pady=PAD_SMALL)

        self.passwordEntryFrame = tk.Frame(self.loginFrame, bg=BACKGROUND_COLOR)
        self.passwordLabel = tk.Label(
            self.passwordEntryFrame,
            text='Password',
            bg=BACKGROUND_COLOR,
            width=8,
            anchor='e')
        self.passwordLabel.pack(side='left')
        self.passwordEntry = tk.Entry(
            self.passwordEntryFrame,
            show='*',
            highlightbackground=BACKGROUND_COLOR,
            width=24)
        self.passwordEntry.pack(padx=PAD_SMALL)
        self.passwordEntryFrame.pack(pady=PAD_SMALL)

        self.loginButtonFrame = tk.Frame(self.loginFrame, bg=BACKGROUND_COLOR)
        self.loginButtonLabel = tk.Label(self.loginButtonFrame, bg=BACKGROUND_COLOR)
        self.loginButton = ttk.Button(
            self.loginButtonLabel,
            text='Login',
            command=self.login)
        self.loginButton.pack()
        self.loginButtonLabel.pack(side='right')
        self.loginButtonFrame.pack(fill='x')

        self.loginFrame.place(in_=self.master, anchor='c', relx=.5, rely=.5)

    def login(self):
        self.token = None
        self.host = self.hostEntry.get()
        self.username = self.userEntry.get()
        password = self.passwordEntry.get()
        try:
            self.token = rest.login(self.host, self.username, password)
        except Exception, e:
            print e
        if not self.token:
            tkMessageBox.showwarning(
                'Login Failed',
                ' Check that the hostname, username, and password are correct')
            return
        self.loginFrame.destroy()
        self.loadMainFrame()

    def loadMainFrame(self):
        self.mainFrame = tk.Frame(self.master, bg=BACKGROUND_COLOR)
        self.mainFrame.pack(
            fill='both',
            expand=True,
            anchor='n',
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)

        self.topFrame = tk.Frame(self.mainFrame, bg=BACKGROUND_COLOR)
        self.topFrame.pack(fill='both', expand=False, anchor='n', padx=0, pady=0)

        self.middleFrame = tk.Frame(self.mainFrame, bg=BACKGROUND_COLOR)
        self.middleFrame.pack(fill='both', expand=True, anchor='n', padx=0, pady=0)

        self.bottomFrame = tk.Frame(self.mainFrame, bg=BACKGROUND_COLOR)
        self.bottomFrame.pack(fill='both', expand=False, anchor='n', padx=0, pady=0)

        # Metadata frame - for choosing project/subject/site etc.
        self.metadataFrame = tk.Frame(self.topFrame, bg=BACKGROUND_COLOR)
        # Start metadata choices, including:
        #    - project
        #    - site
        #    - subject
        #    - visit

        # overall project frame (on bottom left of main window)
        self.projectFrame = tk.Frame(self.metadataFrame, bg=BACKGROUND_COLOR)

        # project label frame (top of project chooser frame)
        self.projectChooserLabelFrame = tk.Frame(self.projectFrame, bg=BACKGROUND_COLOR)
        self.projectChooserLabel = tk.Label(
            self.projectChooserLabelFrame,
            text='Choose Project',
            bg=BACKGROUND_COLOR)
        self.projectChooserLabel.pack(side='left')
        self.projectChooserLabelFrame.pack(fill='x')

        # project chooser listbox frame (bottom of project chooser frame)
        self.projectChooserFrame = tk.Frame(self.projectFrame, bg=BACKGROUND_COLOR)
        self.projectScrollBar = tk.Scrollbar(self.projectChooserFrame, orient='vertical')
        self.projectListBox = tk.Listbox(
            self.projectChooserFrame,
            exportselection=0,
            yscrollcommand=self.projectScrollBar.set,
            relief='flat',
            width=16,
            height=3,
            borderwidth=0,
            highlightcolor=HIGHLIGHT_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1)
        self.projectListBox.bind('<<ListboxSelect>>', self.updateMetadata)
        self.projectScrollBar.config(command=self.projectListBox.yview)
        self.projectScrollBar.pack(side='right', fill='y')
        self.projectListBox.pack(fill='x', expand=True)
        self.projectChooserFrame.pack(fill='x', expand=True)

        self.projectFrame.pack(side='left', fill='x', expand=True)

        # overall site frame (on bottom, 2nd from left of main window
        self.siteFrame = tk.Frame(self.metadataFrame, bg=BACKGROUND_COLOR)

        # site label frame (top of site chooser frame)
        self.siteChooserLabelFrame = tk.Frame(self.siteFrame, bg=BACKGROUND_COLOR)
        self.siteChooserLabel = tk.Label(
            self.siteChooserLabelFrame,
            text='Choose Site',
            bg=BACKGROUND_COLOR)
        self.siteChooserLabel.pack(side='left')
        self.siteChooserLabelFrame.pack(fill='x')

        # site chooser listbox frame (bottom of site chooser frame)
        self.siteChooserFrame = tk.Frame(self.siteFrame, bg=BACKGROUND_COLOR)
        self.siteScrollBar = tk.Scrollbar(self.siteChooserFrame, orient='vertical')
        self.siteListBox = tk.Listbox(
            self.siteChooserFrame,
            exportselection=0,
            yscrollcommand=self.siteScrollBar.set,
            relief='flat',
            width=16,
            height=3,
            borderwidth=0,
            highlightcolor=HIGHLIGHT_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1)
        self.siteListBox.bind('<<ListboxSelect>>', self.siteSelectionChanged)
        self.siteScrollBar.config(command=self.siteListBox.yview)
        self.siteScrollBar.pack(side='right', fill='y')
        self.siteListBox.pack(fill='x', expand=True)
        self.siteChooserFrame.pack(fill='x', expand=True)

        self.siteFrame.pack(side='left', fill='x', expand=True)

        # overall subject frame (on bottom, 2nd from left of main window
        self.subjectFrame = tk.Frame(self.metadataFrame, bg=BACKGROUND_COLOR)

        # subject label frame (top of subject chooser frame)
        self.subjectChooserLabelFrame = tk.Frame(self.subjectFrame, bg=BACKGROUND_COLOR)
        self.subjectChooserLabel = tk.Label(
            self.subjectChooserLabelFrame,
            text='Choose Subject',
            bg=BACKGROUND_COLOR)
        self.subjectChooserLabel.pack(side='left')
        self.subjectChooserLabelFrame.pack(fill='x')

        # subject chooser listbox frame (bottom of subject chooser frame)
        self.subjectChooserFrame = tk.Frame(self.subjectFrame, bg=BACKGROUND_COLOR)
        self.subjectScrollBar = tk.Scrollbar(self.subjectChooserFrame, orient='vertical')
        self.subjectListBox = tk.Listbox(
            self.subjectChooserFrame,
            exportselection=0,
            yscrollcommand=self.subjectScrollBar.set,
            relief='flat',
            width=16,
            height=3,
            borderwidth=0,
            highlightcolor=HIGHLIGHT_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1)
        self.subjectListBox.bind('<<ListboxSelect>>', self.updateUploadButtonState)
        self.subjectScrollBar.config(command=self.subjectListBox.yview)
        self.subjectScrollBar.pack(side='right', fill='y')
        self.subjectListBox.pack(fill='x', expand=True)
        self.subjectChooserFrame.pack(fill='x', expand=True)

        self.subjectFrame.pack(side='left', fill='x', expand=True)

        # overall visit frame
        self.visitFrame = tk.Frame(self.metadataFrame, bg=BACKGROUND_COLOR)

        # visit label frame (top of visit chooser frame)
        self.visitChooserLabelFrame = tk.Frame(self.visitFrame, bg=BACKGROUND_COLOR)
        self.visitChooserLabel = tk.Label(
            self.visitChooserLabelFrame,
            text='Choose Visit',
            bg=BACKGROUND_COLOR)
        self.visitChooserLabel.pack(side='left')
        self.visitChooserLabelFrame.pack(fill='x')

        # visit chooser listbox frame (bottom of visit chooser frame)
        self.visitChooserFrame = tk.Frame(self.visitFrame, bg=BACKGROUND_COLOR)
        self.visitScrollBar = tk.Scrollbar(self.visitChooserFrame, orient='vertical')
        self.visitListBox = tk.Listbox(
            self.visitChooserFrame,
            exportselection=0,
            yscrollcommand=self.visitScrollBar.set,
            relief='flat',
            width=16,
            height=3,
            borderwidth=0,
            highlightcolor=HIGHLIGHT_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1)
        self.visitListBox.bind('<<ListboxSelect>>', self.updateUploadButtonState)
        self.visitScrollBar.config(command=self.visitListBox.yview)
        self.visitScrollBar.pack(side='right', fill='y')
        self.visitListBox.pack(fill='x', expand=True)
        self.visitChooserFrame.pack(fill='x', expand=True)

        self.visitFrame.pack(side='left', fill='x', expand=True)

        # overall specimen frame
        self.specimenFrame = tk.Frame(self.metadataFrame, bg=BACKGROUND_COLOR)

        # specimen label frame (top of specimen chooser frame)
        self.specimenChooserLabelFrame = tk.Frame(self.specimenFrame, bg=BACKGROUND_COLOR)
        self.specimenChooserLabel = tk.Label(
            self.specimenChooserLabelFrame,
            text='Choose Specimen',
            bg=BACKGROUND_COLOR)
        self.specimenChooserLabel.pack(side='left')
        self.specimenChooserLabelFrame.pack(fill='x')

        # specimen chooser listbox frame (bottom of specimen chooser frame)
        self.specimenChooserFrame = tk.Frame(self.specimenFrame, bg=BACKGROUND_COLOR)
        self.specimenScrollBar = tk.Scrollbar(self.specimenChooserFrame, orient='vertical')
        self.specimenListBox = tk.Listbox(
            self.specimenChooserFrame,
            exportselection=0,
            yscrollcommand=self.specimenScrollBar.set,
            relief='flat',
            width=16,
            height=3,
            borderwidth=0,
            highlightcolor=HIGHLIGHT_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1)
        self.specimenListBox.bind('<<ListboxSelect>>', self.updateUploadButtonState)
        self.specimenScrollBar.config(command=self.specimenListBox.yview)
        self.specimenScrollBar.pack(side='right', fill='y')
        self.specimenListBox.pack(fill='x', expand=True)
        self.specimenChooserFrame.pack(fill='x', expand=True)

        self.specimenFrame.pack(side='left', fill='x', expand=True)

        # overall stimulation frame
        self.stimulationFrame = tk.Frame(self.metadataFrame, bg=BACKGROUND_COLOR)

        # stimulation label frame (top of stimulation chooser frame)
        self.stimulationChooserLabelFrame = tk.Frame(self.stimulationFrame, bg=BACKGROUND_COLOR)
        self.stimulationChooserLabel = tk.Label(
            self.stimulationChooserLabelFrame,
            text='Choose Stimulation',
            bg=BACKGROUND_COLOR)
        self.stimulationChooserLabel.pack(side='left')
        self.stimulationChooserLabelFrame.pack(fill='x')

        # stimulation chooser listbox frame (bottom of stimulation chooser frame)
        self.stimulationChooserFrame = tk.Frame(self.stimulationFrame, bg=BACKGROUND_COLOR)
        self.stimulationScrollBar = tk.Scrollbar(self.stimulationChooserFrame, orient='vertical')
        self.simulationListBox = tk.Listbox(
            self.stimulationChooserFrame,
            exportselection=0,
            yscrollcommand=self.stimulationScrollBar.set,
            relief='flat',
            width=16,
            height=3,
            borderwidth=0,
            highlightcolor=HIGHLIGHT_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1)
        self.simulationListBox.bind('<<ListboxSelect>>', self.updateUploadButtonState)
        self.stimulationScrollBar.config(command=self.simulationListBox.yview)
        self.stimulationScrollBar.pack(side='right', fill='y')
        self.simulationListBox.pack(fill='x', expand=True)
        self.stimulationChooserFrame.pack(fill='x', expand=True)

        self.stimulationFrame.pack(side='left', fill='x', expand=True)

        self.loadUserProjects()
        self.loadSpecimens()
        self.loadStimulations()

        self.metadataFrame.pack(
            fill='x',
            expand=False,
            anchor='n',
            padx=PAD_MEDIUM,
            pady=0)

        self.rightFrame = tk.Frame(self.middleFrame, bg=BACKGROUND_COLOR)
        self.rightFrame.pack(
            fill='both',
            expand=True,
            anchor='n',
            side='right',
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)
        self.innerRightFrame = tk.LabelFrame(self.rightFrame, bg=BACKGROUND_COLOR)
        self.innerRightFrame.pack(
            fill='both',
            expand=True,
            anchor='n',
            side='right')

        # session log text box
        self.logFrame = tk.LabelFrame(self.bottomFrame, bg=BACKGROUND_COLOR, text='Session Log')
        self.logVerticalScrollBar = tk.Scrollbar(self.logFrame, orient='vertical')
        self.logHorizontalScrollBar = tk.Scrollbar(self.logFrame, orient='horizontal')
        self.uploadLogText = tk.Text(
            self.logFrame,
            xscrollcommand=self.logHorizontalScrollBar.set,
            yscrollcommand=self.logVerticalScrollBar.set,
            height=10,
            borderwidth=0,
            highlightthickness=0,
            highlightbackground=BORDER_COLOR,
            background=BACKGROUND_COLOR,
            takefocus=False,
            state='disabled')
        self.logVerticalScrollBar.config(command=self.uploadLogText.yview)
        self.logHorizontalScrollBar.config(command=self.uploadLogText.xview)
        self.logVerticalScrollBar.pack(side='right', fill='y')
        self.logHorizontalScrollBar.pack(side='bottom', fill='x')
        self.setLogTextStyles()
        self.uploadLogText.pack(fill='both', expand=True)
        self.logFrame.pack(fill='both', expand=False, anchor='s', padx=PAD_MEDIUM, pady=0)

        # upload button, upload progress bar
        self.progressFrame = tk.Frame(self.bottomFrame, bg=BACKGROUND_COLOR)
        self.uploadProgressBar = ttk.Progressbar(self.progressFrame)
        self.uploadProgressBar.pack(side='bottom', fill='x', expand=True)
        self.progressFrame.pack(
            fill='x',
            expand=False,
            anchor='s',
            padx=PAD_MEDIUM,
            pady=PAD_SMALL)

        self.loadFileUploadFrame()

    def deselectMetadata(self):
        self.subjectListBox.selection_clear(0, 'end')
        self.siteListBox.selection_clear(0, 'end')
        self.visitListBox.selection_clear(0, 'end')
        self.specimenListBox.selection_clear(0, 'end')
        self.simulationListBox.selection_clear(0, 'end')

    def loadFileUploadFrame(self):
        self.innerRightFrame.config(text="Upload Files")
        if hasattr(self, 'fileUploadFrame'):
            pass
        else:
            self.fileUploadFrame = tk.Frame(self.innerRightFrame, bg=BACKGROUND_COLOR)

        self.fileUploadFrame.pack(
            fill='both',
            expand=True,
            anchor='n',
            side='right',
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)

        # action buttons along the top of the window
        self.fileChooserFrame = tk.Frame(
            self.fileUploadFrame,
            bg=BACKGROUND_COLOR)

        self.fileChooserButtonFrame = tk.Frame(self.fileChooserFrame, bg=BACKGROUND_COLOR)
        self.fileChooserButton = ttk.Button(
            self.fileChooserButtonFrame,
            text='Choose FCS Files...',
            command=self.selectFiles)
        self.fileClearSelectionButton = ttk.Button(
            self.fileChooserButtonFrame,
            text='Clear Selected',
            command=self.clearSelectedFiles)
        self.fileClearAllButton = ttk.Button(
            self.fileChooserButtonFrame,
            text='Clear All',
            command=self.clearAllFiles)
        self.refreshButton = ttk.Button(
            self.fileChooserButtonFrame,
            text='Refresh from Server',
            command=self.loadUserProjects)
        self.uploadButton = ttk.Button(
            self.fileChooserButtonFrame,
            text='Upload Files',
            state='disabled',
            style='Inactive.TButton',
            command=self.uploadFiles)
        self.fileChooserButton.pack(side='left')
        self.fileClearSelectionButton.pack(side='left')
        self.fileClearAllButton.pack(side='left')
        self.uploadButton.pack(side='right')
        self.refreshButton.pack(side='right')
        self.fileChooserButtonFrame.pack(anchor='n', fill='x', expand=False)

        self.fileListFrame = tk.Frame(
            self.fileChooserFrame,
            bg=BACKGROUND_COLOR)
        self.fileScrollBar = tk.Scrollbar(self.fileListFrame, orient='vertical')
        self.fileListBox = tk.Listbox(
            self.fileListFrame,
            yscrollcommand=self.fileScrollBar.set,
            relief='flat',
            borderwidth=0,
            highlightcolor=HIGHLIGHT_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1)
        self.fileScrollBar.config(command=self.fileListBox.yview)
        self.fileScrollBar.pack(side='right', fill='y')
        self.fileListBox.pack(fill='both', expand=True)
        self.fileListFrame.pack(fill='both', expand=True)
        self.fileChooserFrame.pack(
            fill='both',
            expand=True,
            anchor='n')

    def clearSelectedFiles(self):
        for i in self.fileListBox.curselection():
            self.fileListBox.delete(i)
        self.updateUploadButtonState()

    def clearAllFiles(self):
        self.fileListBox.delete(0, 'end')
        self.updateUploadButtonState()

    def selectFiles(self):
        selectedFiles = tkFileDialog.askopenfiles('r')
        sortedFileList = list()
        for f in selectedFiles:
            sortedFileList.append(f.name)
        sortedFileList.sort()
        self.fileListBox.delete(0, 'end')
        for i, f in enumerate(sortedFileList):
            self.fileListBox.insert(i, f)
            if i % 2:
                self.fileListBox.itemconfig(i, bg=ROW_ALT_COLOR)
        self.deselectMetadata()
        self.updateUploadButtonState()

    def loadUserProjects(self):
        response = None
        try:
            response = rest.get_projects(self.host, self.token)
        except Exception, e:
            print e

        self.projectListBox.delete(0, 'end')
        self.siteListBox.delete(0, 'end')
        self.subjectListBox.delete(0, 'end')
        self.visitListBox.delete(0, 'end')
        for result in response['data']['results']:
            self.project_dict[result['project_name']] = result['id']
        for project_name in sorted(self.project_dict.keys()):
            self.projectListBox.insert('end', project_name)

    def loadSpecimens(self):
        response = None
        try:
            response = rest.get_specimens(self.host, self.token)
        except Exception, e:
            print e

        self.specimenListBox.delete(0, 'end')
        for result in response['data']['results']:
            self.specimen_dict[result['specimen_description']] = result['id']
        for specimen in sorted(self.specimen_dict.keys()):
            self.specimenListBox.insert('end', specimen)

    def loadStimulations(self):
        response = None
        try:
            response = rest.get_stimulations(self.host, self.token)
        except Exception, e:
            print e

        self.simulationListBox.delete(0, 'end')
        for result in response['data']['results']:
            self.stimulation_dict[result['stimulation_name']] = result['id']
        for stimulation in sorted(self.stimulation_dict.keys()):
            self.simulationListBox.insert('end', stimulation)

    def loadProjectSites(self, project_id):
        response = None
        try:
            response = rest.get_sites(self.host, self.token, project_pk=project_id)
        except Exception, e:
            print e

        self.siteListBox.delete(0, 'end')
        self.site_dict.clear()
        for result in response['data']['results']:
            self.site_dict[result['site_name']] = result['id']
        for site_name in sorted(self.site_dict.keys()):
            self.siteListBox.insert('end', site_name)

    def loadProjectSubjects(self, project_id):
        response = None
        try:
            response = rest.get_subjects(self.host, self.token, project_pk=project_id)
        except Exception, e:
            print e

        self.subjectListBox.delete(0, 'end')
        self.subject_dict.clear()
        for result in response['data']['results']:
            self.subject_dict[result['subject_code']] = result['id']
        for subject_id in sorted(self.subject_dict.keys()):
            self.subjectListBox.insert('end', subject_id)

    def loadProjectVisits(self, project_id):
        response = None
        try:
            response = rest.get_visit_types(self.host, self.token, project_pk=project_id)
        except Exception, e:
            print e

        self.visitListBox.delete(0, 'end')
        self.visit_dict.clear()
        for result in response['data']['results']:
            self.visit_dict[result['visit_type_name']] = result['id']
        for visit_type_name in sorted(self.visit_dict.keys()):
            self.visitListBox.insert('end', visit_type_name)

    def loadProjectPanels(self):
        if self.projectListBox.curselection():
            selectedProjectName = self.projectListBox.get(self.projectListBox.curselection())
        else:
            return
        selectedSiteName = None
        if self.siteListBox.curselection():
            selectedSiteName = self.siteListBox.get(self.siteListBox.curselection())

        panel_args = [self.host, self.token]
        panel_kwargs = {'project_pk': self.project_dict[selectedProjectName]}
        if selectedSiteName:
            panel_kwargs['site_pk'] = self.site_dict[selectedSiteName]

        try:
            response = rest.get_panels(*panel_args, **panel_kwargs)
        except Exception, e:
            print e

        self.panelListBox.delete(0, 'end')
        self.panel_dict.clear()
        for result in response['data']:
            self.panel_dict[result['panel_name']] = result['id']
        for panel_name in sorted(self.panel_dict.keys()):
            self.panelListBox.insert('end', panel_name)

    def updateMetadata(self, event=None):

        selectedProjectName = self.projectListBox.get(self.projectListBox.curselection())

        if selectedProjectName in self.project_dict:
            self.loadProjectSites(self.project_dict[selectedProjectName])
            self.loadProjectSubjects(self.project_dict[selectedProjectName])
            self.loadProjectVisits(self.project_dict[selectedProjectName])

        self.updateUploadButtonState()

    def siteSelectionChanged(self, event=None):
        self.updateUploadButtonState()

    def updateUploadButtonState(self, event=None):
        active = True
        site_selection = self.siteListBox.curselection()
        subject_selection = self.subjectListBox.curselection()
        visit_selection = self.visitListBox.curselection()
        specimen_selection = self.specimenListBox.curselection()

        if not site_selection or not subject_selection or not visit_selection or not specimen_selection:
            active = False
        if hasattr(self, 'fileListBox'):
            if len(self.fileListBox.get(0, 'end')) == 0:
                active = False
        else:
            active = False
        if active:
            self.uploadButton.config(state='active')
        else:
            self.uploadButton.config(state='disabled')

    def setLogTextStyles(self):
        self.uploadLogText.tag_config('error', foreground=ERROR_FOREGROUND_COLOR)

    def uploadFiles(self):
        subject_selection = self.subjectListBox.get(self.subjectListBox.curselection())
        site_selection = self.siteListBox.get(self.siteListBox.curselection())
        visit_selection = self.visitListBox.get(self.visitListBox.curselection())
        specimen_selection = self.specimenListBox.get(self.specimenListBox.curselection())

        if self.simulationListBox.curselection():
            sample_group_pk = str(self.stimulation_dict[self.simulationListBox.get(self.simulationListBox.curselection())])
        else:
            sample_group_pk = None

        uploadFileList = self.fileListBox.get(0, 'end')
        self.uploadProgressBar.config(maximum=len(uploadFileList))

        for i, file_path in enumerate(uploadFileList):
            response_dict = rest.post_sample(
                self.host,
                self.token,
                file_path,
                subject_pk=str(self.subject_dict[subject_selection]),
                site_pk=str(self.site_dict[site_selection]),
                visit_type_pk=str(self.visit_dict[visit_selection]),
                specimen_pk=str(self.specimen_dict[specimen_selection]),
                sample_group_pk=sample_group_pk
            )

            log_text = ''.join(
                [
                    file_path,
                    ' (',
                    str(response_dict['status']),
                    ': ',
                    str(response_dict['reason']),
                    ')\n',
                    json.dumps(response_dict['data'], indent=4),
                    '\n'
                ]
            )
            self.uploadLogText.config(state='normal')

            if response_dict['status'] == 201:
                self.fileListBox.itemconfig(
                    i,
                    fg=SUCCESS_FOREGROUND_COLOR,
                    selectforeground=SUCCESS_FOREGROUND_COLOR)
                self.uploadLogText.insert('end', log_text)
            elif response_dict['status'] == 400:
                self.fileListBox.itemconfig(
                    i,
                    fg=ERROR_FOREGROUND_COLOR,
                    selectforeground=ERROR_FOREGROUND_COLOR)
                self.uploadLogText.insert('end', log_text, 'error')
            self.uploadLogText.config(state='disabled')

            self.uploadProgressBar.step()
            self.uploadProgressBar.update()


root = tk.Tk()
app = Application(root)
app.mainloop()