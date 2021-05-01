# To view directory structures with forward slashes
from pathlib import PurePosixPath 

from utility import *
import re
import pandas as pd
import emoji
from collections import Counter





# Unique messages are identified if starts with DateTime stamp
def startswith_datetime(line):
    """ Returns True if starts with Date Time stamp, else False"""
    # This regex pattern for date Time works for android. 
    # IOS whatsapp chat format is different
    pattern = '^[0-3][\d]/[0-1][\d]/[\d]{4}, [\d]{1,2}:[\d]{1,2} [aApP][mM] -'
    match = re.match(pattern, line)
    return True if match else False

# {DateTime stamp} - {user_message}
# {DateTime stamp} - {{author}: {message}}
def find_author(user_message):
    """ Returns author(username) of the message. 
    
    Returns None if username not detected.
    """

    # username formats
    patterns = [
        '([\w]+):',                     # First_name (1+ alphanumeric characters)
        '([\w]+)[\s]+([\w]+):',         # fname lname
        '([\w]+[\s]+[\w]+[\s]+[\w]+):', # fname Mname lname
        '([+]\d{2} \d{5} \d{5}):',      # mobile number (India)
        '([\w]+)[\u263a-\U0001f999]+:', # name and emoji        
    ]

    pattern = '^' + '|'.join(patterns)
    match = re.match(pattern, user_message)
    
    if match:
        author = user_message.split(': ')[0]
    else:   
        author = None

    return author


def get_data_tokens(unique_message):
    """ Returns data tokens date,time,author,message from a message_line.

    message line is identified as the line starting with date_time stamp. 
    WhatsApp generated messages also have date_time stamps.
    WhatsApp generated messages' author will be set to 'None' 
    """

    # https://docs.python.org/3/library/stdtypes.html#str.split
    
    # user conversation might also include ' - '
    date_time_stamp, message = unique_message.split(' - ', maxsplit=1)   
    date, time = date_time_stamp.split(', ')
    author = find_author(message)
    if author:
        message = message.split(': ', maxsplit=1)[1]

    return date, time, author, message

def drop_sys_msg(dataframe, column='Author'):
    """ Drops all rows with null objects from the passed column in dataframe received """

    print(f"<{df[column].isnull().sum()} system-generated-messages detected> dropping off...")

    df.dropna(inplace=True) 
    # print(df.head(10)) # drop verification


def url_counter(message):
    """ Returns the total number of urls detected in the message """
    URLPATTERN = r'(https?://\S+)'
    urls_count= len(re.findall(URLPATTERN, message))
    return urls_count

def extract_emojis(message,regex_set):
    """ Returns the list of emojis found in the text message line """
    # https://blog.finxter.com/how-to-extract-all-emojis-from-text-in-python/
    msg = [message]
    emojis_list = regex_set.findall(msg[0])
    return emojis_list






if __name__=='__main__':
    # Create an iterable object.
    emojis_iter = map(lambda y: y, emoji.UNICODE_EMOJI['en'].keys())
    # Use the iterable object to compile a regular expression set of all emojis within
    # the ‘en’ dictionary subset
    regex_set = re.compile('|'.join(re.escape(em) for em in emojis_iter))
    # Use the compiled regular expression set to find and extract all emojis in
    # orig_list

    chat_file = select_chat() 
    chat_preview(chat_file,lines=5)

    # Parse Chat Data
    parsedData = []     # track data to feed dataframe

    with open(chat_file, mode='r', encoding='utf8') as chat:
        message_buffer = []
        date, time, author = None, None, None

        while True:
            line = chat.readline() # '\n' is also parsed.
            if line: 
                line = line.strip() # Gets rid of both leading and trailing spaces if any
                if startswith_datetime(line):
                    if len(message_buffer) > 0: # adds previous msg_tokens to parsedData
                        parsedData.append([date,time,author,' '.join(message_buffer)])
                    message_buffer.clear() # initialise for message in this iteration
                    date, time, author, message = get_data_tokens(unique_message=line)
                    message_buffer.append(message)
                    # adds to parsedData only when it confirms that next line is unique message
                    # else keeps in buffer
                else:
                    message_buffer.append(line)
            else: # No line imply end of file
                # adds previous msg_tokens to parsedData (last message)
                if len(message_buffer) > 0: 
                    parsedData.append([date,time,author,' '.join(message_buffer)])
                break
    
    # initialise pandas DataFrame 
    df = pd.DataFrame(parsedData, columns=['Date','Time','Author','Message'])
    df['Date'] = pd.to_datetime(df['Date'])

    drop_sys_msg(df)

    total_messages = df.shape[0]
    media_messages = df[df['Message'] == '<Media omitted>'].shape[0]

    df['urlcount'] = df.Message.apply(url_counter)
    total_links = df.urlcount.sum()

    df['emoji'] = df.Message.apply(extract_emojis, args=(regex_set,))
    total_emojis = df.emoji.apply(lambda c:len(c)).sum()

    # original df remains unaffected. Operations are not inplace.
    media_messages_df = df[df['Message'] == "<Media omitted>"]
    messages_df = df.drop(media_messages_df.index)

    # Letters and Word count for each message
    messages_df['Letter_count'] = messages_df['Message'].apply(lambda s: len(s))
    messages_df['Word_count'] = messages_df['Message'].apply(lambda s: len(s.split(' ')))
    # explicit is better than implicit


    emojis_list = [a for b in messages_df.emoji for a in b]
    emoji_freq = Counter(emojis_list).most_common()
    
    emoji_df = pd.DataFrame(emoji_freq, columns=['emoji','count'])
    # emoji_df.index = emoji_df.index + 1 

    unique_emojis_set = set(emojis_list)
    total_unique_emojis = len(unique_emojis_set)
    
    
    print(f"""--- Stats Overview ---
    Total Messages: [{total_messages}]
    Media Messages: [{media_messages}]
    Total Links: [{total_links}]
    Total emojis: [{total_emojis}] 
    Unique emojis: [{total_unique_emojis}]
    Most Used emojis -----
    {emoji_df.head(5)}
    """)

    




    # list out the unique authors in the chat
    participants = messages_df.Author.unique()


    for i in range(len(participants)):

        # filter msg of particular user
        profile_df = messages_df[messages_df['Author'] == participants[i]]

        print(f"""--- Stats of {participants[i]} ---
        Messages sent: {profile_df.shape[0]} 
        Words-per-msg: {(profile_df['Word_count'].sum())//(profile_df.shape[0])} (on average)
        Links shared: {profile_df['urlcount'].sum()}
        Media messages: {media_messages_df[media_messages_df['Author']==participants[i]].shape[0]}
        Emojis sent: {profile_df['emoji'].str.len().sum()}
        Unique emojis: {len(set([a for b in profile_df.emoji for a in b]))}
        """)
        

    

    
    
    

    
