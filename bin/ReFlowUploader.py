import Tkinter as tk
from PIL import Image, ImageTk

LOGO_PATH = '../imgs/reflow_text.png'


class Application(tk.Frame):

    def __init__(self, master):
        # can't call super on old-style class, call parent init directly
        tk.Frame.__init__(self, master)
        self.master.title('ReFlow Uploader')
        self.master.minsize(width=800, height=640)
        self.master.config(bg='#f5f5f5')
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.loginFrame = tk.Frame(bg='#f5f5f5')

        self.logoImage = ImageTk.PhotoImage(Image.open(LOGO_PATH))
        self.logoLabel = tk.Label(self.loginFrame, image=self.logoImage)
        self.logoLabel.config(bg='#f5f5f5')
        self.logoLabel.pack(side='top')

        self.quitLabel = tk.Label(self.loginFrame, bg='#f5f5f5', fg='#f5f5f5')
        self.quitButton = tk.Button(
            self.quitLabel,
            text='Quit',
            command=self.quit,
            bg='#f5f5f5',
            highlightbackground='#f5f5f5')
        self.quitButton.pack()
        self.quitLabel.pack()

        self.loginFrame.pack()


root = tk.Tk()
app = Application(root)
app.mainloop()