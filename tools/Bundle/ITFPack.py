import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from UbiArtPY import PackFile, PLATFORMS, Path, JdVersion, Versioning
import os

class PackUnpackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pack/Unpack Utility")
        self.root.geometry("550x250")

        # Tabbed interface
        self.notebook = ttk.Notebook(root)
        self.pack_tab = ttk.Frame(self.notebook)
        self.unpack_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.pack_tab, text="Pack")
        self.notebook.add(self.unpack_tab, text="Unpack")
        self.notebook.pack(expand=True, fill="both")

        # Pack tab
        self.create_pack_tab()

        # Unpack tab
        self.create_unpack_tab()

    def create_pack_tab(self):
        ttk.Label(self.pack_tab, text="Folder to Pack:").grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.pack_folder_entry = ttk.Entry(self.pack_tab, width=50)
        self.pack_folder_entry.grid(row=0, column=1, pady=10, padx=10)
        ttk.Button(self.pack_tab, text="Browse", command=self.browse_pack_folder).grid(row=0, column=2, pady=10, padx=10)

        ttk.Label(self.pack_tab, text="Destination File:").grid(row=1, column=0, pady=10, padx=10, sticky="w")
        self.pack_destination_entry = ttk.Entry(self.pack_tab, width=50)
        self.pack_destination_entry.grid(row=1, column=1, pady=10, padx=10)
        ttk.Button(self.pack_tab, text="Browse", command=self.browse_pack_destination).grid(row=1, column=2, pady=10, padx=10)

        ttk.Label(self.pack_tab, text="Platform:").grid(row=2, column=0, pady=10, padx=10, sticky="w")
        self.platform_var = tk.StringVar(value=PLATFORMS[0].Name)
        self.platform_menu = ttk.Combobox(self.pack_tab, textvariable=self.platform_var, values=[p.Name for p in PLATFORMS], state="readonly")
        self.platform_menu.grid(row=2, column=1, pady=10, padx=10)
        self.platform_menu.bind("<<ComboboxSelected>>", self.update_versions)

        ttk.Label(self.pack_tab, text="JdVersion:").grid(row=3, column=0, pady=10, padx=10, sticky="w")
        self.jd_version_var = tk.StringVar()
        self.jd_version_menu = ttk.Combobox(self.pack_tab, textvariable=self.jd_version_var, state="readonly")
        self.jd_version_menu.grid(row=3, column=1, pady=10, padx=10)

        ttk.Button(self.pack_tab, text="Pack Folder", command=self.pack_folder).grid(row=4, column=0, columnspan=3, pady=20)

        # Initialize JD versions based on the default platform
        self.update_versions()

    def create_unpack_tab(self):
        ttk.Label(self.unpack_tab, text="Bundle to Unpack:").grid(row=0, column=0, pady=10, padx=10, sticky="w")
        self.unpack_file_entry = ttk.Entry(self.unpack_tab, width=50)
        self.unpack_file_entry.grid(row=0, column=1, pady=10, padx=10)
        ttk.Button(self.unpack_tab, text="Browse", command=self.browse_unpack_file).grid(row=0, column=2, pady=10, padx=10)

        ttk.Label(self.unpack_tab, text="Destination Folder:").grid(row=1, column=0, pady=10, padx=10, sticky="w")
        self.unpack_destination_entry = ttk.Entry(self.unpack_tab, width=50)
        self.unpack_destination_entry.grid(row=1, column=1, pady=10, padx=10)
        ttk.Button(self.unpack_tab, text="Browse", command=self.browse_unpack_destination).grid(row=1, column=2, pady=10, padx=10)

        ttk.Button(self.unpack_tab, text="Unpack Bundle", command=self.unpack_bundle).grid(row=2, column=0, columnspan=3, pady=20)

    def browse_pack_folder(self):
        folder = filedialog.askdirectory(title="Select Folder to Pack")
        if folder:
            self.pack_folder_entry.delete(0, tk.END)
            self.pack_folder_entry.insert(0, folder)

    def browse_pack_destination(self):
        file = filedialog.asksaveasfilename(title="Select Destination File", defaultextension=".ipk",
                                            filetypes=[("IPK Files", "*.ipk")])
        if file:
            self.pack_destination_entry.delete(0, tk.END)
            self.pack_destination_entry.insert(0, file)

    def browse_unpack_file(self):
        file = filedialog.askopenfilename(title="Select Bundle File", filetypes=[("IPK Files", "*.ipk")])
        if file:
            self.unpack_file_entry.delete(0, tk.END)
            self.unpack_file_entry.insert(0, file)

    def browse_unpack_destination(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.unpack_destination_entry.delete(0, tk.END)
            self.unpack_destination_entry.insert(0, folder)

    def update_versions(self, event=None):
        platform_name = self.platform_var.get()
        platform = next((p for p in PLATFORMS if p.Name == platform_name), None)

        if platform:
            available_versions = platform.AvailableVersions
            self.jd_version_menu["values"] = [v.Name for v in available_versions]
            if available_versions:
                self.jd_version_var.set(available_versions[0].Name)

        # Call Versioning.set_game when platform or version changes
        self.set_versioning()

    def set_versioning(self):
        platform_name = self.platform_var.get()
        jd_version_name = self.jd_version_var.get()

        platform = next((p for p in PLATFORMS if p.Name == platform_name), None)
        jd_version = next((v for v in JdVersion.All if v.Name == jd_version_name), None)

        if platform and jd_version:
            Versioning.set_game(jd_version, platform)

    def pack_folder(self):
        source = self.pack_folder_entry.get()
        destination = self.pack_destination_entry.get()

        platform_name = self.platform_var.get()
        jd_version_name = self.jd_version_var.get()

        platform = next((p for p in PLATFORMS if p.Name == platform_name), None)
        jd_version = next((v for v in JdVersion.All if v.Name == jd_version_name), None)

        if not platform or not jd_version:
            messagebox.showerror("Error", "Invalid platform or JD version selected.")
            return

        if not os.path.isdir(source):
            messagebox.showerror("Error", "Please select a valid folder to pack.")
            return

        if not destination:
            messagebox.showerror("Error", "Please select a destination file.")
            return

        try:
            with PackFile(destination, "w", platform) as packer:
                root = Path(source)
                for directory, _, files in os.walk(source):
                    directory = Path(directory)
                    for file in files:
                        file = Path(file)
                        full_path = directory.copyAndAppendPath(file)
                        itf_path = Path(str(full_path).replace(str(root) + "/", ""))
                        packer.register_file(full_path, itf_path)
                packer.save()
            messagebox.showinfo("Success", f"Folder packed successfully to {destination}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to pack folder: {e}")
            raise e

    def unpack_bundle(self):
        source = self.unpack_file_entry.get()
        destination = self.unpack_destination_entry.get()

        if not os.path.isfile(source):
            messagebox.showerror("Error", "Please select a valid bundle file to unpack.")
            return

        if not destination:
            messagebox.showerror("Error", "Please select a destination folder.")
            return

        try:
            with PackFile(source, "r") as unpacker:
                unpacker.extract_all(destination)
                messagebox.showinfo("Success", f"Bundle unpacked successfully to {destination}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to unpack bundle: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PackUnpackApp(root)
    root.mainloop()
