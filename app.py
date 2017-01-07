from tkinter import filedialog
import tkinter as tk
from tkinter import ttk
import tempfile

import filewatcher

class App():

    def __init__(self):        
        self.temp_dir = tempfile.gettempdir()
        self.file_watcher = None

        root = tk.Tk()
        root.wm_title("PCSFA")

        self.root = root        

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)

        ttk.Label(mainframe, text="Planet Coaster Save File Analyzer", font=("TkHeadingFont", 12)).grid(column=1, row=1, sticky=tk.E)
        ttk.Button(mainframe, text="Find Save File", command=self.find_file).grid(column=1, row=2, sticky=tk.E)

        for child in mainframe.winfo_children():
            child.grid_configure(padx=5, pady=5)

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
            self.file_watcher = filewatcher.FileWatcher(save_file_name, 2, self.file_changed)

    def file_changed(self, filename):
        print("changed: " + filename)


if __name__ == '__main__':
    app = App()