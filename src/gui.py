import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from pathlib import Path
from file_scanner import file_scanner
from models import Rule, rules
from classifier import Classifier
from file_organizer import organize_files

# main application window.
root = tk.Tk()

root.title("Smart File Organizer")
root.geometry("800x650")
root.minsize(500, 500)

root.columnconfigure(0, weight= 1)
root.rowconfigure(0, weight=0)
root.rowconfigure(1, weight=1)

# primary menu bar container
menubar = tk.Menu(root)

selected_directory = tk.StringVar()
def browse_directory():
    directory = filedialog.askdirectory(
        title="Select a Folder",
        mustexist=True
    )   

    if directory:
        selected_directory.set(directory)
        print(f"Selected folder: {directory}")
    else:
        print("User cancelled the dialog.")

# file dropdown menu
# tearoff=0 prevents the user from detaching the menu into a separate window
file_menu = tk.Menu(menubar, tearoff=0)
file_menu.add_command(label="Open...", command= browse_directory)
# file_menu.add_separator()  # visual dividing line
file_menu.add_command(label="Exit", command=lambda: root.destroy())

view_menu = tk.Menu(menubar, tearoff=0)
view_menu.add_command(label="Light Mode", command=lambda: print("Light mode"))
# view_menu.add_separator()  
view_menu.add_command(label="Dark Mode", command=lambda: print("Dark mode"))

# help dropdown menu
help_menu = tk.Menu(menubar, tearoff=0)
help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Version 1.0\nGithub: https://github.com/code-hero-01/file_organizer/"))

menubar.add_cascade(label="File", menu=file_menu)
menubar.add_cascade(label="View", menu=view_menu)
menubar.add_cascade(label="Help", menu=help_menu)

# configure the window to display the Menu Bar
root.config(menu=menubar)

# header panel
header_panel = tk.Frame(root, bg="#C5E5F8", height=75)
header_panel.grid(row= 0, column= 0, sticky="ew")
header_panel.grid_propagate(False) # Keeps the frame exactly 100px tall

header_panel.columnconfigure(0, weight=1) 
header_panel.rowconfigure(0, weight=1) 

# application title.
title_label = tk.Label(
    header_panel, 
    text="Smart File Organizer", 
    font=("Segoe UI", 22), 
    bg="#C5E5F8", 
    fg="#243B53"
)
title_label.grid(row=0, column=0, sticky="w", padx=25)

# Main content container
main_frame = tk.Frame(
    root,
    bg="#EAF2F8",
    padx=20,
    pady=15
)

main_frame.grid(
    row=1,
    column=0,
    sticky="nsew"
)

main_frame.columnconfigure(0, weight=1)
main_frame.rowconfigure(2, weight=1)

# Directory selection panel
directory_frame = tk.Frame(
    main_frame,
    bg="#D9EAF6",
    padx=15,
    pady=5,
    relief="ridge",
    bd=1
)

directory_frame.grid(
    row=0,
    column=0,
    sticky="ew"
)

directory_frame.columnconfigure(0, weight=1)

# Panel heading
directory_heading = tk.Label(
    directory_frame,
    text="SOURCE DIRECTORY",
    font=("Segoe UI", 10, "bold"),
    bg="#D9EAF6",
    fg="#243B53"
)

directory_heading.grid(
    row=0,
    column=0,
    sticky="w"
)

# Display selected directory
directory_display = tk.Label(
    directory_frame,
    textvariable=selected_directory,
    font=("Segoe UI", 10),
    bg="#F8FCFF",
    fg="#526D82",
    anchor="w",
    relief="sunken",
    bd=1,
    padx=8,
    pady=5
)

directory_display.grid(
    row=1,
    column=0,
    sticky="ew",
    pady=(8, 0)
)

scan_button = tk.Button(
    directory_frame,
    text="Select Directory",
    command=browse_directory,
    font=("Segoe UI", 10, "bold"),
    bg="#C5E5F8",
    fg="#243B53",
    padx=15,
    pady=5,
    relief="raised",
    bd=2
)

scan_button.grid(
    row=1,
    column=1,
    sticky="w",
    padx=5,
    pady=5
)

# rules panel
rules_frame = tk.Frame(
    main_frame,
    bg="#D9EAF6",
    padx=15,
    pady=5,
    relief="ridge",
    bd=1
)

rules_frame.grid(
    row=1,
    column=0,
    sticky="ew"
)

rules_frame.columnconfigure(0, weight=1)


