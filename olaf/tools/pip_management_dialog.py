from tkinter import ttk, filedialog
import subprocess
import time
import tkinter as tk


class PipManagementDialog(tk.Toplevel):

    def __init__(self, master, on_apply):
        super().__init__(master)
        self.title("PIP Package Management")
        self.geometry("700x300")
        self.transient(master)
        self.on_apply = on_apply
        self._create_widgets()
        master._safe_grab(self)


    def _create_widgets(self):
        frame = ttk.LabelFrame(self, text="PIP_UNINSTALL")
        frame.pack(fill="x", padx=10, pady=10)

        self.left = tk.Listbox(frame, selectmode="extended", exportselection=False, width=40, height=10)
        self.right = tk.Listbox(frame, selectmode="extended", exportselection=False, width=40, height=10)

        self.left.grid(row=0, column=0, padx=5, pady=5)
        self.right.grid(row=0, column=2, padx=5, pady=5)

        for btn_text, f, t in [(">>", self.left, self.right), ("<<", self.right, self.left)]:
            ttk.Button(frame, text=btn_text, command=lambda f=f, t=t: 
                    self._move_items(f, t)).grid(row=0, column=1, pady=2, padx=2, sticky="n")

        pkgs = self._get_pip_list()
        for p in pkgs:
            self.left.insert(tk.END, p)

        ttk.Button(self, text="Apply", command=self._on_apply).pack(pady=10)


    def _move_items(self, from_listbox, to_listbox):
        for i in reversed(from_listbox.curselection()):
            item = from_listbox.get(i)
            to_listbox.insert(tk.END, item)
            from_listbox.delete(i)


    def _get_pip_list(self):
        try:
            result = subprocess.run(["pip", "list"], capture_output=True, text=True, check=True)
            lines = result.stdout.splitlines()[2:]
            return sorted(line.split()[0] for line in lines if line)
        except Exception as e:
            print(f"PIP list failed: {e}")
            return []


    def _on_apply(self):
        items = self.right.get(0, tk.END)
        if items:
            self.on_apply([{"type": "PIP_UNINSTALL", "items": list(items)}])
        self.destroy()

