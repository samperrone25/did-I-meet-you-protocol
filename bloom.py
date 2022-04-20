# all bloom filters are 100kb and use 3 hash functions
# 100 KB = 819200 bits

# bloom_filter = [0] * size
import pyhash

BLOOM_FILTER_SIZE = 100 # change to 819200 for real implementation, 100 KILOBYTES = 819200 BITS
HFUNCS = [pyhash.murmur3_32(), pyhash.lookup3(), pyhash.xx_64()]

def add_item(bloom, item):

    indexes = [(hfunc(item) % BLOOM_FILTER_SIZE) for hfunc in HFUNCS ]

    for index in indexes:
        bloom[index] = 1

    return

def check_item(bloom, item):

    indexes = [(hfunc(item) % BLOOM_FILTER_SIZE) for hfunc in HFUNCS ]

    for index in indexes:
        if (bloom[index] != 1):
            return False

    return True

def print_bloom(bloom):

    i = 0
    print("Indexes ", end = "")
    empty = True
    for bit in bloom:
        if bit == 1:
            print(str(i) + ", ", end = "")
            empty = False
        #if (i % 10 == 9):
        #    print('\n')
        i += 1
    if empty:
        print("Empty")
    print(" \n")

    # Indexes 1, 3, 70, 8780, 

def to_string(bloom): # implement me
    s = ''
    for entry in bloom:
        if entry == 0:
            s += '0'
        else:
            s += '1'
    return s

# converts string '0101' bloom to array [0,1,0,1] bloom
def to_array(bloomstring):
    realbloom = [0] * BLOOM_FILTER_SIZE
    i = 0
    for char in bloomstring:
        if char == '0':
            realbloom[i] = 0
        else:
            realbloom[i] = 1
        i += 1
    return realbloom

def merge_blooms(bloom1, bloom2):

    newbloom = [0] * BLOOM_FILTER_SIZE
    for i in range(BLOOM_FILTER_SIZE):
        if (bloom1[i] or bloom2[i]): # OR the bits
            newbloom[i] = 1
        else:
            newbloom[i] = 0
    
    return newbloom

def bloom_intersection(bloom1, bloom2):

    newbloom = [0] * BLOOM_FILTER_SIZE
    for i in range(BLOOM_FILTER_SIZE):
        if (bloom1[i] and bloom2[i]): # AND the bits
            newbloom[i] = 1
        else:
            newbloom[i] = 0
    
    return newbloom

def sample_test():

    bloom_filter = [0] * BLOOM_FILTER_SIZE
    print_bloom(bloom_filter)

    print(check_item(bloom_filter, "Jimmy"))
    print(check_item(bloom_filter, "Carlos"))
    print()

    add_item(bloom_filter, "Jimmy")
    print_bloom(bloom_filter)
    print(check_item(bloom_filter, "Jimmy"))
    print()

    add_item(bloom_filter, "Carlos")
    print_bloom(bloom_filter)
    print(check_item(bloom_filter, "Carlos"))

def merge_test():

    bloom1 = [0] * BLOOM_FILTER_SIZE
    add_item(bloom1, "hashme")
    print_bloom(bloom1)
    print()

    bloom2 = [0] * BLOOM_FILTER_SIZE
    add_item(bloom2, "hashmeaswell")
    print_bloom(bloom2)
    print()

    newbloom = merge_blooms(bloom1, bloom2)
    print_bloom(newbloom)
    print('or:')
    print(to_string(newbloom))

if __name__ == "__main__":
    # put desired tests here
    # sample_test()
    merge_test()
