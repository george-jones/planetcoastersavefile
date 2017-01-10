from tkinter import filedialog
import tkinter as tk
from tkinter import ttk
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
        self.version_labels = [ ]
        self.comparison_widgets = [ ]

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0)
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        ttk.Label(mainframe, text="Planet Coaster Save File Analyzer", font=("TkHeadingFont", 12)).grid(column=1, row=1, sticky=tk.W)
        ttk.Button(mainframe, text="Find Save File", command=self.find_file).grid(column=1, row=2, sticky=tk.W)

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
            for r in self.version_labels:
                r.destroy()
            self.version_labels = [ ]
            self.file_watcher = filewatcher.FileWatcher(save_file_name, 2, self.file_changed)

    def file_changed(self, filename, modtime):
        self.get_file(filename, modtime)

    def get_file(self, filename, modtime):
        temp_file_name = os.path.join(self.temp_dir, 'temp.pcsf')
        shutil.copyfile(filename, temp_file_name)
        sf = pcsf.PlanetCoasterSaveFile(temp_file_name)
        self.file_versions.append(sf)
        n = len(self.file_versions)

        def save_raw():
            suggested = "%d.pcsf" % (modtime)
            save_file_name = filedialog.asksaveasfilename(initialfile=suggested, filetypes=(("Planet Coaster Save File", "*.pcsf"),("All files","*.*")))
            if save_file_name:
                sf.write_raw_file(save_file_name)

        r = ttk.Label(self.mainframe, text="Version %d" % (modtime))
        r.grid(column=1, row=n+2, sticky=tk.W)
        r = ttk.Button(self.mainframe, text="Save Raw", command=save_raw)
        r.grid(column=2, row=n+2, sticky=tk.W)        
        self.version_labels.append(r)


if __name__ == '__main__':
    app = App()