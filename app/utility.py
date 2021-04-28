import os

def select_chat(path='data'):
    """ Returns path for chat selected by user. 

    Lists all available chats available at given path.
    If no user chat detected, returns demo chat - sample.txt 
    """
    DEFAULT_CHAT = 'sample.txt'
    chat_list = {}

    with os.scandir(path) as entries:
        id = 1
        for entry in entries:
            if entry.is_file() and entry.name.endswith('.txt'):
                chat_list[id] = entry.name
                id += 1
        
    for id, chat in chat_list.items():
        print(f'[{id}] {chat} ')
    
    try:
        selected = int(input('select chat ID: '))
        if selected<1 or selected>id:
            raise Exception()
        else:
            path = os.path.join(path, chat_list[selected])
    except:
        print(f"Invalid choice. Fallback to default '{DEFAULT_CHAT}' ")
        path = os.path.join(path, DEFAULT_CHAT)
    
    return path


if __name__=='__main__':
    chat = select_chat()
    print('Selected chat location', chat)