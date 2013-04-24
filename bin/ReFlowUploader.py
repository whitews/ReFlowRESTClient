import Tkinter as tk
import ttk
import tkMessageBox
import tkFileDialog
from PIL import Image, ImageTk
import reflowrestclient.utils as rest

LOGO_PATH = '../imgs/reflow_text.png'


class Application(tk.Frame):

    def __init__(self, master):
        self.uploadFileSet = set()
        self.projectDict = dict()  # a bit weird, but we'll use the project name as the key, pk as the value
        self.siteDict = dict()
        self.subjectDict = dict()
        self.visitDict = dict()

        self.style = ttk.Style()
        self.style.configure("ProgressBar", height=20)

        # can't call super on old-style class, call parent init directly
        tk.Frame.__init__(self, master)
        self.master.title('ReFlow Uploader')
        self.master.minsize(width=800, height=640)
        self.master.config(bg='#f5f5f5')
        self.pack()
        self.loadLoginFrame()

    def loadLoginFrame(self):
        self.loginFrame = tk.Frame(bg='#f5f5f5')

        self.logoImage = ImageTk.PhotoImage(Image.open(LOGO_PATH))
        self.logoLabel = tk.Label(self.loginFrame, image=self.logoImage)
        self.logoLabel.config(bg='#f5f5f5')
        self.logoLabel.pack(side='top', pady=15)

        self.hostEntryFrame = tk.Frame(self.loginFrame, bg='#f5f5f5')
        self.hostLabel = tk.Label(self.hostEntryFrame, text='Hostname', bg='#f5f5f5', width=8, anchor='e')
        self.hostLabel.pack(side='left')
        self.hostEntry = tk.Entry(self.hostEntryFrame, highlightbackground='#f5f5f5', width=24)
        self.hostEntry.pack(padx=3)
        self.hostEntryFrame.pack(pady=3)

        self.userEntryFrame = tk.Frame(self.loginFrame, bg='#f5f5f5')
        self.userLabel = tk.Label(self.userEntryFrame, text='Username', bg='#f5f5f5', width=8, anchor='e')
        self.userLabel.pack(side='left')
        self.userEntry = tk.Entry(self.userEntryFrame, highlightbackground='#f5f5f5', width=24)
        self.userEntry.pack(padx=3)
        self.userEntryFrame.pack(pady=3)

        self.passwordEntryFrame = tk.Frame(self.loginFrame, bg='#f5f5f5')
        self.passwordLabel = tk.Label(self.passwordEntryFrame, text='Password', bg='#f5f5f5', width=8, anchor='e')
        self.passwordLabel.pack(side='left')
        self.passwordEntry = tk.Entry(self.passwordEntryFrame, show='*', highlightbackground='#f5f5f5', width=24)
        self.passwordEntry.pack(padx=3)
        self.passwordEntryFrame.pack(pady=3)

        self.loginButtonFrame = tk.Frame(self.loginFrame, bg='#f5f5f5')
        self.loginButtonLabel = tk.Label(self.loginButtonFrame, bg='#f5f5f5')
        self.loginButton = tk.Button(
            self.loginButtonLabel,
            text='Login',
            command=self.login,
            bg='#f5f5f5',
            highlightbackground='#f5f5f5')
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
        self.fileChooserFrame = tk.Frame(self.master, bg='#f5f5f5')

        self.fileListFrame = tk.Frame(self.fileChooserFrame, bg='#f5f5f5')
        self.fileScrollBar = tk.Scrollbar(self.fileListFrame, orient='vertical')
        self.fileListBox = tk.Listbox(
            self.fileListFrame,
            yscrollcommand=self.fileScrollBar.set,
            relief='sunken',
            borderwidth=2)
        self.fileScrollBar.config(command=self.fileListBox.yview)
        self.fileScrollBar.pack(side='right', fill='y')
        self.fileListBox.pack(fill='both', expand=True)
        self.fileListFrame.pack(fill='both', expand=True)

        self.fileChooserButtonFrame = tk.Frame(self.fileChooserFrame, bg='#f5f5f5')
        self.fileChooserButtonLabel = tk.Label(self.fileChooserButtonFrame, bg='#f5f5f5')
        self.fileChooserButton = tk.Button(
            self.fileChooserButtonLabel,
            text='Choose FCS Files...',
            command=self.selectFiles,
            bg='#f5f5f5',
            highlightbackground='#f5f5f5')
        self.fileChooserButton.pack()
        self.fileChooserButtonLabel.pack(side='right')
        self.fileChooserButtonFrame.pack(fill='x')

        self.fileChooserFrame.pack(fill='both', expand=True, anchor='n', padx=6, pady=6)

        # Start metadata choices, including:
        #    - project
        #    - site
        #    - subject
        #    - visit
        self.metadataFrame = tk.Frame(self.master, bg='#f5f5f5')

        # overall project frame (on bottom left of main window)
        self.projectFrame = tk.Frame(self.metadataFrame, bg='#f5f5f5')

        # project label frame (top of project chooser frame)
        self.projectChooserLabelFrame = tk.Frame(self.projectFrame, bg='#f5f5f5')
        self.projectChooserLabel = tk.Label(self.projectChooserLabelFrame, text='Choose Project', bg='#f5f5f5')
        self.projectChooserLabel.pack(side='left')
        self.projectChooserLabelFrame.pack(fill='x')

        # project chooser listbox frame (bottom of project chooser frame)
        self.projectChooserFrame = tk.Frame(self.projectFrame, bg='#f5f5f5')
        self.projectScrollBar = tk.Scrollbar(self.projectChooserFrame, orient='vertical')
        self.projectListBox = tk.Listbox(
            self.projectChooserFrame,
            exportselection=0,
            yscrollcommand=self.projectScrollBar.set,
            relief='sunken',
            borderwidth=2)
        self.projectListBox.bind('<<ListboxSelect>>', self.updateMetadata)
        self.projectScrollBar.config(command=self.projectListBox.yview)
        self.projectScrollBar.pack(side='right', fill='y')
        self.projectListBox.pack(fill='both', expand=True)
        self.projectChooserFrame.pack(fill='both', expand=True)

        self.projectFrame.pack(side='left', fill='both', expand=True)

        # overall site frame (on bottom, 2nd from left of main window
        self.siteFrame = tk.Frame(self.metadataFrame, bg='#f5f5f5')

        # site label frame (top of site chooser frame)
        self.siteChooserLabelFrame = tk.Frame(self.siteFrame, bg='#f5f5f5')
        self.siteChooserLabel = tk.Label(self.siteChooserLabelFrame, text='Choose Site', bg='#f5f5f5')
        self.siteChooserLabel.pack(side='left')
        self.siteChooserLabelFrame.pack(fill='x')

        # site chooser listbox frame (bottom of site chooser frame)
        self.siteChooserFrame = tk.Frame(self.siteFrame, bg='#f5f5f5')
        self.siteScrollBar = tk.Scrollbar(self.siteChooserFrame, orient='vertical')
        self.siteListBox = tk.Listbox(
            self.siteChooserFrame,
            exportselection=0,
            yscrollcommand=self.siteScrollBar.set,
            relief='sunken',
            borderwidth=2)
        self.siteScrollBar.config(command=self.siteListBox.yview)
        self.siteScrollBar.pack(side='right', fill='y')
        self.siteListBox.pack(fill='both', expand=True)
        self.siteChooserFrame.pack(fill='both', expand=True)

        self.siteFrame.pack(side='left', fill='both', expand=True)

        # overall subject frame (on bottom, 2nd from left of main window
        self.subjectFrame = tk.Frame(self.metadataFrame, bg='#f5f5f5')

        # subject label frame (top of subject chooser frame)
        self.subjectChooserLabelFrame = tk.Frame(self.subjectFrame, bg='#f5f5f5')
        self.subjectChooserLabel = tk.Label(self.subjectChooserLabelFrame, text='Choose Subject', bg='#f5f5f5')
        self.subjectChooserLabel.pack(side='left')
        self.subjectChooserLabelFrame.pack(fill='x')

        # subject chooser listbox frame (bottom of subject chooser frame)
        self.subjectChooserFrame = tk.Frame(self.subjectFrame, bg='#f5f5f5')
        self.subjectScrollBar = tk.Scrollbar(self.subjectChooserFrame, orient='vertical')
        self.subjectListBox = tk.Listbox(
            self.subjectChooserFrame,
            exportselection=0,
            yscrollcommand=self.subjectScrollBar.set,
            relief='sunken',
            borderwidth=2)
        self.subjectScrollBar.config(command=self.subjectListBox.yview)
        self.subjectScrollBar.pack(side='right', fill='y')
        self.subjectListBox.pack(fill='both', expand=True)
        self.subjectChooserFrame.pack(fill='both', expand=True)

        self.subjectFrame.pack(side='left', fill='both', expand=True)

        # overall visit frame (on bottom, 2nd from left of main window
        self.visitFrame = tk.Frame(self.metadataFrame, bg='#f5f5f5')

        # visit label frame (top of visit chooser frame)
        self.visitChooserLabelFrame = tk.Frame(self.visitFrame, bg='#f5f5f5')
        self.visitChooserLabel = tk.Label(self.visitChooserLabelFrame, text='Choose Visit', bg='#f5f5f5')
        self.visitChooserLabel.pack(side='left')
        self.visitChooserLabelFrame.pack(fill='x')

        # visit chooser listbox frame (bottom of visit chooser frame)
        self.visitChooserFrame = tk.Frame(self.visitFrame, bg='#f5f5f5')
        self.visitScrollBar = tk.Scrollbar(self.visitChooserFrame, orient='vertical')
        self.visitListBox = tk.Listbox(
            self.visitChooserFrame,
            exportselection=0,
            yscrollcommand=self.visitScrollBar.set,
            relief='sunken',
            borderwidth=2)
        self.visitScrollBar.config(command=self.visitListBox.yview)
        self.visitScrollBar.pack(side='right', fill='y')
        self.visitListBox.pack(fill='both', expand=True)
        self.visitChooserFrame.pack(fill='both', expand=True)

        self.visitFrame.pack(side='left', fill='both', expand=True)

        self.metadataFrame.pack(fill='both', expand=True, padx=6, pady=6)

        # upload progress bar and upload button
        self.progressFrame = tk.Frame(self.master, bg='#f5f5f5')
        self.uploadProgressBar = ttk.Progressbar(self.progressFrame)
        self.uploadButton = tk.Button(
            self.progressFrame,
            text='Upload Files',
            command=self.uploadFiles,
            bg='#f5f5f5',
            highlightbackground='#f5f5f5')
        self.uploadProgressBar.pack(side='left', fill='x', expand=True)
        self.uploadButton.pack(side='right')
        self.progressFrame.pack(fill='x', expand=False, padx=6, pady=6)

        self.loadUserProjects()

    def selectFiles(self):
        selectedFiles = tkFileDialog.askopenfiles('r')
        self.uploadFileSet.update(selectedFiles)
        sortedFileList = list(self.uploadFileSet)
        sortedFileList.sort(key=lambda x: x.name)
        self.fileListBox.delete(0, 'end')
        for f in sortedFileList:
            self.fileListBox.insert('end', f.name)

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

    def uploadFiles(self):
        print 'uploading files'

root = tk.Tk()
app = Application(root)
app.mainloop()