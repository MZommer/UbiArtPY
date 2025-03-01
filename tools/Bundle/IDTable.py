import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from typing import List

from UbiArtPY import Fat, Path, IDTable


class IDTableApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("IDTable Generator")
        self.root.geometry("450x350")
        self.root.resizable(True, True)

        self.bundles: List[str] = []
        self.id_table = IDTable()

        self.create_main_layout()

    def create_main_layout(self):
        # Frames
        control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        bundles_frame = ttk.Frame(self.root)
        bundles_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Controls
        self.add_bundles_button = ttk.Button(control_frame, text="Add Bundles", command=self.add_bundles_thread)
        self.add_bundles_button.pack(side="left", padx=5)

        self.load_securefat_button = ttk.Button(control_frame, text="Load Secure FAT",
                                                command=self.load_securefat_thread)
        self.load_securefat_button.pack(side="left", padx=5)

        self.generate_idtable_button = ttk.Button(control_frame, text="Generate IDTable",
                                                  command=self.generate_idtable_thread)
        self.generate_idtable_button.pack(side="left", padx=5)

        ttk.Button(control_frame, text="Exit", command=self.root.quit).pack(side="right", padx=5)

        # Bundles frame layout
        bundles_tree_frame = ttk.Frame(bundles_frame)
        bundles_tree_frame.pack(fill="both", expand=True, side="left")

        bundles_scroll = ttk.Scrollbar(bundles_tree_frame, orient="vertical")
        bundles_scroll.pack(side="right", fill="y")

        self.bundle_tree = ttk.Treeview(
            bundles_tree_frame, columns="Order", show="tree", selectmode="browse", yscrollcommand=bundles_scroll.set,
            height=10
        )
        self.bundle_tree.heading("#0", text="Bundles")
        self.bundle_tree.heading("Order", text="Order")
        self.bundle_tree.column("#0", width=300, anchor="w")
        self.bundle_tree.column("Order", width=25, anchor="e")
        self.bundle_tree.pack(fill="both", expand=True, side="left")
        bundles_scroll.config(command=self.bundle_tree.yview)

        bundle_buttons = ttk.Frame(bundles_frame)
        bundle_buttons.pack(fill="y", side="right", padx=5)

        ttk.Button(bundle_buttons, text="Move Up", command=lambda: self.move_bundle(-1)).pack(fill="x", pady=2)
        ttk.Button(bundle_buttons, text="Move Down", command=lambda: self.move_bundle(1)).pack(fill="x", pady=2)
        ttk.Button(bundle_buttons, text="Delete", command=self.delete_bundle).pack(fill="x", pady=2)

        # Progress bar and status label
        self.progress_frame = ttk.Frame(self.root)
        self.progress_frame.pack(fill="x", padx=10, pady=5)

        self.progress_label = ttk.Label(self.progress_frame, text="Status: Idle")
        self.progress_label.pack(side="left", padx=5)

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode="determinate")
        self.progress_bar.pack(fill="x", expand=True, padx=5)

    def add_bundles_thread(self):
        self.progress_label.config(text="Status: Adding bundles...")
        self.progress_bar["value"] = 0
        thread = threading.Thread(target=self.add_bundles)
        thread.start()
        self.root.after(100, self.check_thread, thread)

    def add_bundles(self):
        files = filedialog.askopenfilenames(title="Select Bundle Files", filetypes=[("IPK Files", "*.ipk")])
        if files:
            for file in files:
                if file not in self.bundles:
                    self.bundles.append(Path(file).get_basename_without_extension())
            self.refresh_bundle_tree()
        self.progress_label.config(text="Status: Idle")
        self.progress_bar["value"] = 100

    def load_securefat_thread(self):
        self.progress_label.config(text="Status: Loading Secure FAT...")
        self.progress_bar["value"] = 0
        thread = threading.Thread(target=self.load_securefat)
        thread.start()
        self.root.after(100, self.check_thread, thread)

    def load_securefat(self):
        securefat_path = filedialog.askopenfilename(title="Select Secure FAT File", filetypes=[("GF Files", "*.gf")])
        if securefat_path:
            try:
                securefat = Fat()
                if securefat.load(Path(securefat_path)):
                    platform: str = simpledialog.askstring("Platform", "Please enter the securefat platform:")
                    for bundle in securefat.bundles:
                        file_name = f"{bundle}_{platform}"
                        if file_name not in self.bundles:
                            self.bundles.append(file_name)
                    self.refresh_bundle_tree()
                    messagebox.showinfo("Success", "Bundles loaded from Secure FAT successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load Secure FAT: {e}")
        self.progress_label.config(text="Status: Idle")
        self.progress_bar["value"] = 100

    def generate_idtable_thread(self):
        self.progress_label.config(text="Status: Generating IDTable...")
        self.progress_bar["value"] = 0
        thread = threading.Thread(target=self.generate_idtable)
        thread.start()
        self.root.after(100, self.check_thread, thread)

    def generate_idtable(self):
        destination = filedialog.asksaveasfilename(title="Save IDTable", defaultextension=".idt")
        if destination:
            try:
                for bundle in self.bundles:
                    self.id_table.insert_file(Path(bundle))
                if self.id_table.generate(Path(destination)):
                    messagebox.showinfo("Success", f"IDTable saved successfully to {destination}")
                else:
                    messagebox.showerror("Error", "Failed to save IDTable.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save IDTable: {e}")
        self.progress_label.config(text="Status: Idle")
        self.progress_bar["value"] = 100

    def refresh_bundle_tree(self):
        self.bundle_tree.delete(*self.bundle_tree.get_children())
        for index, bundle in enumerate(self.bundles):
            self.bundle_tree.insert("", "end", text=bundle, values=(index + 1,))

    def move_bundle(self, steps: int):
        """Moves the selected bundle up or down by the specified number of steps."""
        selected = self.bundle_tree.selection()
        if selected:
            index = self.bundle_tree.index(selected[0])
            new_index = index + steps

            # Ensure the new index is within valid bounds
            if 0 <= new_index < len(self.bundles):
                self.bundles[index], self.bundles[new_index] = self.bundles[new_index], self.bundles[index]
                self.refresh_bundle_tree()

                self.bundle_tree.selection_set(self.bundle_tree.get_children()[new_index])

    def delete_bundle(self):
        selected = self.bundle_tree.selection()
        if selected:
            index = self.bundle_tree.index(selected[0])
            del self.bundles[index]
            self.refresh_bundle_tree()

    def check_thread(self, thread):
        if thread.is_alive():
            self.root.after(100, self.check_thread, thread)
        else:
            self.progress_label.config(text="Status: Idle")
            self.progress_bar["value"] = 100


if __name__ == "__main__":
    root = tk.Tk()
    app = IDTableApp(root)
    root.mainloop()