# Panel heading
rules_heading = tk.Label(
    rules_frame,
    text="RULES",
    font=("Segoe UI", 10, "bold"),
    bg="#D9EAF6",
    fg="#243B53"
)

rules_heading.grid(
    row=0,
    column=0,
    sticky="w"
)

rule_columns = ("folder", "keywords", "extensions")

rules_tree = ttk.Treeview(
    rules_frame,
    columns=rule_columns,
    show="headings",
    selectmode="browse",
    height=4
)

rules_tree.heading("folder", text="Folder Name", anchor='w')
rules_tree.heading("keywords", text="Keywords", anchor='w')
rules_tree.heading("extensions", text="Extensions", anchor='w')

rules_tree.column("folder", width=150, anchor="w")
rules_tree.column("keywords", width=400, anchor="w")
rules_tree.column("extensions", width=200, anchor="w")

rules_tree.grid(
    row=1,
    column=0,
    columnspan=3,
    sticky="ew",
    pady=5
)

def refresh_rules():
    rules_tree.delete(*rules_tree.get_children())

    for rule in rules:
        rules_tree.insert(
            "",
            "end",
            values=(
                rule.folder_name,
                ", ".join(rule.keywords),
                ", ".join(rule.extensions)
            )
        )

refresh_rules()

def add_rule():
    dialog = tk.Toplevel(root)
    dialog.title("Add Classification Rule")
    dialog.geometry("400x300")
    dialog.resizable(False, False)

    dialog.transient(root)
    dialog.grab_set()

    dialog.configure(bg="#EAF2F8")

    # Input variables
    folder_var = tk.StringVar()
    keywords_var = tk.StringVar()
    extensions_var = tk.StringVar()

    form = tk.Frame(dialog, bg="#D9EAF6", padx=20, pady=15)
    form.pack(fill="both", expand=True, padx=15, pady=15)

    tk.Label(
        form,
        text="Folder Name",
        bg="#D9EAF6"
    ).pack(anchor="w")

    tk.Entry(
        form,
        textvariable=folder_var
    ).pack(fill="x", pady=(3, 10))

    tk.Label(
        form,
        text="Keywords (comma-separated)",
        bg="#D9EAF6"
    ).pack(anchor="w")

    tk.Entry(
        form,
        textvariable=keywords_var
    ).pack(fill="x", pady=(3, 10))

    tk.Label(
        form,
        text="Extensions (comma-separated)",
        bg="#D9EAF6"
    ).pack(anchor="w")

    tk.Entry(
        form,
        textvariable=extensions_var
    ).pack(fill="x", pady=(3, 10))

    def save_rule():
        folder = folder_var.get().strip()

        keywords = [
            keyword.strip().lower()
            for keyword in keywords_var.get().split(',')
            if keyword.strip()
        ]

        extensions = [
            extension.strip().lower().lstrip('.')
            for extension in extensions_var.get().split(',')
            if extension.strip()
        ]

        if not folder:
            messagebox.showwarning(
                "Invalid Rule",
                "Please enter a folder name.",
                parent=dialog
            )
            return

        if not keywords and not extensions:
            messagebox.showwarning(
                "Invalid Rule",
                "Enter at least one keyword or extension.",
                parent=dialog
            )
            return

        if any(rule.folder_name.lower() == folder.lower() for rule in rules):
            messagebox.showwarning(
                "Duplicate Rule",
                "A rule with this folder name already exists.",
                parent=dialog
            )
            return

        rules.append(Rule(folder, keywords, extensions))

        refresh_rules()
        clear_results()

        dialog.destroy()

    button_frame = tk.Frame(form, bg="#D9EAF6")
    button_frame.pack(fill="x", pady=(10, 0))

    tk.Button(
        button_frame,
        text="Save Rule",
        command=save_rule
    ).pack(side="left", padx=5)

    tk.Button(
        button_frame,
        text="Cancel",
        command=dialog.destroy
    ).pack(side="left", padx=5)

add_rule_button = tk.Button(
    rules_frame,
    text="Add Rule",
    command=add_rule,
    font=("Segoe UI", 10, "bold"),
    bg="#C5E5F8",
    fg="#243B53",
    padx=15,
    pady=5,
    relief="raised",
    bd=2
)

add_rule_button.grid(
    row=0,
    column=1,
    sticky="e",
    padx=5,
    pady=5
)

def delete_rule():
    selection = rules_tree.selection()

    if not selection:
        messagebox.showwarning(
            "No Selection",
            "Please select a rule to delete."
        )
        return
    
    index = rules_tree.index(selection[0])
    del rules[index]

    refresh_rules()
    clear_results()


