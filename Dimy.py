# usage: python3 Dimy.py backendIP backendPORT time_until_covid

from ephID import *
import bloom
from socket import *
import threading
import time
from hashlib import sha256
from binascii import hexlify, unhexlify
from Crypto.Protocol.SecretSharing import Shamir
from queue import Queue
import sys
from constants import *

# global variables
priv_key = 0
ephID_hash = ""

print("----------DIMY Node Starting----------")

# UDP broadcaster
# https://gist.github.com/ninedraft/7c47282f8b53ac015c1e326fffb664b5
def udp_server():

	global ephID_hash, priv_key

	# create socket
	broadcaster = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
	broadcaster.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

	# create new ephID and generate recv_shares
	priv_key, ephID = gen_ephID()
	# split id in to chunks (about to send)
	# format: [id][content]
	sender_ephID_chunk = Shamir.split(3, 5, ephID)
	print_id(ephID, sender_ephID_chunk)

	# hash of ephid
	ephID_hash = sha256(ephID).hexdigest()

	start_time = time.time()
	id_timer = ID_TIMER # generate new ephID every ID_TIMER seconds
	broadcast_timer = 0 # begin broadcasting straight away
	curr_timer = time.time() - start_time

	while True:

		# broadcast
		if curr_timer > broadcast_timer and len(sender_ephID_chunk) != 0:
			print(f"Broadcast chunks: {sender_ephID_chunk[0][0], hexlify(sender_ephID_chunk[0][1])}\n")
			send_str = str(sender_ephID_chunk[0][0]) + "|" + hexlify(sender_ephID_chunk[0][1]).decode() + "|" + ephID_hash
			broadcaster.sendto(send_str.encode('utf-8'), ('255.255.255.255', NODE_PORT))
			sender_ephID_chunk.pop(0)
			broadcast_timer += BROADCAST_INTERVAL # broadcast shares at 1 unique share per BROADCAST_INTERVAL seconds

		# create new id
		elif curr_timer > id_timer:
			# create new ephID and get the chunks
			priv_key, ephID = gen_ephID()
			sender_ephID_chunk = Shamir.split(3, 5, ephID)
			
			# hash of ephid
			ephID_hash = sha256(ephID).hexdigest()

			# print id and sender's chunk
			print_id(ephID, sender_ephID_chunk)

			# set timer
			id_timer += ID_TIMER # generate new ephID every ID_TIMER seconds

		# update timer
		curr_timer = time.time() - start_time

