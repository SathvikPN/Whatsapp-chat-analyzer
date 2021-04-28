# To view directory structures with forward slashes
from pathlib import PurePosixPath 

from utility import *




if __name__=='__main__':

    # Get selected chat
    chat = select_chat()
    print(f'Chat location: {PurePosixPath(chat)} ')
    
    chat_preview(chat,lines=5)