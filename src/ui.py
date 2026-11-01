from models import Rule, rules

def get_input():
    while True:
        print('Press 1 to add a new folder')
        print('Press 2 to classify')

        print("Press 1 to enter a rule, press 2 to continue")
        option = int(input())
        match option:
            case 1:
                folder_name = input("Enter folder name: ")
                keywords = input("Enter keywords to match separated by spaces: ").split(' ')
                extensions = input("Enter names of extensions to match separated by spaces: ").split(' ')

                keywords = [keyword.lower() for keyword in keywords]
                extensions = [extension.lower() for extension in extensions]

                rule = Rule(folder_name, keywords, extensions)
                rules.append(rule)

            case 2:
                break
