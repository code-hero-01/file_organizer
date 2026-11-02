# Smart File Organizer

## Run:
    python main.py

## Requirements:
    Python 3.10 or newer
    Tkinter (normally included with the standard Python installation)

## Screenshot:
<img width="994" height="764" alt="image" src="https://github.com/user-attachments/assets/82adb8b7-b1af-4587-887d-93c0e1a7dd23" />


## How it works:
1. Select a source directory.
2. Scan the files in that directory (top-level files only).
3. Add or remove classification rules if needed.
4. Classify the scanned files.
5. Click the Destination Folder cell in the results table to override a suggestion.
6. Use Review Ambiguous to see only ambiguous files and optionally choose destinations.
7. Click Organize Files and confirm the preview.

A destination of "None" means that the file is left where it is. Ambiguous files
are not forced into a folder: if the user leaves the destination as None, they
are skipped. The organizer does not overwrite an existing destination file.

The confidence value is a relative score margin from the classifier, not a
statistically calibrated probability.
