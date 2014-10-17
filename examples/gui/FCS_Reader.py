import Tkinter
import ttk
import tkFileDialog
import os
from exceptions import TypeError

import flowio

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


class ChosenFile(object):
    def __init__(self, f, checkbox):
        self.file = f
        self.file_path = f.name
        self.file_name = os.path.basename(f.name)
        self.checkbox = checkbox

        # test if file is an FCS file, raise TypeError if not
        try:
            self.flow_data = flowio.FlowData(f)
        except:
            raise TypeError("File %s is not an FCS file." % self.file_name)


class Application(Tkinter.Frame):

    def __init__(self, master):

        style = ttk.Style()
        style.configure(
            'Treeview',
            borderwidth=1,
            font=('TkDefaultFont', 12, 'normal'))

        # dict of ChosenFile objects, key is file path, value is ChosenFile
        self.file_dict = dict()

        # can't call super on old-style class, call parent init directly
        Tkinter.Frame.__init__(self, master)
        self.master.title('FCS Reader')
        self.master.minsize(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
        self.master.config(bg=BACKGROUND_COLOR)

        self.menu_bar = Tkinter.Menu(master)
        self.master.config(menu=self.menu_bar)

        self.upload_button = None
        self.upload_progress_bar = None
        self.view_metadata_button = None
        self.file_list_canvas = None

        self.s = ttk.Style()
        self.s.map(
            'Inactive.TButton',
            foreground=[('disabled', INACTIVE_FOREGROUND_COLOR)])

        self.pack()

        self.load_main_frame()

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
        top_frame.config(text="Choose FCS Files")

        bottom_frame = Tkinter.Frame(main_frame, bg=BACKGROUND_COLOR)
        bottom_frame.pack(
            fill='both',
            expand=True,
            anchor='n',
            padx=0,
            pady=0)

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
        file_chooser_button.pack(side='left')
        file_clear_selection_button.pack(side='left')
        file_clear_all_button.pack(side='left')

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

    def _on_mousewheel(self, event):
        self.file_list_canvas.yview_scroll(-event.delta, "units")

    def clear_selected_files(self):
        cb_to_delete = []
        for k, cb in self.file_list_canvas.children.items():
            if isinstance(cb, MyCheckbutton):
                if cb.is_checked() and cb.cget('state') != Tkinter.DISABLED:
                    cb_to_delete.append(cb)

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

    def select_all_files(self):
        for k, v in self.file_list_canvas.children.items():
            if isinstance(v, MyCheckbutton):
                v.mark_checked()

    def choose_files(self):
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
        metadata_text.tag_configure(
            'file-name', font=('TkDefaultFont', 18, 'bold'))

        for k, v in self.file_list_canvas.children.items():
            if isinstance(v, MyCheckbutton):
                if v.is_checked() and v.cget('state') != Tkinter.DISABLED:
                    # get metadata for only the selected checkboxes
                    chosen_file = self.file_dict[v.file_path]
                    metadata_text.insert(
                        Tkinter.END, chosen_file.file_name, ("file-name",))
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
                            metadata_text.tag_remove(
                                "alt-row", line_start, "end")

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


root = Tkinter.Tk()
app = Application(root)
app.mainloop()