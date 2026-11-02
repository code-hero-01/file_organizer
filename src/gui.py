import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from classifier import Classifier
from file_organizer import organize_files
from file_scanner import file_scanner
from models import Rule, Status, rules


# Application state
root = tk.Tk()
root.title("Smart File Organizer")
root.geometry("1000x720")
root.minsize(760, 560)

selected_directory = tk.StringVar()
files = []
results = {}                  # FileInfo -> ClassificationResult
user_choices = {}             # Path -> folder name, or None for "Don't move"
row_to_file = {}              # Main results Treeview row ID -> FileInfo


# Colours and small UI helpers
COLORS = {
    "header": "#C5E5F8",
    "panel": "#D9EAF6",
    "background": "#EAF2F8",
    "text": "#243B53",
    "muted": "#526D82",
    "entry": "#F8FCFF",
}


def make_button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        font=("Segoe UI", 10, "bold"),
        bg=COLORS["header"],
        fg=COLORS["text"],
        padx=13,
        pady=5,
        relief="raised",
        bd=2,
    )


def file_label(file):
    return file.path.name


def effective_choice(file): # Return the user's override, or the classifier's original suggestion
    if file.path in user_choices:
        return user_choices[file.path]
    return results[file].folder


def destination_label(file):
    return effective_choice(file) or "None"


def clear_classification():
    results.clear()
    user_choices.clear()
    row_to_file.clear()
    results_tree.delete(*results_tree.get_children())
    review_status.set("Classify the scanned files to see suggestions.")


def refresh_results():
    results_tree.delete(*results_tree.get_children())
    row_to_file.clear()

    for index, (file, result) in enumerate(results.items()):
        row_id = f"file_{index}"
        row_to_file[row_id] = file
        results_tree.insert(
            "",
            "end",
            iid=row_id,
            values=(
                file_label(file),
                destination_label(file),
                f"{result.confidence:.1f}%",
                result.status.name,
            ),
        )

    ambiguous_count = sum(
        result.status == Status.AMBIGUOUS for result in results.values()
    )
    review_status.set(
        f"{len(results)} files classified  |  "
        f"{ambiguous_count} ambiguous (left at None = not moved)"
    )


def current_folder_options():
    # Rebuilt whenever a dropdown is opened, so newly added rules appear.
    return ["None"] + [rule.folder_name for rule in rules]


def edit_tree_cell(tree, row_id, column, file, on_change): # Place a read-only Combobox over a Treeview cell
    bounds = tree.bbox(row_id, column)
    if not bounds:
        return

    x, y, width, height = bounds
    values = list(tree.item(row_id, "values"))
    column_index = int(column[1:]) - 1
    current_value = values[column_index] or "None"

    combo = ttk.Combobox(
        tree,
        values=current_folder_options(),
        state="readonly",
    )
    combo.set(current_value)
    combo.place(x=x, y=y, width=width, height=height)
    combo.focus_set()

    saved = False

    def save_choice(event=None):
        nonlocal saved
        if saved:
            return
        saved = True

        selected = combo.get()
        new_choice = None if selected == "None" else selected
        values[column_index] = selected
        tree.item(row_id, values=values)
        combo.destroy()
        on_change(file, new_choice)

    def close_editor(event=None):
        if combo.winfo_exists():
            combo.destroy()

    combo.bind("<<ComboboxSelected>>", save_choice)
    combo.bind("<Return>", save_choice)
    combo.bind("<Escape>", close_editor)
    combo.bind("<FocusOut>", close_editor)


# Menu bar
menubar = tk.Menu(root)

file_menu = tk.Menu(menubar, tearoff=0)
view_menu = tk.Menu(menubar, tearoff=0)
help_menu = tk.Menu(menubar, tearoff=0)


def browse_directory():
    directory = filedialog.askdirectory(
        title="Select a Folder",
        mustexist=True,
    )
    if directory:
        selected_directory.set(directory)
        scan_directory()


