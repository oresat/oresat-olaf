from tkinter import ttk, filedialog
import subprocess
import time
import tkinter as tk

DANGEROUS_PACKAGES = {"systemd", "kmod", "libc6", "udev", "grub-common"}

class PackageManagementDialog(tk.Toplevel):

    def __init__(self, master, on_apply, existing_instructions=None):
        super().__init__(master)
        self.title("System Package Management")
        self.geometry("800x500")
        self.transient(master)
        self.on_apply = on_apply
        self.existing_instructions = existing_instructions or []

        self.available_packages = self._get_dpkg_list()
        self.selected_packages_remove = []
        self.selected_packages_purge = []

        self._preload_selected_packages()
        self._create_widgets()


    def _create_widgets(self):
        self.dpkg_remove_left = self._create_list_section("DPKG_REMOVE", 0, self.selected_packages_remove)
        self.dpkg_purge_left = self._create_list_section("DPKG_PURGE", 1, self.selected_packages_purge)

        btn = ttk.Button(self, text="Apply", command=self._on_apply)
        btn.pack(side="right", padx=10, pady=10)


    def _create_list_section(self, title, row, selected_packages):
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

        ttk.Button(button_frame, text=">>", command=lambda: self._move_items(left, right, selected_packages)).pack(pady=(0, 5))
        ttk.Button(button_frame, text="<<", command=lambda: self._move_items(right, left, selected_packages)).pack()

        # Populate installed packages
        for p in self.available_packages:
            if p not in selected_packages:
                left.insert(tk.END, p)

        for p in selected_packages:
            right.insert(tk.END, p)

        return right


    def _move_items(self, from_listbox, to_listbox, target_list):
        for i in reversed(from_listbox.curselection()):
            item = from_listbox.get(i)
            to_listbox.insert(tk.END, item)
            from_listbox.delete(i)
            if to_listbox is not from_listbox:
                if item not in target_list:
                    target_list.append(item)
                else:
                    target_list.remove(item)


    def _get_dpkg_list(self):
        try:
            result = subprocess.run(["apt", "list", "--installed"], capture_output=True, text=True, check=True)
            lines = result.stdout.splitlines()
            return sorted(set(
                line.split('/')[0] for line in lines
                if '[automatic]' not in line and '/' in line and line.split('/')[0] not in DANGEROUS_PACKAGES
            ))
        except Exception as e:
            print(f"DPKG list failed: {e}")
            return []


    def _on_apply(self):
        result = []
        if self.selected_packages_remove:
            result.append({"type": "DPKG_REMOVE", "items": list(self.selected_packages_remove)})
        if self.selected_packages_purge:
            result.append({"type": "DPKG_PURGE", "items": list(self.selected_packages_purge)})
        if result:
            self.on_apply(result)
        self.destroy()


    def _preload_selected_packages(self):
        remove_set = set()
        purge_set = set()

        for instr in self.existing_instructions:
            if instr.get("type") == "DPKG_REMOVE":
                remove_set.update(instr.get("items", []))
            elif instr.get("type") == "DPKG_PURGE":
                purge_set.update(instr.get("items", []))

        self.selected_packages_remove.extend([pkg for pkg in self.available_packages if pkg in remove_set])
        self.selected_packages_purge.extend([pkg for pkg in self.available_packages if pkg in purge_set])

        # Remove already selected packages from available list to avoid duplicates
        self.available_packages = [pkg for pkg in self.available_packages if pkg not in remove_set and pkg not in purge_set]

        print("Preloaded REMOVE:", self.selected_packages_remove)
#        print("Preloaded PURGE:", self.selected_packages_purge)
#        print("Remaining AVAILABLE:", self.available_packages)

