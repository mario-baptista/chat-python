import socket
from tkinter import *
import threading
import errno
import sys
from gtts import gTTS
from io import BytesIO
import pygame

my_username = ""
root = Tk()
root.title("Chat")

ola = ""

aux = False

def ovokinder():

    global ola

    global aux

    messages_frame = Frame(root)
    scrollbar = Scrollbar(messages_frame)

    msg_list = Listbox(messages_frame, height=15, width=100, yscrollcommand=scrollbar.set)
    mensagem = "Bem vindo"
    msg_list.insert(1, mensagem)
    scrollbar.pack(side=RIGHT, fill=Y)
    msg_list.pack(side=LEFT, fill=BOTH)
    msg_list.pack()
    messages_frame.pack()

    e = Entry(root, width=100)
    e.pack()
    send_button = Button(root, text="Enviar", command=lambda: aaa(e.get()), width=10)
    send_button.pack()

    i = 2

    while True:

        if aux:
            e.delete(0, END)
            aux = False

        if ola:
            msg_list.insert(i, ola)

            i+=1

            ola = ""

        root.update_idletasks()
        root.update()


HEADER_LENGTH = 10

IP = ""
PORT = 5555

IP = input("IP: ")
my_username = input("Username: ")

# Criar socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connecta ao IP e port
client_socket.connect((IP, PORT))
client_socket.setblocking(False)

# Antes de mandar o username e header dar encode
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)


def aaa(message):
    global aux
    aux = True
    # message = input(f'{my_username} -> ')
    if message:
        # Dar encode da mensagem
        message = message.encode('utf-8')
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
        client_socket.send(message_header + message)
        message = ""
def bbb():
    global ola
    while True:
        try:
            # Loop para ver se ha msg novas para mostrar

            username_header = client_socket.recv(HEADER_LENGTH)

            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            # Converter header para int
            username_length = int(username_header.decode('utf-8').strip())

            # Receber user
            username = client_socket.recv(username_length).decode('utf-8')

            # A mesma cena para a mensagem
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            first_chars = message[0:5]
            if first_chars == '/tts ':
                message = message[5:]
                mp3_fp = BytesIO()
                message = username + " disse " + message
                tts = gTTS(message, 'pt')

                tts.write_to_fp(mp3_fp)
                mp3_fp.seek(0)

                pygame.mixer.init()
                pygame.mixer.music.load(mp3_fp)
                pygame.mixer.music.play()
                ola = message

            # Print
            # print('\n' + username, '->', message)
            # print(my_username, '->')
            if first_chars != '/tts ':
                ola = username + ' -> ' + message


        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()
            # continue

        except Exception as e:
            print('Reading error: '.format(str(e)))
            sys.exit()

y = threading.Thread(target=bbb)
y.start()
ovokinder()

# o = threading.Thread(target=ovokinder)
# o.start()
