from ephID import *
import bloom
from socket import *
import threading
import time
from hashlib import sha256
from binascii import hexlify, unhexlify
from Crypto.Protocol.SecretSharing import Shamir
from queue import Queue

# global variable
port = 38000
priv_key = 0
ephID_hash = ""

print("----------Server Starting----------")

# udp client/server in this case
# Broadcaster and reciever is taken from 
# the code snippet here:
# https://gist.github.com/ninedraft/7c47282f8b53ac015c1e326fffb664b5
def udp_server():

	global port, ephID_hash, priv_key

	# create socket
	broadcaster = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
	broadcaster.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

	# create new ephID and generate recv_shares
	priv_key, ephID = gen_ephID()
	# split id in to chunks (about to send)
	# format: [id][content]
	sender_ephID_chunk = Shamir.split(3, 5, ephID)

	# hash of ephid
	ephID_hash = sha256(ephID).hexdigest()

	# print id and id chunks
	#print_id(ephID, sender_ephID_chunk)

	# TODO: change
	# timer
	start_time = time.time()
	id_timer = 18
	broadcast_timer = 0
	curr_timer = time.time() - start_time

	while True:

		# broadcast id every 15 seconds 15/60 = 4.5/18
		if curr_timer > broadcast_timer and len(sender_ephID_chunk) != 0:
			print(f"Broadcast chunks: {sender_ephID_chunk[0][0], hexlify(sender_ephID_chunk[0][1])}")
			send_str = str(sender_ephID_chunk[0][0]) + "|" + hexlify(sender_ephID_chunk[0][1]).decode() + "|" + ephID_hash
			broadcaster.sendto(send_str.encode('utf-8'), ('255.255.255.255', port))
			# FIXME: use the counter method instead of pop from top
			# and maybe don't include index
			sender_ephID_chunk.pop(0)
			broadcast_timer += 4.5

		# create new id every minute
		elif curr_timer > id_timer:
			# create new ephID and get the chunks
			priv_key, ephID = gen_ephID()
			sender_ephID_chunk = Shamir.split(3, 5, ephID)
			
			# hash of ephid
			ephID_hash = sha256(ephID).hexdigest()

			# print id and sender's chunk
			print_id(ephID, sender_ephID_chunk)

			# set timer
			id_timer += 25 # was 18

		# update timer
		curr_timer = time.time() - start_time

# udp client/server in this case	
# Broadcaster and reciever is taken from 
# the code snippet here:
# https://gist.github.com/ninedraft/7c47282f8b53ac015c1e326fffb664b5
def udp_client():

	global port, ephID_hash, priv_key
	
	new_contact_list = {}

	# create socket
	server_socket = socket(AF_INET, SOCK_DGRAM) # UDP
	server_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
	server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
	server_socket.bind(("", port))
	
	DBFQueue = Queue(maxsize = 6)
	DBF = [0] * bloom.BLOOM_FILTER_SIZE
	# use bloom.tostring(dbf) to make sendable object
	DBFtimer = 30 # was 90
	QBFtimer = 90 # was 9 minutes -> 540s
	start_time2 = time.time()
	current_time2 = time.time() - start_time2

	while True:

		# receive message
		recv_msg, recv_addr = server_socket.recvfrom(2048)
		recv_index, recv_share, recv_hash = recv_msg.decode("utf-8").split("|")

		##
		if current_time2 > DBFtimer: # check dbf timer
			print("DBF EXPIRED\n")
			print("DBF: ", end = "")
			bloom.print_bloom(DBF)

			DBFQueue.put(DBF) # enqueue old DBF
			DBF = [0] * bloom.BLOOM_FILTER_SIZE # make new DBF
			DBFtimer += 30 # update DBFtimer

		if current_time2 > QBFtimer: ## check qbf timer
			for i in range(5):
				print("MAKING QBF\n")
			QBF = [0] * bloom.BLOOM_FILTER_SIZE # make QBF
			while not DBFQueue.empty():
				temp_filter = DBFQueue.get()
				QBF = bloom.merge_blooms(QBF, temp_filter)
			
			print("QBF: ", end = "")
			bloom.print_bloom(QBF) # debug
			# send to backend via tcp
			# recieve and display result
			QBFtimer += 90 # update timer
			##
		##

		# skip if receive own message
		if recv_hash == ephID_hash:
			continue
		else:
			print("recieved id share")
			# recv_index
			# TODO: seems like we can get rid of index
			recv_index = int(recv_index)

			# recv_share
			recv_share = unhexlify(recv_share.encode())
			
			if recv_hash not in new_contact_list.keys():
				new_contact_list[recv_hash] = [(recv_index, recv_share)]
			else:
				new_contact_list[recv_hash].append((recv_index, recv_share))
			
			# keep track of number of recv_shares received
			num_recv_shares = len(new_contact_list[recv_hash])
			print(f"Received {num_recv_shares} chunks from {recv_hash}.")
			print()
			
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
					# delete enc_id?

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