import Tkinter as tk
import ttk
import tkMessageBox
import tkFileDialog
from PIL import Image, ImageTk
import reflowrestclient.utils as rest
import json
import sys
import os


if hasattr(sys, '_MEIPASS'):
    # for PyInstaller 2.0
    RESOURCE_DIR = sys._MEIPASS
else:
    # for development
    RESOURCE_DIR = '../resources'

LOGO_PATH = os.path.join(RESOURCE_DIR, 'reflow_text.png')
if sys.platform == 'win32':
    ICON_PATH = os.path.join(RESOURCE_DIR, 'reflow.ico')
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

FUNCTION_DICT = {
    '0': 'Upload Files',
    '1': 'Apply Panel',
}


class Application(tk.Frame):

    def __init__(self, master):
        # a bit weird, but we'll use the names (project, site, etc.) as the key, pk as the value
        # for the four choice dictionaries below. we need the names to be unique (and they should be) and
        # it's more convenient to lookup by key using the name to find the selection.
        self.projectDict = dict()
        self.siteDict = dict()
        self.subjectDict = dict()
        self.visitDict = dict()

        # can't call super on old-style class, call parent init directly
        tk.Frame.__init__(self, master)
        self.master.iconbitmap(ICON_PATH)
        self.master.title('ReFlow Client')
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
            tkMessageBox.showwarning('Login Failed', ' Check that the hostname, username, and password are correct')
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
            height=5,
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
            height=5,
            borderwidth=0,
            highlightcolor=HIGHLIGHT_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1)
        self.siteListBox.bind('<<ListboxSelect>>', self.updateUploadButtonState)
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
            height=5,
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

        # overall visit frame (on bottom, 2nd from left of main window
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
            height=5,
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

        self.loadUserProjects()

        self.metadataFrame.pack(
            fill='x',
            expand=False,
            anchor='n',
            padx=PAD_MEDIUM,
            pady=0)

        self.leftFrame = tk.Frame(self.middleFrame, bg=BACKGROUND_COLOR)
        self.leftFrame.pack(
            fill='y',
            expand=False,
            anchor='n',
            side='left',
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)

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
        self.functionLabelFrame = tk.LabelFrame(
            self.leftFrame,
            bg=BACKGROUND_COLOR,
            text="Choose Function")
        self.functionLabelFrame.pack(fill='y', expand=False, anchor='n', side='left')

        self.functionListFrame = tk.Frame(self.functionLabelFrame, bg=BACKGROUND_COLOR)
        self.functionListScrollBar = tk.Scrollbar(self.functionListFrame, orient='vertical')
        self.functionListBox = tk.Listbox(
            self.functionListFrame,
            yscrollcommand=self.functionListScrollBar.set,
            relief='flat',
            height=14,
            borderwidth=0,
            highlightcolor=HIGHLIGHT_COLOR,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1)
        self.functionListBox.bind('<<ListboxSelect>>', self.loadSelectedFunction)
        self.functionListScrollBar.config(command=self.functionListBox.yview)
        self.functionListScrollBar.pack(side='right', fill='y')
        self.functionListBox.pack(fill='both', expand=True, padx=PAD_MEDIUM, pady=0)
        self.functionListFrame.pack(fill='both', expand=True, pady=PAD_MEDIUM)

        for key in FUNCTION_DICT:
            self.functionListBox.insert(key, FUNCTION_DICT[key])

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

        self.functionListBox.selection_set(0, 0)
        self.loadSelectedFunction()

    def deselectMetadata(self):
        self.subjectListBox.selection_clear(0, 'end');
        self.siteListBox.selection_clear(0, 'end');
        self.visitListBox.selection_clear(0, 'end');

    def loadSelectedFunction(self, event=None):
        selectedFunction = self.functionListBox.curselection()

        for widget in self.innerRightFrame.pack_slaves():
            widget.pack_forget()

        if selectedFunction[0] in FUNCTION_DICT:
            if selectedFunction[0] == '0':
                if hasattr(self, 'fileUploadFrame'):
                    self.innerRightFrame.config(text="Upload Files")
                    self.fileUploadFrame.pack(
                        fill='both',
                        expand=True,
                        anchor='n',
                        padx=PAD_MEDIUM,
                        pady=PAD_MEDIUM)
                else:
                    self.loadFileUploadFrame()
            elif selectedFunction[0] == '1':
                if hasattr(self, 'applyPanelFrame'):
                    self.innerRightFrame.config(text="Apply Panel to Samples")
                    self.applyPanelFrame.pack(
                        fill='both',
                        expand=True,
                        anchor='n',
                        padx=PAD_MEDIUM,
                        pady=PAD_MEDIUM)
                else:
                    self.loadApplyPanelFrame()

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
            side='right')

        # action buttons along the top of the window
        self.fileChooserFrame = tk.Frame(self.fileUploadFrame, bg=BACKGROUND_COLOR)

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
        self.fileChooserButtonFrame.pack(side='top', fill='x', expand=False)

        self.fileListFrame = tk.Frame(self.fileChooserFrame, bg=BACKGROUND_COLOR)
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
        self.fileListFrame.pack(fill='both', expand=True, pady=PAD_MEDIUM)
        self.fileChooserFrame.pack(
            fill='both',
            expand=True,
            anchor='n',
            padx=PAD_MEDIUM,
            pady=PAD_MEDIUM)

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
        for result in response['data']:
            self.projectDict[result['project_name']] = result['id']
        for project_name in sorted(self.projectDict.keys()):
            self.projectListBox.insert('end', project_name)

    def loadProjectSites(self, project_id):
        response = None
        try:
            response = rest.get_sites(self.host, self.token, project_pk=project_id)
        except Exception, e:
            print e

        self.siteListBox.delete(0, 'end')
        self.siteDict.clear()
        for result in response['data']:
            self.siteDict[result['site_name']] = result['id']
        for site_name in sorted(self.siteDict.keys()):
            self.siteListBox.insert('end', site_name)

    def loadProjectSubjects(self, project_id):
        response = None
        try:
            response = rest.get_subjects(self.host, self.token, project_pk=project_id)
        except Exception, e:
            print e

        self.subjectListBox.delete(0, 'end')
        self.subjectDict.clear()
        for result in response['data']:
            self.subjectDict[result['subject_id']] = result['id']
        for subject_id in sorted(self.subjectDict.keys()):
            self.subjectListBox.insert('end', subject_id)

    def loadProjectVisits(self, project_id):
        response = None
        try:
            response = rest.get_visit_types(self.host, self.token, project_pk=project_id)
        except Exception, e:
            print e

        self.visitListBox.delete(0, 'end')
        self.visitDict.clear()
        for result in response['data']:
            self.visitDict[result['visit_type_name']] = result['id']
        for visit_type_name in sorted(self.visitDict.keys()):
            self.visitListBox.insert('end', visit_type_name)

    def updateMetadata(self, event=None):

        selectedProjectName = self.projectListBox.get(self.projectListBox.curselection())

        if selectedProjectName in self.projectDict:
            self.loadProjectSites(self.projectDict[selectedProjectName])
            self.loadProjectSubjects(self.projectDict[selectedProjectName])
            self.loadProjectVisits(self.projectDict[selectedProjectName])

        self.updateUploadButtonState()

    def updateUploadButtonState(self, event=None):
        active = True
        site_selection = self.siteListBox.curselection()
        subject_selection = self.subjectListBox.curselection()
        visit_selection = self.visitListBox.curselection()

        if not site_selection or not subject_selection or not visit_selection:
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

        uploadFileList = self.fileListBox.get(0, 'end')
        self.uploadProgressBar.config(maximum=len(uploadFileList))

        for i, file_path in enumerate(uploadFileList):
            response_dict = rest.post_sample(
                self.host,
                self.token,
                file_path,
                subject_pk=str(self.subjectDict[subject_selection]),
                site_pk=str(self.siteDict[site_selection]),
                visit_type_pk=str(self.visitDict[visit_selection])
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

    def loadApplyPanelFrame(self):
        self.innerRightFrame.config(text="Apply Panel to Samples")
        if hasattr(self, 'applyPanelFrame'):
            pass
        else:
            self.applyPanelFrame = tk.Frame(self.innerRightFrame, bg=BACKGROUND_COLOR)

        self.applyPanelFrame.pack(
            fill='both',
            expand=True,
            anchor='n',
            side='right')

        self.someButton = ttk.Button(
            self.applyPanelFrame,
            text='Some Button',
            style='Inactive.TButton')
        self.someButton.pack(side='left')

root = tk.Tk()
app = Application(root)
app.mainloop()