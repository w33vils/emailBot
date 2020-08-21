#!/usr/bin/env python3

from config import *
import imapclient
import time
import re
import telegram
import pyzmail


def imap():
    try:
        print("Initializing IMAP ... ", end="")
        global connect
        connect = imapclient.IMAPClient(imap_server)
        connect.login(read_from, password)
        connect.select_folder("INBOX", readonly=False)
        print("Success")
    except Exception as e:
        print(e)

def get_unread():
    uids=connect.search(['UNSEEN'])
    if not uids:
        return None
    else:
        print("Found %s unread emails" %len(uids))
        return connect.fetch(uids, ['BODY[]', 'FLAGS'])

def analyze_msg(raws, a):
    print("Analyzing message with uid" +str(a))
    msg=pyzmail.PyzMessage.factory(raws[a][b'BODY[]'])
    global subject
    subject=msg.get_subject()
    frm=msg.get_address('from')
    if frm[1] != sender_address:
        print("Unread is from %s <%s> skipping" %(frm[0][0], frm[0][1]))
        return None
    if msg.text_part is None:
        print("No text Parse, cannot parse")
        return None
    if "High Severity" not in subject:
        return None

    return msg.text_part.get_payload().decode(msg.text_part.charset)


def get_event(raw_msg):
    pattern = re.compile(r'(\bMessage:)([a-zA-Z0-9-\s]+(\bgateway)([a-zA-Z0-9-\s]+.))', re.I)
    matches = pattern.finditer(raw_msg)
    # print(matches)
    return matches

def botsy(telegram_message):
    bot = telegram.Bot(bot_token)
    bot.sendMessage(chat_ID, text=telegram_message)

imap()
while True:
    try:
        print("""
                   __          __     _  _    _                              
           \ \        / /    (_)| |  (_)                             
            \ \  /\  / /__ _  _ | |_  _  _ __    __ _                
             \ \/  \/ // _` || || __|| || '_ \  / _` |               
 _  _  _  _  _\  /\  /| (_| || || |_ | || | | || (_| | _  _  _  _  _ 
(_)(_)(_)(_)(_)\/  \/  \__,_||_| \__||_||_| |_| \__, |(_)(_)(_)(_)(_)
                                                 __/ |               
                                                |___/                
        """)
        messages=get_unread()
        while messages is None:
            time.sleep(5)
            messages = get_unread()
        for a in messages.keys():
            if type(a) is not int:
                continue
            received_email=analyze_msg(messages, a)
            if received_email is None:
                pass
            elif received_email:
                parsed_email = get_event(received_email)
                print(parsed_email)
                for match in parsed_email:
                    if not match.group(4):
                        # print(match.group(4))
                        pass
                    elif match.group(4):
                        botsy(str(match.group(4)))
                        break
                    else:
                        pass

    except KeyboardInterrupt:
        connect.logout()
        break
    except OSError:
        imap()
        continue
