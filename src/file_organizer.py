import shutil

def organize_files(plan : dict):
    for src_file, dest_dir in plan.items():
        print(f"{src_file} -> {dest_dir}")

    option = input("Press 1 to proceed, press anything else to quit\n")
    if option != '1':
        print("Nothing happened!")
        return
    
    for src_file, dest_dir in plan.items():
        dest_dir.mkdir(exist_ok = True)
        dest_file = dest_dir / src_file.name
        shutil.move(src_file, dest_file)

    print("Successfully organized files")