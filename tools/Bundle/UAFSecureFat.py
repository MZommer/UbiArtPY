import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from UbiArtPY import PackFile, Versioning, FatBuilder, StringID
import os
import threading

class UafSecureFat:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure FATs Utility")
        self.root.geometry("900x700")
        self.root.resizable(False, False)

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

        files_frame = ttk.LabelFrame(self.root, text="Files in FAT", padding=10)
        files_frame.pack(fill="both", expand=True, padx=10, pady=5)

        engine_frame = ttk.LabelFrame(self.root, text="Engine Info", padding=10)
        engine_frame.pack(fill="x", padx=10, pady=5)

        # Controls
        self.add_bundles_button = ttk.Button(control_frame, text="Add Bundles", command=self.add_bundles_thread)
        self.add_bundles_button.pack(side="left", padx=5)
        
        ttk.Button(control_frame, text="Reload All Bundles", command=self.reload_all_bundles).pack(side="left", padx=5)
        
        ttk.Button(control_frame, text="Save Secure FAT", command=self.save_securefat).pack(side="left", padx=5)

        ttk.Button(control_frame, text="Exit", command=self.root.quit).pack(side="right", padx=5)

        # Bundles frame layout
        bundles_tree_frame = ttk.Frame(bundles_frame)
        bundles_tree_frame.pack(fill="both", expand=True, side="left")

        bundles_scroll = ttk.Scrollbar(bundles_tree_frame, orient="vertical")
        bundles_scroll.pack(side="right", fill="y")

        self.bundle_tree = ttk.Treeview(
            bundles_tree_frame, columns=("Order"), show="tree", selectmode="browse", yscrollcommand=bundles_scroll.set, height=10
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

        # Files list with scrollbar
        files_container = ttk.Frame(files_frame)
        files_container.pack(fill="both", expand=True)

        files_scroll = ttk.Scrollbar(files_container, orient="vertical")
        files_scroll.pack(side="right", fill="y")

        self.files_tree = ttk.Treeview(
            files_container, columns=("Bundle", "StringID"), show="tree", yscrollcommand=files_scroll.set, height=10
        )
        self.files_tree.heading("#0", text="Files")
        self.files_tree.heading("Bundle", text="Bundle")
        self.files_tree.heading("StringID", text="StringID")
        self.files_tree.column("#0", width=500, anchor="w")
        self.files_tree.column("Bundle", width=50, anchor="e")
        self.files_tree.column("StringID", width=5, anchor="e")
        self.files_tree.pack(fill="both", expand=True)
        files_scroll.config(command=self.files_tree.yview)

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

    def add_bundles_thread(self):
        thread = threading.Thread(target=self.add_bundle)
        thread.start()

    def add_bundle(self):
        self.add_bundles_button.config(state="disabled")
        files = filedialog.askopenfilenames(title="Select Bundle Files", filetypes=[("IPK Files", "*.ipk")])
        if files:
            try:
                for file in files:
                    if file in self.bundles:
                        messagebox.showwarning("Warning", f"Bundle {os.path.basename(file)} is already added.")
                        continue

                    with PackFile(file, "r") as unpacker:
                        if self.platform is None:
                            self.platform = unpacker.Header.Platform
                        elif self.platform != unpacker.Header.Platform:
                            raise ValueError("All bundles must have the same platform.")

                        self.bundles.append(file)
                        self.files[file] = {f: StringID(f) for f in unpacker.Files}

                self.refresh_bundle_tree()
                self.update_engine_info()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load bundle: {e}")
                raise e
        self.add_bundles_button.config(state="normal")

    def refresh_bundle_tree(self):
        self.bundle_tree.delete(*self.bundle_tree.get_children())
        for index, bundle in enumerate(self.bundles):
            bundle_id = self.bundle_tree.insert("", "end", text=os.path.basename(bundle), values=(index + 1))
            for file, string_id in self.files[bundle].items():
                self.bundle_tree.insert(bundle_id, "end", text=file, values=(f"{string_id.GetHashCode():0x}".upper(),))

        self.refresh_files_tree()

    def refresh_files_tree(self):
        self.files_tree.delete(*self.files_tree.get_children())
        file_collisions = {}

        for bundle, file_list in self.files.items():
            for file, string_id in file_list.items():
                if file not in file_collisions:
                    file_collisions[file] = []
                file_collisions[file].append((bundle, string_id))

        for file, bundles in file_collisions.items():
            file_id = self.files_tree.insert(
                "", "end", text=file, 
                values=(os.path.basename(bundles[0][0]) if len(bundles) == 1 else "Collision", f"{bundles[0][1].GetHashCode():0x}".upper())
            )
            if len(bundles) > 1:
                self.files_tree.item(file_id, tags=("collision",))
                for bundle, _ in bundles:
                    self.files_tree.insert(file_id, "end", text=os.path.basename(bundle))

        self.files_tree.tag_configure("collision", background="red")

    def move_bundle_up(self):
        selected = self.bundle_tree.selection()
        if selected:
            index = self.bundle_tree.index(selected[0])
            if index > 0:
                self.bundles[index], self.bundles[index - 1] = self.bundles[index - 1], self.bundles[index]
                self.refresh_bundle_tree()
                self.bundle_tree.selection_set(self.bundle_tree.get_children()[index - 1])

    def move_bundle_down(self):
        selected = self.bundle_tree.selection()
        if selected:
            index = self.bundle_tree.index(selected[0])
            if index < len(self.bundles) - 1:
                self.bundles[index], self.bundles[index + 1] = self.bundles[index + 1], self.bundles[index]
                self.refresh_bundle_tree()
                self.bundle_tree.selection_set(self.bundle_tree.get_children()[index + 1])

    def reload_bundle(self):
        selected = self.bundle_tree.selection()
        if selected:
            index = self.bundle_tree.index(selected[0])
            bundle = self.bundles[index]
            try:
                with PackFile(bundle, "r") as unpacker:
                    self.files[bundle] = {f: StringID(f) for f in unpacker.Files}
                self.refresh_bundle_tree()
                messagebox.showinfo("Success", f"Bundle {os.path.basename(bundle)} reloaded successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reload bundle: {e}")
                raise e

    def reload_all_bundles(self):
        for index, bundle in enumerate(self.bundles):
            try:
                with PackFile(bundle, "r") as unpacker:
                    self.files[bundle] = {f: StringID(f) for f in unpacker.Files}
                self.refresh_bundle_tree()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to reload bundle {os.path.basename(bundle)}: {e}")
                raise e
    
    def delete_bundle(self):
        selected = self.bundle_tree.selection()
        if selected:
            index = self.bundle_tree.index(selected[0])
            del self.bundles[index]
            self.refresh_bundle_tree()

    def save_securefat(self):
        destination = filedialog.asksaveasfilename(title="Save Secure FAT", defaultextension=".gf")
        if not destination:
            return

        try:
            builder = FatBuilder()
            for bundle, file_list in self.files.items():
                for file in file_list:
                    builder.referenceFile(file, bundle)

            builder.save(destination)
            messagebox.showinfo("Success", f"Secure FAT saved successfully to {destination}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save Secure FAT: {e}")
            raise e

    def update_engine_info(self):
        self.engine_signature_label.config(text=str(Versioning.EngineSignature))
        self.engine_label.config(text=str(Versioning.Engine))
        self.platform_label.config(text=self.platform if self.platform else "N/A")

if __name__ == "__main__":
    root = tk.Tk()
    app = UafSecureFat(root)
    root.mainloop()