# UDP reciever
# inspiration: https://gist.github.com/ninedraft/7c47282f8b53ac015c1e326fffb664b5
def udp_client():

	global ephID_hash, priv_key
	
	new_contact_list = {}

	# create socket
	server_socket = socket(AF_INET, SOCK_DGRAM) # UDP
	server_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
	server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
	server_socket.bind(("", NODE_PORT))
	
	DBFQueue = Queue(maxsize = 6) # queue of daily bloom filters
	DBF = [0] * bloom.BLOOM_FILTER_SIZE
	infected = False
	DBFtimer = DBF_TIMER # new dbf every DBF_TIMER seconds
	QBFtimer = QBF_TIMER # new qbf every QBF_TIMER seconds
	start_time2 = time.time()
	current_time2 = time.time() - start_time2
	covid_time = int(sys.argv[3]) # time until diagnosis

	while True:

		# receive message
		recv_msg, recv_addr = server_socket.recvfrom(2048)
		recv_index, recv_share, recv_hash = recv_msg.decode("utf-8").split("|")

        # check dbf timer
		if current_time2 > DBFtimer:
			print("DBF expired")
			print("DBF: ", end = "")
			bloom.print_bloom(DBF)

			DBFQueue.put(DBF) # enqueue old DBF
			DBF = [0] * bloom.BLOOM_FILTER_SIZE # make new DBF
			DBFtimer += DBF_TIMER # new dbf every DBF_TIMER seconds

        # check qbf timer, no need to make qbf's if infected
		if current_time2 > QBFtimer and not infected:
			QBF = [0] * bloom.BLOOM_FILTER_SIZE # make QBF
			while not DBFQueue.empty():
				temp_filter = DBFQueue.get() # remove and return item from queue
				QBF = bloom.merge_blooms(QBF, temp_filter)
			
			print("QBF created: ", end = "")
			bloom.print_bloom(QBF)
			
			# send to backend via tcp
			send_str = "QUERY" + "|" + bloom.to_string(QBF)
			backend = socket(AF_INET, SOCK_STREAM)
			backend.connect((sys.argv[1], int(sys.argv[2])))
			backend.sendall(send_str.encode('utf-8'))

			# recieve and display result
			recv_msg2 =  backend.recv(2048).decode("utf-8")
			if not recv_msg2:
				print("No response from server")
			print("Servers response: " + str(recv_msg2) + "\n")

			backend.close()

			if recv_msg2 == "Match": # upload cbf to server and stop making QBF's
			    # the qbf and the cbf are both just the combination of all dbf's, therefore we can upload the qbf as the cbf
				send_str2 = "UPLOAD" + "|" + bloom.to_string(QBF)
				backend = socket(AF_INET, SOCK_STREAM)
				backend.connect((sys.argv[1], int(sys.argv[2])))
				backend.sendall(send_str2.encode('utf-8'))
				print("CBF uploaded: ", end = "")
				bloom.print_bloom(QBF)
				infected = True

				# recieve and display result
				recv_msg2 =  backend.recv(2048).decode("utf-8")
				if not recv_msg2:
					print("No response from server")
				else:
					print("Servers response: " + str(recv_msg2) + "\n")
				backend.close()

			QBFtimer += QBF_TIMER # new qbf every QBF_TIMER seconds

        # a node recieves a covid diagnosis
		if current_time2 > covid_time and not infected:
			infected = True
			# upload cbf
			CBF = [0] * bloom.BLOOM_FILTER_SIZE # make QBF
			while not DBFQueue.empty():
				temp_filter = DBFQueue.get() # remove and return item from queue
				CBF = bloom.merge_blooms(CBF, temp_filter)
			
			# send to backend via tcp
			send_str = "UPLOAD" + "|" + bloom.to_string(CBF)
			backend = socket(AF_INET, SOCK_STREAM)
			backend.connect((sys.argv[1], int(sys.argv[2])))
			backend.sendall(send_str.encode('utf-8'))
			print("CBF uploaded: ", end = "")
			bloom.print_bloom(CBF)

			# recieve and display result
			recv_msg2 =  backend.recv(2048).decode("utf-8")
			if not recv_msg2:
				print("No response from server")
			print("Servers response: " + str(recv_msg2) + "\n")
			backend.close()

		# skip if receive own message
		if recv_hash == ephID_hash:
			continue
		else:
			print("Recieved id share {}", recv_share)
			recv_index = int(recv_index)

			# recv_share
			recv_share = unhexlify(recv_share.encode())
			
			if recv_hash not in new_contact_list.keys():
				new_contact_list[recv_hash] = [(recv_index, recv_share)]
			else:
				new_contact_list[recv_hash].append((recv_index, recv_share))
			
			# keep track of number of recv_shares received
			num_recv_shares = len(new_contact_list[recv_hash])
			print(f"Received {num_recv_shares} chunks from {recv_hash}.\n")
			
			# Check if the hash contains 3 entries
			if num_recv_shares == 3:
				sec = Shamir.combine(new_contact_list[recv_hash])
				print(f"Reconstructing EphID: {hexlify(sec)}")
				print("Verifying integrity of EphID...")
				new_hash = sha256(sec).hexdigest()
				print()
				print(f"Received hash: 	   {recv_hash}")
				print(f"Recontructed hash: {new_hash}")
				print()
				if recv_hash == new_hash:
					print(f"Verified hash. Computing EncID...")
					enc_id = int(hexlify(sec), 16) * priv_key
					print(f"EncID is: {enc_id}")
					
					if not bloom.check_item(DBF, str(enc_id)): # add enc id
						bloom.add_item(DBF, str(enc_id))

				else:
					print("Error: Hash not verified.")
				print()

		# update timer
		current_time2 = time.time() - start_time2


if __name__ == "__main__":

	# thread for listening for beacons
	broadcaster_server_thread = threading.Thread(name = "Server", target = udp_server, daemon = True)
	broadcaster_server_thread.start()

	# thread for receiving messages
	broadcaster_receiver_thread = threading.Thread(name = "Client", target = udp_client)
	broadcaster_receiver_thread.start()