delete_rule_button = tk.Button(
    rules_frame,
    text="Delete Rule",
    command=delete_rule,
    font=("Segoe UI", 10, "bold"),
    bg="#C5E5F8",
    fg="#243B53",
    padx=15,
    pady=5,
    relief="raised",
    bd=2
)

delete_rule_button.grid(
    row=0,
    column=2,
    sticky="e",
    padx=5,
    pady=5
)

# results panel
results_frame = tk.Frame(
    main_frame,
    bg="#D9EAF6",
    padx=15,
    pady=5,
    relief="ridge",
    bd=1
)

results_frame.grid(
    row=2,
    column=0,
    sticky="nsew"
)

results_frame.columnconfigure(0, weight=1)
results_frame.rowconfigure(1, weight=1)

results_heading = tk.Label(
    results_frame,
    text="RESULTS",
    font=("Segoe UI", 10, "bold"),
    bg="#D9EAF6",
    fg="#243B53"
)

results_heading.grid(
    row=0,
    column=0,
    sticky="w"
)

result_columns = ("file", "suggested folder", "confidence", "status")

results_tree = ttk.Treeview(
    results_frame,
    columns=result_columns,
    show="headings",
    selectmode="browse",
    height=6
)

results_tree.heading("file", text="File Name", anchor='w')
results_tree.heading("suggested folder", text="Suggested Folder", anchor='w')
results_tree.heading("confidence", text="Confidence", anchor='w')
results_tree.heading("status", text="Status", anchor='w')

results_tree.column("file", width=200, anchor="w")
results_tree.column("suggested folder", width=150, anchor="w")
results_tree.column("confidence", width=100, anchor="w")
results_tree.column("status", width=100, anchor="w")

results_tree.grid(
    row=1,
    column=0,
    columnspan=3,
    sticky="nsew",
    pady=5
)

def clear_results():
    results_tree.delete(*results_tree.get_children())

files = []
def scan_directory():
    global files
    directory = selected_directory.get()

    if not directory:
        messagebox.showwarning(
            "No Directory Selected",
            "Please select a directory first."
        )
        return

    if not Path(directory).is_dir():
        messagebox.showerror(
            "Invalid Directory",
            "The selected directory does not exist."
        )
        return

    files = file_scanner(directory)

    if files is None:
        messagebox.showerror(
            "Scan Failed",
            "Unable to scan the selected directory."
        )
        return

    messagebox.showinfo(
        "Scan Complete",
        f"Found {len(files)} files."
    )

    clear_results()
    
    for file in files:
        results_tree.insert(
            "",
            "end",
            values=(
                file.filename + '.' + file.extension,
                '',
                '',
                ''
            )
        )

scan_button = tk.Button(
    results_frame,
    text="Scan Directory",
    command=scan_directory,
    font=("Segoe UI", 10, "bold"),
    bg="#C5E5F8",
    fg="#243B53",
    padx=15,
    pady=5,
    relief="raised",
    bd=2
)

scan_button.grid(
    row=0,
    column=1,
    sticky="w",
    padx=5,
    pady=5
)

results = {}
plan = {}
ambiguous_files = []
def classify():
    if not files:
        messagebox.showwarning(
            "No files available",
            "Please scan files first."
        )
        return

    classifier = Classifier(rules)
    
    for file in files:
        res = classifier.classify(file)
        results[file] = res

    if not results:
        messagebox.showwarning(
            "Nothing happened!",
            "Nothing happened!"
        )
        return
    
    results_tree.delete(*results_tree.get_children())
        
    for file, res in results.items():
        results_tree.insert(
            "",
            "end",
            values=(
                file.path.name,
                res.folder,
                f"{res.confidence:.1f}%",
                res.status.name
            )
        )

        source_file = file.path
        if res.folder:
            dest_dir = Path(selected_directory.get()) / res.folder
        else:   
            dest_dir = Path(selected_directory.get()) 

        plan[source_file] = dest_dir

    global ambiguous_files
    ambiguous_files = [
        file for file, res in results.items()
        if res.status.name == "AMBIGUOUS"
    ]

classify_button = tk.Button(
    results_frame,
    text="Classify",
    command=classify,
    font=("Segoe UI", 10, "bold"),
    bg="#C5E5F8",
    fg="#243B53",
    padx=15,
    pady=5,
    relief="raised",
    bd=2
)