file_menu.add_command(label="Open...", command=browse_directory)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.destroy)

# Theme switching is intentionally left as a placeholder for a later polish pass.
view_menu.add_command(
    label="Light Mode",
    command=lambda: messagebox.showinfo("Appearance", "Light mode is already active."),
)
view_menu.add_command(
    label="Dark Mode",
    command=lambda: messagebox.showinfo("Appearance", "Dark mode is not implemented yet."),
)

help_menu.add_command(
    label="About",
    command=lambda: messagebox.showinfo(
        "About Smart File Organizer",
        "Smart File Organizer\nVersion 1.0\n"
        "Github: https://github.com/code-hero-01/file_organizer/",
    ),
)

menubar.add_cascade(label="File", menu=file_menu)
menubar.add_cascade(label="View", menu=view_menu)
menubar.add_cascade(label="Help", menu=help_menu)
root.config(menu=menubar)


# Main window layout
root.configure(bg=COLORS["background"])
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)

header = tk.Frame(root, bg=COLORS["header"], height=75)
header.grid(row=0, column=0, sticky="ew")
header.grid_propagate(False)
header.columnconfigure(0, weight=1)

tk.Label(
    header,
    text="Smart File Organizer",
    font=("Segoe UI", 22),
    bg=COLORS["header"],
    fg=COLORS["text"],
).grid(row=0, column=0, sticky="w", padx=25)

main = tk.Frame(root, bg=COLORS["background"], padx=18, pady=14)
main.grid(row=1, column=0, sticky="nsew")
main.columnconfigure(0, weight=1)
main.rowconfigure(2, weight=1)


# Source directory panel
directory_frame = tk.Frame(
    main, bg=COLORS["panel"], padx=14, pady=10, relief="ridge", bd=1
)
directory_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
directory_frame.columnconfigure(0, weight=1)

tk.Label(
    directory_frame,
    text="SOURCE DIRECTORY",
    font=("Segoe UI", 10, "bold"),
    bg=COLORS["panel"],
    fg=COLORS["text"],
).grid(row=0, column=0, sticky="w")

directory_display = tk.Label(
    directory_frame,
    textvariable=selected_directory,
    font=("Segoe UI", 10),
    bg=COLORS["entry"],
    fg=COLORS["muted"],
    anchor="w",
    relief="sunken",
    bd=1,
    padx=8,
    pady=6,
)
directory_display.grid(row=1, column=0, sticky="ew")

make_button(directory_frame, "Select Directory", browse_directory).grid(
    row=1, column=1, padx=(8, 0), pady=(7, 0)
)


# Rules panel
rules_frame = tk.Frame(
    main, bg=COLORS["panel"], padx=14, pady=8, relief="ridge", bd=1
)
rules_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
rules_frame.columnconfigure(0, weight=1)

tk.Label(
    rules_frame,
    text="RULES",
    font=("Segoe UI", 10, "bold"),
    bg=COLORS["panel"],
    fg=COLORS["text"],
).grid(row=0, column=0, sticky="w")

rules_tree = ttk.Treeview(
    rules_frame,
    columns=("folder", "keywords", "extensions"),
    show="headings",
    selectmode="browse",
    height=4,
)
for column, heading, width in (
    ("folder", "Folder Name", 150),
    ("keywords", "Keywords", 420),
    ("extensions", "Extensions", 220),
):
    rules_tree.heading(column, text=heading, anchor="w")
    rules_tree.column(column, width=width, anchor="w")

rules_tree.grid(row=1, column=0, columnspan=3, sticky="ew", pady=6)


def refresh_rules():
    rules_tree.delete(*rules_tree.get_children())
    for index, rule in enumerate(rules):
        rules_tree.insert(
            "",
            "end",
            iid=f"rule_{index}",
            values=(
                rule.folder_name,
                ", ".join(rule.keywords),
                ", ".join(rule.extensions),
            ),
        )


def invalidate_classification():
    clear_classification()


