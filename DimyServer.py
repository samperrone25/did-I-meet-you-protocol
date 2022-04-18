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
                    realbloom = bloom.to_array(bloomstring)
                    cbf_array.append(realbloom)

            else:
                print('connection closed with: ' + str(client_addr))

        finally:
            client.close()

if __name__ == "__main__":
	backend_server()