import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import re
import yaml
from PIL import Image, ImageTk

class GameMediaAuditApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Game Media Auditor")

        self.platforms = []  # To store platform configurations

        # UI Layout
        self.setup_ui()
        

    def setup_ui(self):

        self.dir_entries = {
            'Platform Name': 'Pinball X',
            'Rom Dir': 'r:\ROMS-1G1R\pinball\Visual Pinball\Visual Pinball [VPX0-VPX08] PinMame Tables',
            'Clear Logo Dir': 'C:\Programs\LaunchBox\Images\Visual Pinball\Clear Logo',
            'Playfield Dir': 'c:\Programs\LaunchBox\Images\Visual Pinball\Screenshot - Gameplay'
        }

        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side="left", fill="both", expand=True)

        # Create a button to create a new platform
        self.new_platform_button = tk.Button(self.root, text="Create New Platform", command=self.create_new_platform)
        self.new_platform_button.pack()


        self.setup_directory_entries(self.left_frame)

        self.setup_platform_table()

        self.scan_button = tk.Button(self.left_frame, text="Scan", command=self.scan_directories)
        self.scan_button.pack(pady=10)

        # MIDDLE FRAME
        self.middle_frame = tk.Frame(self.root)
        self.middle_frame.pack(side="left", fill="both", expand=True)

        self.setup_table()
        self.setup_image_frame()

        self.image_frame.pack(side="left", fill="both", expand=True)
        self.tree.pack(side="left", fill="both", expand=True)        

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)


    def setup_directory_entries(self, parent_frame):
        for dir_name, default_path in self.dir_entries.items():
            entry_frame = tk.Frame(parent_frame)
            entry_frame.pack(anchor=tk.W, padx=5, pady=5, fill=tk.X) # Fill horizontally

            label = tk.Label(entry_frame, text=dir_name)
            label.pack(side=tk.LEFT)

            entry = tk.Entry(entry_frame, width=40, state='readonly')
            # entry.insert(0, default_path)
            entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True) # Fill and expand

            # button = tk.Button(entry_frame, text="Browse", command=lambda path_var=entry: self.browse_directory(path_var))
            # button.pack(side=tk.LEFT, padx=5)

            self.dir_entries[dir_name] = entry

    def browse_directory(self, path_var):
        directory = filedialog.askdirectory()
        if directory:
            path_var.delete(0, tk.END)
            path_var.insert(0, directory)

    def scan_directories(self):
        # Get directory paths from UI
        rom_dir = self.dir_entries['Rom Dir'].get()
        clear_logo_dir = self.dir_entries['Clear Logo Dir'].get()
        playfield_dir = self.dir_entries['Playfield Dir'].get()

        # Perform scanning and processing
        rom_files, rom_file_paths = self.scan_files(rom_dir, '.ahk')
        clear_logo_files, clear_logo_file_paths = self.scan_files(clear_logo_dir, '.png|.jpg')
        playfield_files, playfield_file_paths = self.scan_files(playfield_dir, '.png|.jpg')

        # Process files and perform regex operations
        rom_data = self.process_files(rom_files)
        clear_logo_data = self.process_files(clear_logo_files)
        playfield_data = self.process_files(playfield_files)

        # Store data in YAML
        self.store_data_in_yaml(rom_dir, rom_data, rom_file_paths,
                                clear_logo_dir, clear_logo_data, clear_logo_file_paths,
                                playfield_dir, playfield_data, playfield_file_paths)        

        # self.setup_table()
        self.populate_table()        
        # self.populate_table_with_dummy_data()

    def scan_files(self, directory, file_extensions):
        files = []
        file_paths = []

        if directory:
            for file_extension in file_extensions.split('|'):
                for root, _, files_list in os.walk(directory):
                    for file in files_list:
                        if file.endswith(file_extension):
                            files.append(file)
                            file_paths.append(os.path.join(root, file))

        return files, file_paths        

    def process_files(self, files):
        processed_data = {}
        for file in files:
            # Perform regex operations or any other required processing
            # Modify regex pattern to remove brackets and file extensions
            processed_data[file] = re.sub(r'\s*\[.*?\]\s*|\s*\([^()]*\)\s*|\.\w+$', '', file)
        return processed_data

    def store_data_in_yaml(self, rom_dir, rom_data, rom_filepaths, clear_logo_dir, clear_logo_data, clear_logo_filepaths, playfield_dir, playfield_data, playfield_filepaths):
        data = {
            'rom_dir': {
                'filename': list(rom_data.keys()),
                'filename_regexed': list(rom_data.values()),
                'filepath': rom_filepaths
            },
            'clear_logo': {
                'filename': list(clear_logo_data.keys()),
                'filename_regexed': list(clear_logo_data.values()),
                'filepath': clear_logo_filepaths
            },
            'playfield': {
                'filename': list(playfield_data.keys()),
                'filename_regexed': list(playfield_data.values()),
                'filepath': playfield_filepaths
            }
        }

        with open('out.yaml', 'w') as file:
            yaml.dump(data, file)

    def setup_table(self):
        self.tree = ttk.Treeview(self.middle_frame)
        self.tree["columns"] = ("clear_logo_found", "playfield_image_found", "rom_filepath", "clear_logo_filepath", "playfield_filepath") 
        self.tree.heading("#0", text="rom_filename_regexed")
        self.tree.heading("clear_logo_found", text="Clear Logo Found")
        self.tree.heading("playfield_image_found", text="Playfield Image Found")

        self.tree.column("#0", width=200)  # Adjust the width according to your content
        self.tree.column("clear_logo_found", width=50)
        self.tree.column("playfield_image_found", width=50)
        # self.tree.column("rom_filepath", width=0)
        # self.tree.column("clear_logo_filepath", width=0)
        # self.tree.column("playfield_filepath", width=0)

        # Expand rows to fill the whole root frame
        # self.frame.grid_rowconfigure(0, weight=1)  # Configure row 0 to expand
        # self.tree.grid(row=0, column=3, padx=5, pady=5, sticky="nsew")  # Remove rowspan attribute

        scrollbar = ttk.Scrollbar(self.middle_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = ttk.Scrollbar(self.middle_frame, orient="horizontal", command=self.tree.xview)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.tree.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def setup_image_frame(self):
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.clear_logo_image_label = tk.Label(self.image_frame)
        self.clear_logo_image_label.pack(padx=5, pady=5)

        self.playfield_image_label = tk.Label(self.image_frame)
        self.playfield_image_label.pack(padx=5, pady=5)

        # self.root.grid_rowconfigure(0, weight=1)
        # self.root.grid_columnconfigure(0, weight=1)

    def setup_table2(self):
        self.tree = ttk.Treeview(self.frame)
        self.tree["columns"] = ("clear_logo_found", "playfield_image_found", "rom_filepath", "clear_logo_filepath", "playfield_filepath") 
        self.tree.heading("#0", text="rom_filename_regexed")
        self.tree.heading("clear_logo_found", text="Clear Logo Found")
        self.tree.heading("playfield_image_found", text="Playfield Image Found")

        # Create a vertical scrollbar
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        # Create a horizontal scrollbar
        x_scrollbar = ttk.Scrollbar(self.frame, orient="horizontal", command=self.tree.xview)
        x_scrollbar.pack(side=tk.BOTTOM, fill="x")

        self.tree.configure(yscrollcommand=scrollbar.set, xscrollcommand=x_scrollbar.set)
        self.tree.pack(expand=True, fill="both", padx=5, pady=5)

        # Additional configuration to expand the window if needed
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    # def populate_table(self):
    #     # Read data from out.yaml file
    #     with open('out.yaml', 'r') as file:
    #         data = yaml.safe_load(file)

    #     # Get data from the YAML structure and populate the table
    #     rom_filenames = data.get('rom_dir', {}).get('filename_regexed', [])
    #     clear_logo_filenames = data.get('clear_logo', {}).get('filename_regexed', [])
    #     playfield_filenames = data.get('playfield', {}).get('filename_regexed', [])

    #     # Define tags for 'green' and 'red' colors
    #     self.tree.tag_configure("green", background="green")
    #     self.tree.tag_configure("red", background="red")

    #     for idx, rom_filename in enumerate(rom_filenames):
    #         # Match rom filename with clear logo and playfield filenames
    #         clear_logo_found = 'green' if rom_filename in clear_logo_filenames else 'red'
    #         playfield_found = 'green' if rom_filename in playfield_filenames else 'red'

    #         # Insert item into the treeview
    #         item_id = self.tree.insert("", "end", text=rom_filename)

    #         # Apply tags for colors to the entire row
    #         self.tree.item(item_id, tags=(clear_logo_found, playfield_found))

    #         # Define column-specific styles within the tags
    #         self.tree.tag_configure(clear_logo_found, columnspan='#2')  # Apply only to the 'clear_logo_found' column
    #         self.tree.tag_configure(playfield_found, columnspan='#3')  # Apply only to the 'playfield_image_found' column



    def populate_table(self):
        # Read data from out.yaml file
        with open('out.yaml', 'r') as file:
            data = yaml.safe_load(file)

        rom_filenames = data.get('rom_dir', {}).get('filename_regexed', [])
        clear_logo_filenames = data.get('clear_logo', {}).get('filename_regexed', [])
        playfield_filenames = data.get('playfield', {}).get('filename_regexed', [])

        rom_filepaths = data.get('rom_dir', {}).get('filepath', [])
        clear_logo_filepaths = data.get('clear_logo', {}).get('filepath', [])
        playfield_filepaths = data.get('playfield', {}).get('filepath', [])

        # Define tags for 'green' and 'red' colors
        self.tree.tag_configure("green", background="green")
        self.tree.tag_configure("red", background="red")

        for idx, rom_filename in enumerate(rom_filenames):
            # Match rom filename with clear logo and playfield filenames
            clear_logo_found = 'green' if rom_filename in clear_logo_filenames else 'red'
            playfield_found = 'green' if rom_filename in playfield_filenames else 'red'

            # Insert item into the treeview and apply tags for colors
            item_id = self.tree.insert("", "end", text=rom_filename)
            self.tree.set(item_id, "clear_logo_found", clear_logo_found)
            self.tree.set(item_id, "playfield_image_found", playfield_found)

            # Set the corresponding file paths in the Treeview
            if idx < len(rom_filepaths):
                self.tree.set(item_id, "rom_filepath", rom_filepaths[idx])
            if idx < len(clear_logo_filepaths):
                self.tree.set(item_id, "clear_logo_filepath", clear_logo_filepaths[idx])
            if idx < len(playfield_filepaths):
                self.tree.set(item_id, "playfield_filepath", playfield_filepaths[idx])            
            
            # Apply tags for colors
            self.tree.item(item_id, tags=(clear_logo_found, playfield_found))


    def populate_table_with_dummy_data(self):
        # Inserting dummy data into the treeview for demonstration
        self.tree.insert("", "end", text="File1", values=("green", "red"))
        self.tree.insert("", "end", text="File2", values=("red", "green"))
        self.tree.insert("", "end", text="File3", values=("green", "green"))

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_text = self.tree.item(selected_item, "text")
            clear_logo_filepath = self.tree.set(selected_item, "clear_logo_filepath")
            playfield_filepath = self.tree.set(selected_item, "playfield_filepath")
            print(f"Selected Item: {item_text}")
            print(f"Clear Logo Filepath: {clear_logo_filepath}")
            print(f"Playfield Filepath: {playfield_filepath}")
            self.show_images(clear_logo_filepath, playfield_filepath)

    def show_images2(self, clear_logo_filepath, playfield_filepath):
        print(f"Loading Clear Logo: {clear_logo_filepath}")
        print(f"Loading Playfield: {playfield_filepath}")
        clear_logo_image = self.load_image(clear_logo_filepath)
        playfield_image = self.load_image(playfield_filepath)

        if clear_logo_image and playfield_image:
            self.clear_logo_image_label.configure(image=clear_logo_image)
            self.clear_logo_image_label.image = clear_logo_image

            self.playfield_image_label.configure(image=playfield_image)
            self.playfield_image_label.image = playfield_image
        else:
            print("Failed to load images. Paths might be invalid.")

    def show_images(self, clear_logo_filepath, playfield_filepath):
        max_width = 300  # Define your maximum width here
        max_height = 400  # Define your maximum height here

        clear_logo_image = self.load_image(clear_logo_filepath, max_width, max_height)
        playfield_image = self.load_image(playfield_filepath, max_width, max_height)

        # Display the clear logo and playfield images in the Label widgets
        self.clear_logo_image_label.configure(image=clear_logo_image)
        self.clear_logo_image_label.image = clear_logo_image

        self.playfield_image_label.configure(image=playfield_image)
        self.playfield_image_label.image = playfield_image            

    def load_image(self, path, max_width=100, max_height=100):
        if path:
            image = Image.open(path)
            # Get the original dimensions
            width, height = image.size
            
            # Calculate the aspect ratio
            aspect_ratio = width / height
            
            # Resize based on the maximum width or height, preserving aspect ratio
            if width > max_width or height > max_height:
                if width > height:
                    new_width = max_width
                    new_height = int(new_width / aspect_ratio)
                else:
                    new_height = max_height
                    new_width = int(new_height * aspect_ratio)

                # Resize the image using thumbnail method
                image.thumbnail((new_width, new_height))
            
            image = ImageTk.PhotoImage(image)
            return image
        return None


    # show popup window
    def create_new_platform(self):
        self.new_platform_window = tk.Toplevel(self.root)
        self.new_platform_window.title("Create New Platform")

        directory_frame = tk.Frame(self.new_platform_window)
        directory_frame.pack(padx=10, pady=10, anchor=tk.W)

        self.new_dir_entries = {}
        for dir_name, default_path in self.dir_entries.items():
            entry_frame = tk.Frame(directory_frame)
            entry_frame.pack(anchor=tk.W, padx=5, pady=5)

            label = tk.Label(entry_frame, text=dir_name)
            label.pack(side=tk.LEFT)

            entry = tk.Entry(entry_frame, width=40)
            # entry.insert(0, default_path)
            entry.pack(side=tk.LEFT, padx=5)

            def browse_and_update(path_var):
                def inner():
                    directory = filedialog.askdirectory()
                    if directory:
                        path_var.delete(0, tk.END)
                        path_var.insert(0, directory)
                        self.new_platform_window.lift()  # Ensure popup remains on top

                return inner

            button = tk.Button(entry_frame, text="Browse", command=browse_and_update(entry))
            button.pack(side=tk.LEFT, padx=5)

            self.new_dir_entries[dir_name] = entry

        save_button = tk.Button(self.new_platform_window, text="Save", command=self.save_directories)
        save_button.pack(padx=10, pady=10)

    def save_directories(self):
        new_data = {
            'platform_name': self.new_dir_entries['Platform Name'].get(),
            'rom_dir': self.new_dir_entries['Rom Dir'].get(),
            'clear_logo_dir': self.new_dir_entries['Clear Logo Dir'].get(),
            'playfield_dir': self.new_dir_entries['Playfield Dir'].get()
        }

        try:
            with open('config.yaml', 'r') as file:
                existing_data = yaml.safe_load(file)
                if existing_data is None:
                    existing_data = {'platforms': []}
        except FileNotFoundError:
            existing_data = {'platforms': []}

        existing_data['platforms'].append(new_data)

        with open('config.yaml', 'w') as file:
            yaml.dump(existing_data, file)

        self.new_platform_window.destroy()
        self.populate_platform_table()  # Update the platform list in the UI     

    def save_platform(self):
        # Get directory paths and platform name
        platform_name = self.platform_name_entry.get()
        rom_dir = self.rom_dir_entry.get()
        clear_logo_dir = self.clear_logo_dir_entry.get()
        playfield_dir = self.playfield_dir_entry.get()

        # Validate if the paths are not empty
        if platform_name and rom_dir and clear_logo_dir and playfield_dir:
            # Create a dictionary for the new platform
            platform = {
                "name": platform_name,
                "rom_dir": rom_dir,
                "clear_logo_dir": clear_logo_dir,
                "playfield_dir": playfield_dir
            }

            # Append the new platform to the list
            self.platforms.append(platform)

            # Show a message that the platform is saved
            messagebox.showinfo("Success", f"Platform '{platform_name}' has been saved!")

            # You can save this list of platforms to a YAML file here
            # ...

            # Destroy the popup window after saving
            self.new_platform_window.destroy()
        else:
            messagebox.showwarning("Incomplete Information", "Please fill in all fields!")



    def setup_platform_table(self):
        platform_frame = tk.Frame(self.left_frame)
        platform_frame.pack()

        self.platform_tree = ttk.Treeview(platform_frame, columns=('Platform Name'))
        self.platform_tree.heading("#0", text='Platform Name')

        self.platform_tree.pack()

        self.populate_platform_table()

        # Bind the selection of the platform table to a function
        self.platform_tree.bind("<<TreeviewSelect>>", self.on_platform_table_select)


    def populate_platform_table(self):
        self.platform_tree.delete(*self.platform_tree.get_children())  # Clear existing items

        try:
            with open('config.yaml', 'r') as file:
                data = yaml.safe_load(file)
                if data and 'platforms' in data:
                    platforms = data['platforms']
                    for platform in platforms:
                        platform_name = platform.get('platform_name', 'Unknown Platform')
                        self.platform_tree.insert("", "end", text=platform_name)
        except FileNotFoundError:
            print("Config file not found.")

    def on_platform_table_select(self, event):
        # Retrieve the selected item from the platform table
        selected_item = self.platform_tree.selection()
        if selected_item:
            # Get the platform name
            platform_name = self.platform_tree.item(selected_item, "text")

            # Read config.yaml to get the selected platform's info
            with open('config.yaml', 'r') as file:
                data = yaml.safe_load(file)
                platforms = data.get('platforms', [])
                for platform in platforms:
                    if platform.get('platform_name', '') == platform_name:
                        self.enable_editing_for_directory_entries()
                        # Update the text fields in the left frame
                        self.dir_entries['Platform Name'].delete(0, tk.END)
                        self.dir_entries['Platform Name'].insert(0, platform.get('platform_name', ''))

                        self.dir_entries['Rom Dir'].delete(0, tk.END)
                        self.dir_entries['Rom Dir'].insert(0, platform.get('rom_dir', ''))

                        self.dir_entries['Clear Logo Dir'].delete(0, tk.END)
                        self.dir_entries['Clear Logo Dir'].insert(0, platform.get('clear_logo_dir', ''))

                        self.dir_entries['Playfield Dir'].delete(0, tk.END)
                        self.dir_entries['Playfield Dir'].insert(0, platform.get('playfield_dir', ''))
                        self.disable_editing_for_directory_entries()

    def enable_editing_for_directory_entries(self):
        for entry in self.dir_entries.values():
            entry.config(state='normal')  # Enable editing by setting state to 'normal'

    def disable_editing_for_directory_entries(self):
        for entry in self.dir_entries.values():
            entry.config(state='readonly')  # Disable editing by setting state to 'readonly'



def main():
    root = tk.Tk()
    app = GameMediaAuditApp(root)

    # Set the window state to maximize
    root.state('zoomed')    
    
    root.mainloop()

if __name__ == "__main__":
    main()
