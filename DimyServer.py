import socket
import bloom
from constants import *

# global variables
cbf_array = []
ip_port = (BACKEND_IP, BACKEND_PORT) # use port 55000, ip found with linux: 'ifconfig', may not be correct initially

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
        print('Idle...\n')
        client, client_addr = server.accept()

        try:
            print('Connected to: ' + str(client_addr))
            msg = client.recv(2048)
            if msg:
                # QUERY or UPLOAD
                request, bloomstring = msg.decode("utf-8").split("|")
                realbloom = bloom.to_array(bloomstring)
                print("Recieved message: {} ".format(request), end = " ")
                print("with bloom filter: ", end = "")
                bloom.print_bloom(realbloom)
                send_str = "Please make a query or upload"
                if request == "QUERY":
                    # perform bloom matching against cbf_array
                    print("[Task 10C] Comparing query bloom filter against stored contact bloom filters...")
                    match = False
                    all_cbfs = [0] * bloom.BLOOM_FILTER_SIZE 
                    if cbf_array:
                        for filter in cbf_array:
                            all_cbfs = bloom.merge_blooms(all_cbfs, filter)

                        intersection = bloom.bloom_intersection(realbloom, all_cbfs)
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
                
                client.sendall(send_str.encode('utf-8')) # reply to client
                print("Result: " + send_str + "\n")

            else:
                print('Connection closed with: ' + str(client_addr))

        finally:
            client.close()

if __name__ == "__main__":
	backend_server()
