from models import Rule

def get_input() -> list[Rule]:
    rules = []

    while True:
        print('Press 1 to add a new folder')
        print('Press 2 to classify')

        rules.append(Rule('pics', ['photo', 'screenshot', 'pic', 'picture'], ['jpg', 'jpeg', 'png', 'webp']))
        rules.append(Rule('docs', ['document', 'doc'], ['pdf', 'docx', 'pptx', 'md', 'xlsx', 'py', 'cpp', 'c']))
        rules.append(Rule('college', ['document', 'doc', 'college', 'homework', 'assignment', 'assign', 'ass', '24106007'], ['pdf', 'docx', 'ppt', 'md']))
        rules.append(Rule('videos', ['movie', 'film', 'clip', 'season', 'episode'], ['mp4', 'mkv', 'webm', 'avi']))
        rules.append(Rule('audio', ['song', 'sound'], ['mp3', 'wav', 'flac', 'opus']))

        return rules

        print("Press 1 to enter a rule, press 2 to continue")
        option = int(input())
        match option:
            case 1:
                folder_name = input("Enter folder name: ")
                keywords = input("Enter keywords to match separated by spaces: ").split(' ')
                extensions = input("Enter names of extensions to match separated by spaces: ").split(' ')

                keywords = [keyword.lower() for keyword in keywords]
                extensions = [keyword.lower() for keyword in keywords]

                rule = Rule(folder_name, keywords, extensions)
                rules.append(rule)

            case 2:
                break

    return rules