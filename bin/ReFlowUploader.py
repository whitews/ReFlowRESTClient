import Tkinter as tk
from PIL import Image, ImageTk

LOGO_PATH = '../imgs/reflow_text.png'


class Application(tk.Frame):

    def __init__(self, master):
        # can't call super on old-style class, call parent init directly
        tk.Frame.__init__(self, master)
        self.master.title('ReFlow Uploader')
        self.master.minsize(width=800, height=640)
        self.master.config(bg="#f5f5f5")
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.logoImage = ImageTk.PhotoImage(Image.open(LOGO_PATH))
        self.logoPanel = tk.Label(self, image=self.logoImage)
        self.logoPanel.config(bg="#f5f5f5")
        self.logoPanel.pack(side='top')

        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.config(bg="#f5f5f5")
        self.quitButton.pack()


root = tk.Tk()
app = Application(root)
app.mainloop()