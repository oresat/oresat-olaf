from package_management_dialog import PackageManagementDialog
from pip_management_dialog import PipManagementDialog
from tkinter import ttk, filedialog
import csv
import io
import json
import os
import re
import requests
import subprocess
import tarfile
import time
import tkinter as tk

VALID_TYPES = [
    "BASH_SCRIPT",
    "DPKG_INSTALL",
    "DPKG_REMOVE",
    "DPKG_PURGE",
    "PIP_INSTALL",
    "PIP_UNINSTALL",
    "UNKNOWN"
]

class OlafInstructionEditor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OreSat OLAF Instruction Editor")
        self.geometry("800x600")
        self.instructions = []
        self._create_widgets()

    def _create_widgets(self):
        top_row = ttk.Frame(self, padding=10)
        top_row.pack(fill="x")

        # Row 1: Card Selection
        card_row = ttk.Frame(self, padding=(10, 10))
        card_row.pack(fill="x")

        ttk.Label(card_row, text="Select a Card:", width=15).pack(side="left")
        self.card_var = tk.StringVar()
        self.card_dropdown = ttk.Combobox(card_row, textvariable=self.card_var, width=30, state="readonly")
        self.card_dropdown.pack(side="left", padx=(0, 10))
        self.card_dropdown['values'] = ["Friendly Name (real-card-name)"]
        self.card_dropdown.current(0)

        # Row 2: Add, update, remove packages and files
        action_row = ttk.Frame(self, padding=(10, 5))
        action_row.pack(fill="x")

        ttk.Button(action_row, text="Load Archive", command=self._load_archive).pack(side="left", padx=(0, 5))
        ttk.Button(action_row, text="Add File", command=self._browse_files).pack(side="left", padx=(0, 5))

        button_group = ttk.LabelFrame(action_row, text="Package Management")
        button_group.pack(side="right")

        ttk.Button(button_group, text="System Packages", command=self._open_sys_pkg_mgmt).pack(side="left", padx=5, pady=5)
        ttk.Button(button_group, text="PIP Packages", command=self._open_pip_pkg_mgmt).pack(side="left", padx=5, pady=5)

        # Row 3: Display instructions.txt content
        tree_row = ttk.Frame(self)
        tree_row.pack(fill="both", expand=True, padx=10, pady=5)

        # Left: Up/Down buttons stacked vertically
        nav_col = ttk.Frame(tree_row)
        nav_col.pack(side="left", fill="y", padx=(0, 5))

        ttk.Button(nav_col, text="↑", command=self._move_up, width=3).pack(pady=2)
        ttk.Button(nav_col, text="↓", command=self._move_down, width=3).pack(pady=2)

        # Right: Treeview
        tree_container = ttk.Frame(tree_row)
        tree_container.pack(side="left", fill="both", expand=True)

        self.tree = ttk.Treeview(tree_container, columns=("type", "items", "action"), show="headings", selectmode="browse")
        self.tree.heading("type", text="Type")
        self.tree.heading("items", text="Items")
        self.tree.heading("action", text="")
        self.tree.column("type", width=150)
        self.tree.column("items", width=500)
        self.tree.column("action", width=40, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree.bind("<Double-1>", self._on_double_click)

        # Row 4: 
        button_row = ttk.Frame(self, padding=10)
        button_row.pack(fill="x")

        ttk.Button(button_row, text="Up", command=self._move_up).pack(side=tk.LEFT)
        ttk.Button(button_row, text="Down", command=self._move_down).pack(side=tk.LEFT, padx=(5, 20))
        ttk.Button(button_row, text="Delete", command=self._delete_selected).pack(side=tk.LEFT)
        ttk.Button(button_row, text="Generate", command=self._on_generate).pack(side=tk.RIGHT)


    def _add_remove_package(self):
        index = len(self.instructions)  # future row index
        pkg = self._prompt_for_package()
        if pkg:
            self.instructions.append({"type": "DPKG_REMOVE", "items": [pkg]})
            self._render_tree()


    def _prompt_for_package(self):
        try:
            result = subprocess.run(["apt", "list", "--installed"], capture_output=True, text=True, check=True)
            lines = result.stdout.splitlines()
            packages = sorted(set(
                line.split('/')[0] for line in lines
                if '[automatic]' not in line and '/' in line and line.split('/')[0] not in DANGEROUS_PACKAGES
            ))
        except Exception as e:
            print(f"❌ Failed to get package list: {e}")
            return None

        popup = tk.Toplevel(self)
        popup.title("Select Package to Remove")
        popup.geometry("400x300")
        popup.transient(self)

        listbox = tk.Listbox(popup, selectmode=tk.SINGLE)
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        for pkg in packages:
            listbox.insert(tk.END, pkg)

        selected = tk.StringVar(value=None)

        def apply():
            sel = listbox.curselection()
            if sel:
                selected.set(listbox.get(sel[0]))
            popup.destroy()

        ttk.Button(popup, text="OK", command=apply).pack(pady=(0, 10))
        self._safe_grab(popup)
        self.wait_window(popup)

        return selected.get() if selected.get() else None


    def _browse_files(self):
        paths = filedialog.askopenfilenames(title="Select files to add to OLAF App")
        for path in paths:
            inferred_type = self._infer_type_from_filename(path)
            rel_path = os.path.basename(path)
            self.instructions.append({"type": inferred_type, "items": [rel_path]})
        self._render_tree()


    def _render_tree(self):
        self.tree.delete(*self.tree.get_children())
        for i, instr in enumerate(self.instructions):
            items_text = ", ".join(instr["items"])
            self.tree.insert("", "end", iid=str(i), values=(instr["type"], items_text, "❌"))


    def _delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = int(selected[0])
        del self.instructions[index]
        self._render_tree()


    def _move_up(self):
        selected = self.tree.selection()
        if not selected:
            return
        idx = int(selected[0])
        if idx == 0:
            return
        self.instructions[idx], self.instructions[idx - 1] = self.instructions[idx - 1], self.instructions[idx]
        self._render_tree()
        self.tree.selection_set(str(idx - 1))


    def _move_down(self):
        selected = self.tree.selection()
        if not selected:
            return
        idx = int(selected[0])
        if idx >= len(self.instructions) - 1:
            return
        self.instructions[idx], self.instructions[idx + 1] = self.instructions[idx + 1], self.instructions[idx]
        self._render_tree()
        self.tree.selection_set(str(idx + 1))


    def _on_generate(self):

        # 🧱 Step 1: Flatten the instruction rows
        flat = [{"type": instr["type"], "item": instr["items"][0]} for instr in self.instructions]

        # 🧠 Step 2: Group by consecutive rows with same type
        grouped = []
        current_group = None

        for entry in flat:
            if not current_group or current_group["type"] != entry["type"]:
                current_group = {"type": entry["type"], "items": [entry["item"]]}
                grouped.append(current_group)
            else:
                current_group["items"].append(entry["item"])

        # 📝 Step 3: Write to instructions.txt
        try:
            with open("instructions.txt", "w") as f:
                json.dump(grouped, f, indent=4)
            print("✅ instructions.txt written.")
        except Exception as e:
            print(f"❌ Failed to write instructions.txt: {e}")
            return

        # 📦 Step 4: Package into tar.xz with timestamp and card name
        raw_card = self.card_var.get()
        match = re.search(r'\(([^)]+)\)', raw_card)
        card_name = match.group(1) if match else "unknown"
        timestamp = int(time.time() * 1000)
        archive_name = f"{card_name}_update_{timestamp}.tar.xz"

        try:
            with tarfile.open(archive_name, "w:xz") as tar:
                tar.add("instructions.txt")
                for instr in self.instructions:
                    item = instr["items"][0]
                    if os.path.isfile(item):
                        arcname = os.path.basename(item)  # or use os.path.relpath(item) if needed
                        tar.add(item, arcname=arcname)
            print(f"✅ Created archive: {archive_name}")
        except Exception as e:
            print(f"❌ Failed to create archive: {e}")


    def _load_archive(self):
        path = filedialog.askopenfilename(filetypes=[("Tar XZ Files", "*.tar.xz")])
        if not path:
            return
        try:
            with tarfile.open(path, "r:xz") as tar:
                f = tar.extractfile("instructions.txt")
                data = json.load(f)
        except Exception as e:
            print(f"❌ Load failed: {e}")
            return
        self.instructions = []
        for entry in data:
            for item in entry["items"]:
                self.instructions.append({"type": entry["type"], "items": [item]})
        self._render_tree()


    def _infer_type_from_filename(self, filename):
        lower = filename.lower()
        if lower.endswith(".sh"):
            return "BASH_SCRIPT"
        elif lower.endswith(".deb"):
            return "DPKG_INSTALL"
        elif "requirements.txt" in lower or lower.endswith(".pip"):
            return "PIP_INSTALL"
        elif lower.endswith(".uninstall.pip"):
            return "PIP_UNINSTALL"
        else:
            return "UNKNOWN"


    def _populate_card_list(self):
        try:
            with open("cards.csv", "r", encoding="utf-8") as f:
                csv_data = f.read()
        except Exception as e:
            print(f"⚠️ Failed to load local cards.csv: {e}")
            csv_data = ""

#        csv_url = "https://raw.githubusercontent.com/oresat/oresat-configs/master/oresat_configs/oresat0/cards.csv"
#        try:
#            response = requests.get(csv_url)
#            response.raise_for_status()
#            csv_data = response.text
#        except Exception as e:
#            print(f"⚠️ Failed to fetch CSV: {e}")
#            csv_data = ""

        reader = csv.DictReader(io.StringIO(csv_data))
        options = [
            f"{row['nice_name'].strip()} ({row['name'].strip()})"
            for row in reader
            if 'name' in row and 'nice_name' in row and row['name'] and row['nice_name']
        ]
        self.card_dropdown['values'] = options


    def _on_double_click(self, event):
        item_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)

        if not item_id:
            return  # clicked empty space, do nothing

        if col == '#1' and item_id:
            self._edit_type_popup(int(item_id))
        if col == '#3':  # delete column
            self._delete_instruction(int(item_id))


    def _edit_type_popup(self, index):
        popup = tk.Toplevel(self)
        popup.title("Edit Type")
        popup.geometry("300x100")
        popup.transient(self)

        type_var = tk.StringVar(value=self.instructions[index]["type"])
        dropdown = ttk.Combobox(popup, textvariable=type_var, values=VALID_TYPES, state="readonly")
        dropdown.pack(pady=10, padx=10)

        button_frame = ttk.Frame(popup)
        button_frame.pack(pady=(5, 10), padx=10, anchor="e")

        ttk.Button(button_frame, text="Save", command=lambda: self._save_type_edit(popup, index, type_var)).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=lambda: self._cancel_popup(popup)).pack(side="right")

        self._safe_grab(popup)


    def _delete_instruction(self, index):
        if 0 <= index < len(self.instructions):
            del self.instructions[index]
            self._render_tree()


    def _cancel_popup(self, popup):
        try:
            popup.grab_release()  # In case grab_set() was applied
        except tk.TclError:
            pass

        if popup.winfo_exists():
            popup.destroy()


    def _save_type_edit(self, popup, index, type_var):
        self.instructions[index]["type"] = type_var.get()
        self._render_tree()
        popup.destroy()


    def _safe_grab(self, window):
        ''' 
        safer grab_set after popup is viewable
        '''
        if not window.winfo_exists():
            return
        
        try:
            window.grab_set()
        except tk.TclError:
            window.after(10, lambda: self._safe_grab(window) if window.winfo_exists() else None)
            

    def _open_sys_pkg_mgmt(self):
        def apply(instructions):
            self.instructions.extend(instructions)
            self._render_tree()
        PackageManagementDialog(self, on_apply=apply)


    def _open_pip_pkg_mgmt(self):
        def apply(instructions):
            self.instructions.extend(instructions)
            self._render_tree()
        PipManagementDialog(self, on_apply=apply)


if __name__ == "__main__":
    app = OlafInstructionEditor()
    app.mainloop()
