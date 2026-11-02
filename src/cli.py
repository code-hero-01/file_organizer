# Optional command-line rule input; the Tkinter application does not use it

from models import Rule, create_default_rules

def get_input() -> list[Rule]:
    rules = create_default_rules()

    while True:
        print("\nCurrent rules:")
        for index, rule in enumerate(rules, start=1):
            print(f"{index}. {rule.folder_name}")

        print("\n1. Add rule")
        print("2. Finish")
        choice = input("Choose an option: ").strip()

        if choice == "2":
            return rules
        if choice != "1":
            print("Please enter 1 or 2.")
            continue

        folder = input("Folder name: ").strip()
        keywords = [
            item.strip().lower()
            for item in input("Keywords (comma-separated): ").split(",")
            if item.strip()
        ]
        extensions = [
            item.strip().lower().lstrip(".")
            for item in input("Extensions (comma-separated): ").split(",")
            if item.strip()
        ]

        if not folder or (not keywords and not extensions):
            print("A folder name and at least one keyword or extension are required.")
            continue
        if any(rule.folder_name.casefold() == folder.casefold() for rule in rules):
            print("That folder name already exists.")
            continue

        rules.append(Rule(folder, keywords, extensions))
