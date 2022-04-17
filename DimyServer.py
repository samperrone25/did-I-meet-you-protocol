import socket

# inspiration: https://pymotw.com/3/socket/tcp.html

# variables
cbf_array = []
ip_port = ('192.168.88.100', 55000) # use port 55000, ip can change

def backend_server():
    # use TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind socket
    print('starting up on {} port {}'.format(*ip_port))
    server.bind(ip_port)

    # listen
    server.listen()
    while True:

        # await clients
        print('waiting')
        client, client_addr = server.accept()

        try:
            print('connection with: ' + str(client_addr))

            while True:
                data = client.recv(2048)
                print('received: ' + str(data))
                if data:
                    print('sending data back to the client')
                    newstr = "ok"
                    client.sendall(newstr)
                else:
                    print('connection closed with: ' + str(client_addr))
                    break

        finally:
            # Clean up the client
            client.close()


if __name__ == "__main__":
	backend_server()