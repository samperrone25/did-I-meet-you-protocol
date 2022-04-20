import socket
import bloom
from constants import *

# inspiration: https://pymotw.com/3/socket/tcp.html

# variables
cbf_array = []
ip_port = (BACKEND_IP, BACKEND_PORT) # use port 55000, ip found with linux: 'ifconfig'

def backend_server():
    # use TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # bind socket
    print('Starting on {}:{}'.format(*ip_port))
    server.bind(ip_port)

    # listen
    server.listen()
    while True:

        # await clients
        print('Idle...')
        client, client_addr = server.accept()

        try:
            print('Connected to: ' + str(client_addr))
            msg = client.recv(2048)
            if msg:
                # QUERY or UPLOAD
                request, bloomstring = msg.decode("utf-8").split("|")
                print("Recieved message: {} {}".format(request, bloomstring))
                send_str = "Please make a query or upload"
                if request == "QUERY":
                    # perform bloom matching against cbf_array
                    match = False
                    realbloom = bloom.to_array(bloomstring)
                    for filter in cbf_array:
                        intersection = bloom.bloom_intersection(realbloom, filter)
                        if sum(intersection) >= 3: # 3 hash functions -> 3 similar bits
                            match = True

                    # return result
                    if match:
                        send_str = "Match"
                    else: 
                        send_str = "No Match"
                    
                elif request == "UPLOAD":
                    # add bloom to cbf_array
                    realbloom = bloom.to_array(bloomstring)
                    cbf_array.append(realbloom)
                    print("CBF added to cbf_array")
                    send_str = "Upload Successful"
                
                client.sendall(send_str.encode('utf-8'))
                print("Replied: " + send_str)

            else:
                print('Connection closed with: ' + str(client_addr))

        finally:
            client.close()

if __name__ == "__main__":
	backend_server()