def add_rule():
    dialog = tk.Toplevel(root)
    dialog.title("Add Classification Rule")
    dialog.geometry("420x300")
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()
    dialog.configure(bg=COLORS["background"])

    form = tk.Frame(dialog, bg=COLORS["panel"], padx=18, pady=15)
    form.pack(fill="both", expand=True, padx=14, pady=14)

    folder_var = tk.StringVar()
    keywords_var = tk.StringVar()
    extensions_var = tk.StringVar()

    for label_text, variable in (
        ("Folder Name", folder_var),
        ("Keywords (comma-separated)", keywords_var),
        ("Extensions (comma-separated)", extensions_var),
    ):
        tk.Label(form, text=label_text, bg=COLORS["panel"]).pack(anchor="w")
        tk.Entry(form, textvariable=variable).pack(fill="x", pady=(3, 10))

    def save_rule():
        folder = folder_var.get().strip()
        keywords = [
            item.strip().lower()
            for item in keywords_var.get().split(",")
            if item.strip()
        ]
        extensions = [
            item.strip().lower().lstrip(".")
            for item in extensions_var.get().split(",")
            if item.strip()
        ]

        if not folder:
            messagebox.showwarning(
                "Invalid Rule", "Please enter a folder name.", parent=dialog
            )
            return
        if not keywords and not extensions:
            messagebox.showwarning(
                "Invalid Rule",           
                "Enter at least one keyword or extension.",
                parent=dialog,
            )
            return
        if folder in {".", ".."} or any(char in folder for char in '/\\:'):
            messagebox.showwarning(
                "Invalid Folder Name",
                "Folder names cannot contain path separators or reserved names.",
                parent=dialog,
            )
            return
        if any(rule.folder_name.casefold() == folder.casefold() for rule in rules):
            messagebox.showwarning(
                "Duplicate Rule",
                "A rule with this folder name already exists.",
                parent=dialog,
            )
            return

        rules.append(Rule(folder, keywords, extensions))
        refresh_rules()
        invalidate_classification()
        dialog.destroy()

    buttons = tk.Frame(form, bg=COLORS["panel"])
    buttons.pack(fill="x", pady=(5, 0))
    tk.Button(buttons, text="Save Rule", command=save_rule).pack(side="left", padx=4)
    tk.Button(buttons, text="Cancel", command=dialog.destroy).pack(side="left", padx=4)


def delete_rule():
    selection = rules_tree.selection()
    if not selection:
        messagebox.showwarning("No Selection", "Select a rule to delete.")
        return

    index = int(selection[0].split("_")[1])
    del rules[index]
    refresh_rules()
    invalidate_classification()


make_button(rules_frame, "Add Rule", add_rule).grid(
    row=0, column=1, sticky="e", padx=4, pady=4
)
make_button(rules_frame, "Delete Rule", delete_rule).grid(
    row=0, column=2, sticky="e", padx=4, pady=4
)
refresh_rules()


# Results panel and scanning/classification
results_frame = tk.Frame(
    main, bg=COLORS["panel"], padx=14, pady=8, relief="ridge", bd=1
)
results_frame.grid(row=2, column=0, sticky="nsew")
results_frame.columnconfigure(0, weight=1)
results_frame.rowconfigure(1, weight=1)

tk.Label(
    results_frame,
    text="RESULTS",
    font=("Segoe UI", 10, "bold"),
    bg=COLORS["panel"],
    fg=COLORS["text"],
).grid(row=0, column=0, sticky="w")

review_status = tk.StringVar(value="Select a directory and scan its files.")
tk.Label(
    results_frame,
    textvariable=review_status,
    font=("Segoe UI", 9),
    bg=COLORS["panel"],
    fg=COLORS["muted"],
).grid(row=0, column=1, sticky="e", padx=8)

