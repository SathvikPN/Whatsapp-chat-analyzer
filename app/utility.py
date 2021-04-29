# from os import scandir

from pathlib import Path, PureWindowsPath, PurePosixPath
# The objects returned by Path are either PosixPath or WindowsPath objects 
# depending on the OS.

def select_chat(directory='data/'):
    """ Returns path for chat selected by user. 

    Lists all available chats available at given path.
    If no user chat detected, returns demo chat - sample.txt 
    """
    DEFAULT_CHAT = 'sample.txt'
    chat_list = {}

    with Path(directory) as dir_path:
    # The Path() object will convert forward slashes into the 
    # correct kind of slash for the current operating system.
        id = 0
        for entry in dir_path.iterdir():
            if entry.is_file() and entry.name.endswith('.txt'):
                id += 1
                chat_list[id] = entry.name
                
    for id, chat in chat_list.items():
        print(f'[{id}] {chat} ')
    
    try:
        selected = int(input('select chat ID: '))
        if selected<1 or selected>id:
            raise ValueError()
        else:
            chat_location = dir_path / chat_list[selected]
    except:
        print(f"Invalid choice. Fallback to default '{DEFAULT_CHAT}' ")
        chat_location = dir_path / DEFAULT_CHAT
    
    return chat_location

def chat_preview(chat, lines=3):
    """ Previews the beginning few lines of chat as specified """
    with open(chat, mode='r', encoding='utf8') as file:
        print(f"[Preview of beginning {lines} lines of chat]")
        for _ in range(lines):
            print(file.readline(),end='')
        print('\n[End of chat preview]')
                


if __name__=='__main__':
    chat = select_chat()
    print(f'Selected chat location: {PurePosixPath(chat)}')

    chat_preview(chat, lines=25)