import socket
import select

HEADER_LENGTH = 10

IP = ""
PORT = 5555

IP = input("IP: ")

# Criar socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Bind, informa o OS que vai usar um certo IP e PORT
s.bind((IP, PORT))

# Faz com que o servidor fique a espera de conexoes
s.listen()

# Lista de sockets
sockets_list = [s]

# Lista de clienets conectados
clients = {}

print(f'Listening for connections on ', IP,' :', PORT, '...')

# Recebe as mensagens
def receive_message(client_socket):

    try:
        # Recebe o HEADER que tem o comp. da mensagem o tamanho
        message_header = client_socket.recv(HEADER_LENGTH)

        # Sen nao receber nada "morre" a conexao
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode('utf-8').strip())

        # Deveolve o header e a mensagem da mensagem
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        return False

while True:
    # nao sei como isto sabe quando e k alguma cena se conecta
    read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)


    # conectou-se alguma cena?
    for notified_socket in read_sockets:

        # ver se e um conexao do socket
        if notified_socket == s:

            # Aceita a conexao
            # client_socket -> nova socket unica conectada SO a este cliente
            # client_address tem ip, port
            client_socket, client_address = s.accept()

            # Username do cliente
            user = receive_message(client_socket)

            # Se for falso o gajo saiu antes de por o nome
            if user is False:
                continue

            # Adiciona a nova socket a lista
            sockets_list.append(client_socket)

            # Guarda username
            clients[client_socket] = user

            print('Accepted new connection from {}:{}, username: {}'.format(*client_address, user['data'].decode('utf-8')))

        else:

            # Receber mensagem
            message = receive_message(notified_socket)

            # Se for falso cliente morreu :(
            if message is False:
                print('Closed connection from: {}'.format(clients[notified_socket]['data'].decode('utf-8')))

                # Tira a socket da lista
                sockets_list.remove(notified_socket)

                # Tira da lista de users
                del clients[notified_socket]

                continue

            # notified socket serve para saber de onde e que a mensagem veio
            user = clients[notified_socket]

            print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

            # Ciclo entre todos os clientes connectados e manda a mensagem para todos
            for client_socket in clients:
                # menos para o que enviou
                if client_socket != notified_socket:

                    # Manda a mensagem e o header k tem o user de quem mandou
                    client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])