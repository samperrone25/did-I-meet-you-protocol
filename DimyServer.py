import socket
import bloom

# inspiration: https://pymotw.com/3/socket/tcp.html

# variables
cbf_array = []
ip_port = ('192.168.88.132', 55000) # use port 55000, ip found with linux: 'ifconfig'

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
                send_str = "please make a query or upload"
                if request == "QUERY":
                    # perform bloom matching against cbf_array
                    match = False
                    realbloom = bloom.to_array(bloomstring)
                    for filter in cbf_array:
                        intersection = bloom.bloom_intersection(realbloom, filter)
                        print("intersection: {}", str(intersection))
                        print("sum: {}", str(sum(intersection)))
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

            else:
                print('connection closed with: ' + str(client_addr))

        finally:
            client.close()

if __name__ == "__main__":
	backend_server()