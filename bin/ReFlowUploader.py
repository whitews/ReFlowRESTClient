import Tkinter as tk
import ttk
import tkMessageBox
import tkFileDialog
from PIL import Image, ImageTk
import reflowrestclient.utils as rest
import json

LOGO_PATH = '../imgs/reflow_text.png'
BACKGROUND_COLOR = '#ededed'
SEPARATOR_COLOR = '#d7d7d7'
BORDER_COLOR = '#bebebe'
HIGHLIGHT_COLOR = '#5489b9'
ROW_ALT_COLOR = '#f3f6fa'

PAD_SMALL = 3
PAD_MEDIUM = 6
PAD_LARGE = 12
PAD_EXTRA_LARGE = 15

class Application(tk.Frame):

    def __init__(self, master):
        self.uploadFileDict = dict()  # key is file path, value is file object

        # a bit weird, but we'll use the names (project, site, etc.) as the key, pk as the value
        # for the four choice dictionaries below. we need the names to be unique (and they should be) and
        # it's more convenient to lookup by key using the name to find the selection.
        self.projectDict = dict()
        self.siteDict = dict()
        self.subjectDict = dict()
        self.visitDict = dict()

        # can't call super on old-style class, call parent init directly
        tk.Frame.__init__(self, master)
        self.master.title('ReFlow Uploader')
        self.master.minsize(width=800, height=640)
        self.master.config(bg=BACKGROUND_COLOR)

        self.pack()
        self.loadLoginFrame()

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
        self.loginButton = tk.Button(
            self.loginButtonLabel,
            text='Login',
            command=self.login,
            bg=BACKGROUND_COLOR,
            highlightbackground=BACKGROUND_COLOR)
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
        self.loadFileChooserFrame()

    def loadFileChooserFrame(self):
        self.fileChooserFrame = tk.Frame(self.master, bg=BACKGROUND_COLOR)

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
        self.fileListFrame.pack(fill='both', expand=True)

        self.fileChooserButtonFrame = tk.Frame(self.fileChooserFrame, bg=BACKGROUND_COLOR)
        self.fileChooserButtonLabel = tk.Label(self.fileChooserButtonFrame, bg=BACKGROUND_COLOR)
        self.fileChooserButton = tk.Button(
            self.fileChooserButtonLabel,
            text='Choose FCS Files...',
            command=self.selectFiles,
            bg=BACKGROUND_COLOR,
            highlightbackground=BACKGROUND_COLOR)
        self.fileChooserButton.pack()
        self.fileChooserButtonLabel.pack(side='right')
        self.fileChooserButtonFrame.pack(fill='x')

        self.fileChooserFrame.pack(fill='both', expand=True, anchor='n', padx=PAD_MEDIUM, pady=PAD_MEDIUM)

        self.separatorFrame = tk.Frame(self.master, bg=SEPARATOR_COLOR, height=1)
        self.separatorFrame.pack(fill='both', expand=False, padx=PAD_MEDIUM, pady=PAD_MEDIUM)

        # Start metadata choices, including:
        #    - project
        #    - site
        #    - subject
        #    - visit
        self.metadataFrame = tk.Frame(self.master, bg=BACKGROUND_COLOR)

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

        self.metadataFrame.pack(fill='x', expand=False, padx=PAD_MEDIUM, pady=PAD_MEDIUM)

        # upload progress bar and upload button
        self.progressFrame = tk.Frame(self.master, bg=BACKGROUND_COLOR)
        self.uploadProgressBar = ttk.Progressbar(self.progressFrame)
        self.uploadButton = tk.Button(
            self.progressFrame,
            text='Upload Files',
            state='disabled',
            command=self.uploadFiles,
            bg=BACKGROUND_COLOR,
            highlightbackground=BACKGROUND_COLOR)
        self.uploadProgressBar.pack(side='bottom', fill='x', expand=True)
        self.uploadButton.pack(side='right', pady=PAD_LARGE)
        self.progressFrame.pack(fill='x', expand=False, padx=PAD_MEDIUM)

        self.loadUserProjects()

    def selectFiles(self):
        selectedFiles = tkFileDialog.askopenfiles('r')
        for f in selectedFiles:
            self.uploadFileDict[f.name] = f
        sortedFileList = self.uploadFileDict.keys()
        sortedFileList.sort()
        self.fileListBox.delete(0, 'end')
        for i, f in enumerate(sortedFileList):
            self.fileListBox.insert(i, f)
            if i % 2:
                self.fileListBox.itemconfig(i, bg=ROW_ALT_COLOR)
        self.updateUploadButtonState()

    def loadUserProjects(self):
        response = None
        try:
            response = rest.get_projects(self.host, self.token)
        except Exception, e:
            print e

        self.projectListBox.delete(0, 'end')
        for result in response['data']:
            self.projectDict[result['project_name']] = result['id']
            self.projectListBox.insert('end', result['project_name'])

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
            self.siteListBox.insert('end', result['site_name'])

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
            self.subjectListBox.insert('end', result['subject_id'])

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
            self.visitListBox.insert('end', result['visit_type_name'])

    def updateMetadata(self, event):
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
        if len(self.uploadFileDict) == 0:
            active = False
        if active:
            self.uploadButton.config(state='active')
        else:
            self.uploadButton.config(state='disabled')

    def uploadFiles(self):
        subject_selection = self.subjectListBox.get(self.subjectListBox.curselection())
        site_selection = self.siteListBox.get(self.siteListBox.curselection())
        visit_selection = self.visitListBox.get(self.visitListBox.curselection())

        self.uploadProgressBar.config(maximum=len(self.uploadFileDict))

        for file_path in self.uploadFileDict.keys():
            response_dict = rest.post_sample(
                self.host,
                self.token,
                file_path,
                subject_pk=str(self.subjectDict[subject_selection]),
                site_pk=str(self.siteDict[site_selection]),
                visit_type_pk=str(self.visitDict[visit_selection])
            )

            print "Response: ", response_dict['status'], response_dict['reason']
            print 'Data: '
            print json.dumps(response_dict['data'], indent=4)

            self.uploadProgressBar.step()
            self.uploadProgressBar.update()




root = tk.Tk()
app = Application(root)
app.mainloop()