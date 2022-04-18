import socket
import bloom

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
                msg = client.recv(2048)
                if msg:
                    # QUERY or UPLOAD
                    request, bloomstring = msg.decode("utf-8").split("|")
                    print("Recieved message: {} {}", request, bloomstring)
                    if request == "QUERY":
                        pass
                        # perform bloom matching against cbf_array
                        # return result
                    elif request == "UPLOAD":
                        pass
                        # add bloom to cbf_array
                        # have to convert from '001001' to [0,0,1,0,0,1]
                        realbloom = [0] * bloom.BLOOM_FILTER_SIZE
                        i = 0
                        for char in bloomstring:
                            if char == '0':
                                realbloom[i] = 0
                            else:
                                realbloom[i] = 1
                        cbf_array.append(realbloom)

                    print('sending data back to the client')
                    newstr = "ok"
                    client.sendall(newstr)
                else:
                    print('connection closed with: ' + str(client_addr))
                    break

        finally:
            client.close()


if __name__ == "__main__":
	backend_server()