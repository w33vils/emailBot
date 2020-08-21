
import getpass

read_from=input("Enter mailbox to read from: ")
imap_server=input("Enter imap server: ")

password=getpass.getpass("Account Password: ")
sender_address = input("Trusted sender address: ")

bot_token = input("Telegram Bot Token : ")
chat_ID = input ("Channel Chat ID : ")