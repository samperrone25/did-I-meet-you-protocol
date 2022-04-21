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
from ephID import *


# global variable
port = 38000
key = 0
ephID_hash = ""
dh = pyDH.DiffieHellman()
public_key = dh.gen_public_key()

print("[Task 11A]")
print("----------Attacker Starting----------")

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
		recv_index = recv_msg.decode("utf-8").split("|")[0]
		recv_share = recv_msg.decode("utf-8").split("|")[1]
		recv_hash = recv_msg.decode("utf-8").split("|")[2]
		key = recv_msg.decode("utf-8").split("|")[3]
		k, attacker = gen_ephID()
		sender_ephID_chunk = Shamir.split(3, 5, attacker)
		payload = hexlify(sender_ephID_chunk[0][1]).decode()
		# skip if receive own message
		if recv_hash == ephID_hash:
			continue
		else:
			
			broadcaster = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
			broadcaster.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
			print("[Task 11A] sending the attacking payload")
			send_str = recv_index + "|" + payload + "|" + recv_hash + "|" + str(public_key)
			broadcaster.sendto(send_str.encode('utf-8'), ('255.255.255.255', port))

# thread for receiving messages
broadcaster_receiver_thread = threading.Thread(name = "Attacker", target = udp_client)
broadcaster_receiver_thread.start()