result_columns = ("file", "destination", "confidence", "status")
results_tree = ttk.Treeview(
    results_frame,
    columns=result_columns,
    show="headings",
    selectmode="browse",
    height=9,
)
for column, heading, width in (
    ("file", "File Name", 310),
    ("destination", "Destination Folder", 180),
    ("confidence", "Confidence", 110),
    ("status", "Status", 120),
):
    results_tree.heading(column, text=heading, anchor="w")
    results_tree.column(column, width=width, anchor="w")

results_tree.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=6)

scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=results_tree.yview)
scrollbar.grid(row=1, column=3, sticky="ns")
results_tree.configure(yscrollcommand=scrollbar.set)


def scan_directory():
    global files
    directory = selected_directory.get().strip()

    if not directory:
        messagebox.showwarning("No Directory Selected", "Select a directory first.")
        return

    try:
        files = file_scanner(directory)
    except (NotADirectoryError, PermissionError, OSError) as error:
        messagebox.showerror("Scan Failed", str(error))
        return

    clear_classification()
    results_tree.delete(*results_tree.get_children())

    for index, file in enumerate(files):
        results_tree.insert(
            "", "end", iid=f"file_{index}",
            values=(file.path.name, "", "", "Not classified"),
        )

    review_status.set(f"Found {len(files)} files.")


def classify_files():
    if not files:
        messagebox.showwarning("No Files", "Scan a directory before classifying.")
        return
    if not rules:
        messagebox.showwarning("No Rules", "Add at least one classification rule.")
        return

    classifier = Classifier(rules)
    results.clear()
    user_choices.clear()

    for file in files:
        results[file] = classifier.classify(file)

    refresh_results()


def on_main_tree_click(event):
    row_id = results_tree.identify_row(event.y)
    column = results_tree.identify_column(event.x)
    if not row_id or column != "#2":
        return

    file = row_to_file.get(row_id)
    if file is None:
        return

    edit_tree_cell(
        results_tree,
        row_id,
        column,
        file,
        lambda selected_file, choice: (
            user_choices.__setitem__(selected_file.path, choice),
            refresh_results(),
        ),
    )


results_tree.bind("<Button-1>", on_main_tree_click)

make_button(results_frame, "Scan Directory", scan_directory).grid(
    row=0, column=2, sticky="e", padx=4, pady=4
)
make_button(results_frame, "Classify", classify_files).grid(
    row=0, column=3, sticky="e", padx=4, pady=4
)


