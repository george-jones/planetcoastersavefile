from tkinter import filedialog
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msgbox
import tempfile
import shutil
import os.path

import filewatcher
import pcsf

class App():

    def __init__(self):        
        self.temp_dir = tempfile.gettempdir()
        self.file_watcher = None
        self.data_width = 48 # size of data comparison boxes

        root = tk.Tk()
        root.wm_title("PCSFA")

        self.root = root
        self.file_versions = [ ]
        self.left_version = tk.IntVar()
        self.right_version = tk.IntVar()
        self.version_radios = [ ]
        self.comparison_widgets = [ ]

        #root.minsize(width=600, height=400)
        root.configure(background="blue")

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0)
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        ttk.Label(mainframe, text="Planet Coaster Save File Analyzer", font=("TkHeadingFont", 12)).grid(column=1, row=1, sticky=tk.W)
        ttk.Button(mainframe, text="Find Save File", command=self.find_file).grid(column=1, row=2, sticky=tk.W)
        ttk.Button(mainframe, text="Compare", command=self.compare).grid(column=2, row=2, sticky=tk.W)
        ttk.Label(mainframe, text="Initial Version").grid(column=1, row=3, sticky=tk.W)
        ttk.Label(mainframe, text="Compare To").grid(column=2, row=3, sticky=tk.W)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

        self.mainframe = mainframe
        root.mainloop()
        self.cleanup()

    def cleanup(self):
        if self.file_watcher is not None:
            self.file_watcher.cancel()

    def find_file(self):
        if self.file_watcher is not None:
            self.file_watcher.cancel()

        save_file_name = filedialog.askopenfilename()
        if save_file_name:
            self.file_versions = [ ]
            for r in self.version_radios:
                r.destroy()
            self.version_radios = [ ]
            self.get_file(save_file_name)
            self.file_watcher = filewatcher.FileWatcher(save_file_name, 2, self.file_changed)

    def file_changed(self, filename):
        self.get_file(filename)

    def get_file(self, filename):
        temp_file_name = os.path.join(self.temp_dir, 'temp.pcsf')
        shutil.copyfile(filename, temp_file_name)
        sf = pcsf.PlanetCoasterSaveFile(temp_file_name)
        self.file_versions.append(sf)
        n = len(self.file_versions)

        r = ttk.Radiobutton(self.mainframe, text="Version %d" % (n), variable=self.left_version, value=n-1)
        r.grid(column=1, row=n+3, sticky=tk.W)
        self.version_radios.append(r)
        r = ttk.Radiobutton(self.mainframe, text="Version %d" % (n), variable=self.right_version, value=n-1)
        r.grid(column=2, row=n+3, sticky=tk.W)
        self.version_radios.append(r)

    def compare(self):
        v0 = self.left_version.get()
        v1 = self.right_version.get()
        if v0 >= len(self.file_versions) or v1 >= len(self.file_versions) or v0 == v1:
            msgbox.showwarning("No Comparison Possible", "Please first choose a save file.  Then make a change in Planet Coaster so that there are multiple versions to compare. Then, choose two different versions and click thie Compare Button.")
            return
        for w in self.comparison_widgets:
            w.destroy()
        start_row = len(self.file_versions) + 4
        self.comparison_widgets = [ ]
        d = self.find_diffs(v0, v1)
        addresses = tk.StringVar(value=d["addresses"])

        label = tk.Label(self.mainframe, text="Diffs")
        label.grid(column=1, row=start_row, sticky=tk.W)

        box = tk.Listbox(self.mainframe, listvariable=addresses, height=20)
        box.grid(column=1, row=start_row + 1, sticky=tk.W, rowspan=2)

        def pick_diff(evt):
            cs = box.curselection()[0]
            text0.replace("1.0", "end", d["v0"][cs])
            text1.replace("1.0", "end", d["v1"][cs])

        box.bind('<<ListboxSelect>>', pick_diff)

        text0 = tk.Text(self.mainframe, width=self.data_width, height=10)
        text0.grid(column=2, row=start_row + 1, sticky=tk.W)

        text1 = tk.Text(self.mainframe, width=self.data_width, height=10)
        text1.grid(column=2, row=start_row + 2, sticky=tk.W)

        self.comparison_widgets.append(label)
        self.comparison_widgets.append(box)
        self.comparison_widgets.append(text0)
        self.comparison_widgets.append(text1)

    def find_diffs(self, v0, v1):
        o = { }

        o["addresses"] = [ "0x12345", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456", "0x23456" ]
        num_diffs = len(o["addresses"])
        d0 = [[ x, 2, x, 4, x, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8 ] for x in range(num_diffs) ]
        d1 = [[ x, 3, x, 5, x, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8, 1, 2, 3, 4, 5, 6, 7, 8, 1 ] for x in range(num_diffs) ]

        o["v0"] = [ self.numbers_to_hexstr(x) for x in d0 ]
        o["v1"] = [ self.numbers_to_hexstr(x) for x in d1 ]

        return o

    def numbers_to_hexstr(self, a):
        strings = [ ]
        for i,v in enumerate(a):
            if i > 0 and (i * 3) % self.data_width == 0:
                strings.append('\n')
            strings.append("%02x " % v)
        return "".join(strings)



if __name__ == '__main__':
    app = App()