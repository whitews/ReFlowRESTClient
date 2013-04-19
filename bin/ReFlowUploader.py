import Tkinter as tk


class Application(tk.Frame):

    def __init__(self, master):
        # can't call super on old-style class, call parent init directly
        tk.Frame.__init__(self, master)

        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.quitButton = tk.Button(self, text='Quit', command=self.quit)
        self.quitButton.pack()

root = tk.Tk()
app = Application(root)
app.master.title('ReFlow Uploader')
app.master.minsize(width=200, height=200)

app.mainloop()