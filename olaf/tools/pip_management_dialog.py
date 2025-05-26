from tkinter import ttk, filedialog
import subprocess
import time
import tkinter as tk


class PipManagementDialog(tk.Toplevel):

    def __init__(self, master, on_apply, existing_instructions=None):
        super().__init__(master)
        self.title("PIP Package Management")
        self.geometry("700x300")
        self.transient(master)
        self.on_apply = on_apply
        self.existing_instructions = existing_instructions or []

        self.available_packages = self._get_pip_list()
        self.selected_packages_uninstall = []

        self._preload_selected_packages()
        self._create_widgets()


    def _preload_selected_packages(self):
        uninstall_set = set()

        for instr in self.existing_instructions:
            if instr.get("type") == "PIP_UNINSTALL":
                uninstall_set.update(instr.get("items", []))

        self.selected_packages_uninstall.extend([
            pkg for pkg in self.available_packages if pkg in uninstall_set
        ])

        # Remove from available
        self.available_packages = [
            pkg for pkg in self.available_packages if pkg not in uninstall_set
        ]

        print("Preloaded PIP_UNINSTALL:", self.selected_packages_uninstall)


    def _create_widgets(self):
        self.pip_uninstall = self._create_list_section("PIP_UNINSTALL", 0)

        btn = ttk.Button(self, text="Apply", command=self._on_apply)
        btn.pack(side="right", padx=10, pady=10)


    def _create_list_section(self, title, row):
        frame = ttk.LabelFrame(self, text=title)
        frame.pack(fill="x", padx=10, pady=5)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(2, weight=1)

        left = tk.Listbox(frame, selectmode="extended", exportselection=False, width=40, height=10)
        right = tk.Listbox(frame, selectmode="extended", exportselection=False, width=40, height=10)

        left.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        right.grid(row=0, column=2, padx=5, pady=5, sticky="nsew")

        # Add vertical buttons properly
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(button_frame, text=">>", command=lambda: self._move_items(left, right)).pack(pady=(0, 5))
        ttk.Button(button_frame, text="<<", command=lambda: self._move_items(right, left)).pack()

        # ✅ Use preloaded lists
        for p in self.available_packages:
            left.insert(tk.END, p)

        for p in self.selected_packages_uninstall:
            right.insert(tk.END, p)

        return right


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
        result = []

        existing_set = set()
        for instr in self.existing_instructions:
            if instr.get("type") == "PIP_UNINSTALL":
                existing_set.update(instr.get("items", []))

        # Compare current selected packages to existing ones
        current_items = self.pip_uninstall.get(0, tk.END)
        new_items = [pkg for pkg in current_items if pkg not in existing_set]

        if new_items:
            result.append({"type": "PIP_UNINSTALL", "items": new_items})

        if result:
            self.on_apply(result)
        self.destroy()
