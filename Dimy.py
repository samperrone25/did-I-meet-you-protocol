# ephID generation
from ecdsa import SigningKey, SECP128r1
from ecdsa.util import randrange

from socket import *
import threading
import time
from hashlib import sha256
from binascii import hexlify, unhexlify
from Crypto.Protocol.SecretSharing import Shamir
import pyDH
import random

# global variable
port = 38000
key = 0
ephID_hash = ""
dh = pyDH.DiffieHellman()

print("----------Server Starting----------")

# helpers
# used secexp as the dh public key
def generate_ephid():
	curve = SECP128r1
	secexp = randrange(curve.order)
	sk = SigningKey.from_secret_exponent(secexp, curve)
	ephid = sk.to_string()

	return secexp, ephid
# print both id and recive shares
def print_id(id, chunks):
	print()
	print(f"Generating ID: {hexlify(id)}")
	for i, chunk in chunks:
		print(f"Chunk {i}: ({i}, {hexlify(chunk)})")
	print()

def message_drop():
	num = random.uniform(0, 1)
	return num<0.5

# udp client/server in this case
# Broadcaster and reciever is taken from 
# the code snippet here:
# https://gist.github.com/ninedraft/7c47282f8b53ac015c1e326fffb664b5
def udp_server():

	global port, ephID_hash, key
	public_key = dh.gen_public_key()

	# create socket
	broadcaster = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
	broadcaster.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

	# create new ephID and generate recv_shares
	key, ephID = generate_ephid()
	# split id in to chunks (about to send)
	# format: [id][content]
	sender_ephID_chunk = Shamir.split(3, 5, ephID)

	# hash of ephid
	ephID_hash = sha256(ephID).hexdigest()

	# print id and id chunks
	print_id(ephID, sender_ephID_chunk)

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
			send_str = str(sender_ephID_chunk[0][0]) + "|" + hexlify(sender_ephID_chunk[0][1]).decode() + "|" + ephID_hash + "|" + str(public_key)
			# Message drop mech
			if message_drop():
				broadcaster.sendto(send_str.encode('utf-8'), ('255.255.255.255', port))
			else:
				print("Chunk not sent due to message drop mechanism")
			# FIXME: use the counter method instead of pop from top
			# and maybe don't include index
			sender_ephID_chunk.pop(0)
			broadcast_timer += 4.5

		# create new id every minute
		elif curr_timer > id_timer:
			# create new ephID and get the chunks
			key, ephID = generate_ephid()
			sender_ephID_chunk = Shamir.split(3, 5, ephID)
			
			# hash of ephid
			ephID_hash = sha256(ephID).hexdigest()

			# print id and sender's chunk
			print_id(ephID, sender_ephID_chunk)

			# set timer
			id_timer += 18

		# update timer
		curr_timer = time.time() - start_time

# udp client/server in this case
# Broadcaster and reciever is taken from 
# the code snippet here:
# https://gist.github.com/ninedraft/7c47282f8b53ac015c1e326fffb664b5
def udp_client():

	global port, ephID_hash, key
	
	new_contact_list = {}

	# create socket
	server_socket = socket(AF_INET, SOCK_DGRAM) # UDP
	server_socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
	server_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
	server_socket.bind(("", port))

	while True:

		# receive message
		recv_msg, recv_addr = server_socket.recvfrom(2048)
		# parse the messaeg
		recv_index = recv_msg.decode("utf-8").split("|")[0]
		recv_share = recv_msg.decode("utf-8").split("|")[1]
		recv_hash = recv_msg.decode("utf-8").split("|")[2]
		key = recv_msg.decode("utf-8").split("|")[3]

		# skip if receive own message
		if recv_hash == ephID_hash:
			continue
		else:
			# recv_index
			# TODO: seems like we can get rid of index
			# can keep it for demo purpose
			recv_index = int(recv_index)

			# recv_share
			recv_share = unhexlify(recv_share.encode())
			
			if recv_hash not in new_contact_list.keys():
				new_contact_list[recv_hash] = [(recv_index, recv_share)]
			else:
				new_contact_list[recv_hash].append((recv_index, recv_share))
			
			# keep track of number of recv_shares received
			num_recv_shares = len(new_contact_list[recv_hash])
			print()
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
					enc_id = dh.gen_shared_key(int(key))
					print(f"EncID is: {enc_id}")
				else:
					print("Error: Hash not verified.")
				print()

# thread for listening for beacons
broadcaster_server_thread = threading.Thread(name = "Server", target = udp_server, daemon = True)
broadcaster_server_thread.start()

# thread for receiving messages
broadcaster_receiver_thread = threading.Thread(name = "Client", target = udp_client)
broadcaster_receiver_thread.start()