import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from UbiArtPY import PackFile, Versioning, FatBuilder, StringID, Path


class UafSecureFat:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure FATs Utility")
        self.root.geometry("800x400")
        self.root.resizable(True, True)  # Allow resizing for better usability

        self.bundles = []
        self.files = {}
        self.platform = None

        self.create_main_layout()

    def create_main_layout(self):
        # Frames
        control_frame = ttk.LabelFrame(self.root, text="Controls", padding=10)
        control_frame.pack(fill="x", padx=10, pady=5)

        bundles_frame = ttk.Frame(self.root)
        bundles_frame.pack(fill="both", expand=True, padx=10, pady=5)

        engine_frame = ttk.LabelFrame(self.root, text="Engine Info", padding=10)
        engine_frame.pack(fill="x", padx=10, pady=5)

        # Controls
        self.add_bundles_button = ttk.Button(control_frame, text="Add Bundles", command=self.add_bundles_thread)
        self.add_bundles_button.pack(side="left", padx=5)

        self.reload_bundles = ttk.Button(control_frame, text="Reload All Bundles", command=self.reload_all_bundles)
        self.reload_bundles.pack(side="left", padx=5)

        self.save_fat = ttk.Button(control_frame, text="Save Secure FAT", command=self.save_securefat)
        self.save_fat.pack(side="left", padx=5)

        ttk.Button(control_frame, text="Exit", command=self.root.quit).pack(side="right", padx=5)

        # Bundles frame layout
        bundles_tree_frame = ttk.Frame(bundles_frame)
        bundles_tree_frame.pack(fill="both", expand=True, side="left")

        bundles_scroll = ttk.Scrollbar(bundles_tree_frame, orient="vertical")
        bundles_scroll.pack(side="right", fill="y")

        self.bundle_tree = ttk.Treeview(
            bundles_tree_frame, columns=("Order"), show="tree", selectmode="browse", yscrollcommand=bundles_scroll.set,
            height=10
        )
        self.bundle_tree.heading("#0", text="Bundles")
        self.bundle_tree.heading("Order", text="Order")
        self.bundle_tree.column("#0", width=600, anchor="w")
        self.bundle_tree.column("Order", width=25, anchor="e")
        self.bundle_tree.pack(fill="both", expand=True, side="left")
        bundles_scroll.config(command=self.bundle_tree.yview)

        bundle_buttons = ttk.Frame(bundles_frame)
        bundle_buttons.pack(fill="y", side="right", padx=5)

        ttk.Button(bundle_buttons, text="Move Up", command=self.move_bundle_up).pack(fill="x", pady=2)
        ttk.Button(bundle_buttons, text="Move Down", command=self.move_bundle_down).pack(fill="x", pady=2)
        ttk.Button(bundle_buttons, text="Reload", command=self.reload_bundle).pack(fill="x", pady=2)
        ttk.Button(bundle_buttons, text="Delete", command=self.delete_bundle).pack(fill="x", pady=2)

        # Engine Info
        ttk.Label(engine_frame, text="Engine Signature:").grid(row=0, column=0, sticky="w")
        self.engine_signature_label = ttk.Label(engine_frame, text="N/A")
        self.engine_signature_label.grid(row=0, column=1, sticky="w")

        ttk.Label(engine_frame, text="Engine Version:").grid(row=1, column=0, sticky="w")
        self.engine_label = ttk.Label(engine_frame, text="N/A")
        self.engine_label.grid(row=1, column=1, sticky="w")

        ttk.Label(engine_frame, text="Platform:").grid(row=2, column=0, sticky="w")
        self.platform_label = ttk.Label(engine_frame, text="N/A")
        self.platform_label.grid(row=2, column=1, sticky="w")

        # Progress Label
        self.progress_label = ttk.Label(control_frame, text="Progress: 0.00%")
        self.progress_label.pack(side="right", padx=10)

    def add_bundles_thread(self):
        """Starts a new thread to add bundles and monitors its completion."""
        self.add_bundles_button.config(state="disabled")
        self.reload_bundles.config(state="disabled")
        self.save_fat.config(state="disabled")
        thread = threading.Thread(target=self.add_bundle)
        thread.start()
        self.root.after(100, self.check_thread, thread)

    def check_thread(self, thread):
        """Checks if the thread is still running and updates the GUI accordingly."""
        if thread.is_alive():
            self.root.after(100, self.check_thread, thread)
        else:
            self.add_bundles_button.config(state="normal")
            self.reload_bundles.config(state="normal")
            self.save_fat.config(state="normal")

    def add_bundle(self):
        """Adds one or more bundles to the application. Each bundle is opened and its files are indexed."""
        files = filedialog.askopenfilenames(title="Select Bundle Files", filetypes=[("IPK Files", "*.ipk")])
        if files:
            try:
                for i, file in enumerate(files):
                    if file in self.bundles:
                        messagebox.showwarning("Warning", f"Bundle {os.path.basename(file)} is already added.")
                        continue

                    with PackFile(file, "r") as unpacker:
                        if self.platform is None:
                            self.platform = unpacker.header.platform
                        elif self.platform != unpacker.header.platform:
                            raise ValueError(
                                f"All bundles must have the same platform. Expected {self.platform}, found {unpacker.header.platform}.")

                        self.bundles.append(file)
                        self.files[file] = {f: StringID(f) for f in unpacker.files}

                    # Update progress
                    self.update_progress(i + 1, len(files))

                self.refresh_bundle_tree()
                self.update_engine_info()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load bundle: {e}")
        self.add_bundles_button.config(state="normal")
        self.reload_bundles.config(state="normal")
        self.save_fat.config(state="normal")

    def refresh_bundle_tree(self, new_bundle=None):
        """Refreshes the bundle tree view. If `new_bundle` is provided, only that bundle is added."""
        if new_bundle:
            bundle_id = self.bundle_tree.insert("", "end", text=os.path.basename(new_bundle),
                                                values=(len(self.bundles),))
            for file, string_id in self.files[new_bundle].items():
                self.bundle_tree.insert(bundle_id, "end", text=file,
                                        values=(f"{string_id.get_hash_code():0x}".upper(),))
        else:
            self.bundle_tree.delete(*self.bundle_tree.get_children())
            for index, bundle in enumerate(self.bundles):
                bundle_id = self.bundle_tree.insert("", "end", text=os.path.basename(bundle), values=(index + 1))
                for file, string_id in self.files[bundle].items():
                    self.bundle_tree.insert(bundle_id, "end", text=file,
                                            values=(f"{string_id.get_hash_code():0x}".upper(),))

    def refresh_files_tree(self):
        """Detects file collisions and informs the user."""
        file_collisions = {}
        for bundle, file_list in self.files.items():
            for file, string_id in file_list.items():
                if file not in file_collisions:
                    file_collisions[file] = []
                file_collisions[file].append((bundle, string_id))
        if file_collisions:
            messagebox.showwarning("File Collisions", f"Found {len(file_collisions)} file collisions.")

    def move_bundle_up(self):
        """Moves the selected bundle up in the list."""
        selected = self.bundle_tree.selection()
        if selected:
            index = self.bundle_tree.index(selected[0])
            if index > 0:
                self.bundles[index], self.bundles[index - 1] = self.bundles[index - 1], self.bundles[index]
                self.refresh_bundle_tree()
                self.bundle_tree.selection_set(self.bundle_tree.get_children()[index - 1])

    def move_bundle_down(self):
        """Moves the selected bundle down in the list."""
        selected = self.bundle_tree.selection()
        if selected:
            index = self.bundle_tree.index(selected[0])
            if index < len(self.bundles) - 1:
                self.bundles[index], self.bundles[index + 1] = self.bundles[index + 1], self.bundles[index]
                self.refresh_bundle_tree()
                self.bundle_tree.selection_set(self.bundle_tree.get_children()[index + 1])

    def reload_bundle(self):
        """Reloads the selected bundle."""
        selected = self.bundle_tree.selection()
        if selected:
            index = self.bundle_tree.index(selected[0])
            bundle = self.bundles[index]
            self.reload_bundle_files(bundle)

    def reload_all_bundles(self):
        """Reloads all bundles."""
        for bundle in self.bundles:
            self.reload_bundle_files(bundle)

    def reload_bundle_files(self, bundle):
        """Reloads the files of a specific bundle."""
        try:
            with PackFile(bundle, "r") as unpacker:
                self.files[bundle] = {f: StringID(f) for f in unpacker.files}
            self.refresh_bundle_tree()
            messagebox.showinfo("Success", f"Bundle {os.path.basename(bundle)} reloaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reload bundle: {e}")

    def delete_bundle(self):
        """Deletes the selected bundle."""
        selected = self.bundle_tree.selection()
        if selected:
            index = self.bundle_tree.index(selected[0])
            del self.bundles[index]
            self.refresh_bundle_tree()

    def save_securefat(self):
        """Saves the Secure FAT file."""
        destination = filedialog.asksaveasfilename(title="Save Secure FAT", defaultextension=".gf")
        if not destination:
            return

        try:
            builder = FatBuilder()
            for bundle, file_list in self.files.items():
                bundleName = Path(bundle).get_basename_without_extension().rsplit("_", 1)[0]
                for file in file_list:
                    builder.reference_file(file, bundleName)

            builder.save(destination)
            messagebox.showinfo("Success", f"Secure FAT saved successfully to {destination}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save Secure FAT: {e}")

    def update_engine_info(self):
        """Updates the engine information labels."""
        self.engine_signature_label.config(text=str(Versioning.EngineSignature))
        self.engine_label.config(text=str(Versioning.Engine))
        self.platform_label.config(text=self.platform if self.platform else "N/A")

    def update_progress(self, current, total):
        """Updates the progress label."""
        progress = (current / total) * 100
        self.progress_label.config(text=f"Progress: {progress:.2f}%")


if __name__ == "__main__":
    root = tk.Tk()
    app = UafSecureFat(root)
    root.mainloop()
