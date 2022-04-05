# pip install shamir
# import shamir
# Can use this but this is a bit dodgy
# PyCryptodome is more official and has more 
# Documentation
# secret, shares = make_random_secret(3, 5)

from Crypto.Protocol.SecretSharing import Shamir

# 3 out of 5 according to the spec
def generate_shares(secret):
    return Shamir.split(3, 5, secret)

# reconstruction
def reconstruct_secret(shares):
    return Shamir.combine(shares)