# Ambiguous-file review window
def open_review_window():
    ambiguous = [
        file for file, result in results.items()
        if result.status == Status.AMBIGUOUS
    ]

    if not results:
        messagebox.showinfo("Nothing to Review", "Classify the scanned files first.")
        return
    if not ambiguous:
        messagebox.showinfo("No Ambiguous Files", "There are no ambiguous files.")
        return

    dialog = tk.Toplevel(root)
    dialog.title("Review Ambiguous Files")
    dialog.geometry("760x420")
    dialog.minsize(600, 300)
    dialog.transient(root)
    dialog.configure(bg=COLORS["background"])
    dialog.columnconfigure(0, weight=1)
    dialog.rowconfigure(2, weight=1)

    tk.Label(
        dialog,
        text="AMBIGUOUS FILES",
        font=("Segoe UI", 12, "bold"),
        bg=COLORS["background"],
        fg=COLORS["text"],
    ).grid(row=0, column=0, sticky="w", padx=15, pady=(12, 2))

    tk.Label(
        dialog,
        text="Choose a destination from the dropdown, or leave it as None to keep the file in place.",
        font=("Segoe UI", 9),
        bg=COLORS["background"],
        fg=COLORS["muted"],
    ).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 4))

    review_tree = ttk.Treeview(
        dialog,
        columns=("file", "alternatives", "destination"),
        show="headings",
        selectmode="browse",
    )
    review_tree.heading("file", text="File Name", anchor="w")
    review_tree.heading("alternatives", text="Suggested Alternatives", anchor="w")
    review_tree.heading("destination", text="Destination", anchor="w")
    review_tree.column("file", width=250, anchor="w")
    review_tree.column("alternatives", width=250, anchor="w")
    review_tree.column("destination", width=150, anchor="w")
    review_tree.grid(row=2, column=0, sticky="nsew", padx=14, pady=8)

    review_scroll = ttk.Scrollbar(
        dialog, orient="vertical", command=review_tree.yview
    )
    review_scroll.grid(row=2, column=1, sticky="ns", pady=8)
    review_tree.configure(yscrollcommand=review_scroll.set)

    review_row_to_file = {}

    def refresh_review_tree():
        review_tree.delete(*review_tree.get_children())
        review_row_to_file.clear()

        for index, file in enumerate(ambiguous):
            row_id = f"amb_{index}"
            review_row_to_file[row_id] = file
            alternatives = ", ".join(results[file].alternatives[:2]) or "None"
            review_tree.insert(
                "",
                "end",
                iid=row_id,
                values=(file.path.name, alternatives, destination_label(file)),
            )

    def on_review_tree_click(event):
        row_id = review_tree.identify_row(event.y)
        column = review_tree.identify_column(event.x)
        if not row_id or column != "#3":
            return

        file = review_row_to_file.get(row_id)
        if file is None:
            return

        def save_review_choice(selected_file, choice):
            user_choices[selected_file.path] = choice
            refresh_results()
            refresh_review_tree()

        edit_tree_cell(
            review_tree, row_id, column, file, save_review_choice
        )

    review_tree.bind("<Button-1>", on_review_tree_click)

    tk.Button(
        dialog,
        text="Done",
        command=dialog.destroy,
        font=("Segoe UI", 10, "bold"),
        bg=COLORS["header"],
        fg=COLORS["text"],
        padx=14,
        pady=4,
    ).grid(row=3, column=0, sticky="e", padx=14, pady=10)

    refresh_review_tree()


# Build and execute the final move plan
def build_plan():
    plan = {}
    for file, result in results.items():
        folder = effective_choice(file)
        destination = Path(selected_directory.get()) / folder if folder else None
        plan[file.path] = destination
    return plan


def organize():
    if not results:
        messagebox.showwarning("No Results", "Scan and classify files first.")
        return

    plan = build_plan()
    moving = [(source, destination) for source, destination in plan.items()
              if destination is not None and source.parent != destination]
    staying = len(plan) - len(moving)

    if not moving:
        messagebox.showinfo(
            "Nothing to Organize",
            f"No files have a destination folder. {staying} file(s) will remain in place.",
        )
        return

    preview_lines = [
        f"{source.name}  ->  {destination.name}"
        for source, destination in moving[:12]
    ]
    if len(moving) > 12:
        preview_lines.append(f"... and {len(moving) - 12} more file(s)")

    preview = (
        f"Files to move: {len(moving)}\n"
        f"Files to leave in place: {staying}\n\n"
        + "\n".join(preview_lines)
        + "\n\nProceed?"
    )

    if not messagebox.askyesno("Confirm Organization", preview):
        return

    report = organize_files(plan)
    moved_count = len(report["moved"])
    skipped_count = len(report["skipped"])
    error_count = len(report["errors"])

    summary = (
        f"Moved: {moved_count}\n"
        f"Left in place: {skipped_count}\n"
        f"Errors: {error_count}"
    )

    if report["errors"]:
        details = "\n".join(
            f"{source.name}: {error}"
            for source, error in report["errors"][:5]
        )
        summary += "\n\nSome files could not be moved:\n" + details

    if error_count:
        messagebox.showwarning("Organization Finished with Errors", summary)
    else:
        messagebox.showinfo("Organization Complete", summary)

    # Refresh the directory listing after successful/partial movement.
    scan_directory()


make_button(main, "Review Ambiguous", open_review_window).grid(
    row=3, column=0, sticky="w", padx=2, pady=(8, 0)
)
make_button(main, "Organize Files", organize).grid(
    row=3, column=0, sticky="e", padx=2, pady=(8, 0)
)


if __name__ == "__main__":
    root.mainloop()
