import Tkinter as tk
from PIL import Image, ImageTk
import reflowrestclient.utils as rest

LOGO_PATH = '../imgs/reflow_text.png'


class Application(tk.Frame):

    def __init__(self, master):
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
        self.passwordEntry = tk.Entry(self.passwordEntryFrame, highlightbackground='#f5f5f5', width=24)
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

        #self.loginFrame.pack(fill='both', expand=True)
        self.loginFrame.place(in_=self.master, anchor='c', relx=.5, rely=.5)

    def login(self):
        print 'login'

root = tk.Tk()
app = Application(root)
app.mainloop()