classify_button.grid(
    row=0,
    column=2,
    sticky="w",
    padx=5,
    pady=5
)

def on_tree_click(event):
    tree = event.widget
    # Identify region and row/column clicked
    region = tree.identify_region(event.x, event.y)
    if region != "cell":
        return
    
    column = tree.identify_column(event.x) # e.g., "#2"
    row_id = tree.identify_row(event.y)     # e.g., "I001"
    
    # Check if user clicked on the "suggested folder" column (#2)
    if column == "#2":
        edit_cell(tree, row_id, column)

AVAILABLE_FOLDERS = [rule.folder_name for rule in rules]
AVAILABLE_FOLDERS.append(None)
def edit_cell(tree, row_id, column):
    # Get the bounding box of the cell
    x, y, width, height = tree.bbox(row_id, column)
    
    # Get current value of the cell
    current_values = tree.item(row_id, "values")
    col_index = int(column.replace("#", "")) - 1
    current_val = current_values[col_index]

    # Create a Combobox widget over the cell
    combo = ttk.Combobox(tree, values=AVAILABLE_FOLDERS, state="readonly")
    combo.set(current_val)
    combo.place(x=x, y=y, width=width, height=height)
    combo.focus()

    # Save changes when an option is selected or focus is lost
    def save_value(event=None):
        new_val = combo.get()
        # Update treeview values tuple
        val_list = list(tree.item(row_id, "values"))
        val_list[col_index] = new_val
        tree.item(row_id, values=val_list)

        source_file = Path(selected_directory.get()) / val_list[0]

        if new_val:
            dest_dir = Path(selected_directory.get()) / new_val
        else:   
            dest_dir = Path(selected_directory.get())

        plan[source_file] = dest_dir
        
        # Destroy the combobox
        combo.destroy()
        
    combo.bind("<<ComboboxSelected>>", save_value)
    combo.bind("<FocusOut>", lambda e: combo.destroy())
    combo.bind("<Return>", save_value)

results_tree.bind("<Button-1>", on_tree_click)

reviewed = False
def review():
    if not ambiguous_files:
        messagebox.showinfo(
            "No Ambiguous Files",
            "There are no ambiguous files to review."
        )
        return

    dialog = tk.Toplevel(root)
    dialog.title("Review Ambiguous Files")
    dialog.geometry("650x400")
    dialog.transient(root)

    tk.Label(
        dialog,
        text="Ambiguous Files",
        font=("Segoe UI", 12, "bold")
    ).pack(anchor="w", padx=15, pady=10)

    ambiguous_tree = ttk.Treeview(
        dialog,
        columns=("filename", "alternatives", "review"),
        show="headings",
        selectmode="browse"
    )

    ambiguous_tree.heading("filename", text="File Name")
    ambiguous_tree.heading("alternatives", text="Suggested Alternatives")

    ambiguous_tree.column("filename", width=200)
    ambiguous_tree.column("alternatives", width=250)

    ambiguous_tree.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=10
    )

    def refresh_ambiguous():
        ambiguous_tree.delete(*ambiguous_tree.get_children())

        for file in ambiguous_files:
            ambiguous_tree.insert(
                "",
                "end",
                values=(
                    file.filename,
                    results[file].alternatives[0]
                )
            )

    refresh_ambiguous()
    ambiguous_tree.bind("<Button-1>", on_tree_click)

    def finish_review():
        dialog.destroy()
        global reviewed
        reviewed = True
    
    finish_btn = tk.Button(
            dialog,
            text="Done",
            command=finish_review
        ).pack(side="left", padx=5)


review_btn = tk.Button(
    main_frame,
    text="Review",
    command=review,
    font=("Segoe UI", 10, "bold"),
    bg="#C5E5F8",
    fg="#243B53",
    padx=15,
    pady=5,
    relief="raised",
    bd=2
)

review_btn.grid(
    row=3,
    column=0,
    sticky="w",
    padx=5,
    pady=5
)

def organize():
    if not reviewed:
        messagebox.showinfo(
                    "Unreviewed Ambiguous Files Remaining",
                    "Review ambiguous files first!"
                )
        return
    
    organize_files(plan)

organize_btn = tk.Button(
    main_frame,
    text="Organize",
    command=organize,
    font=("Segoe UI", 10, "bold"),
    bg="#C5E5F8",
    fg="#243B53",
    padx=15,
    pady=5,
    relief="raised",
    bd=2
)

organize_btn.grid(
    row=3,
    column=1,
    sticky="w",
    padx=5,
    pady=5
)

root.mainloop()