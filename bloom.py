# all bloom filters are 100kb and use 3 hash functions
# 100 KB = 800000 bits

# bloom_filter = [0] * size
import pyhash

BLOOM_FILTER_SIZE = 20 # change to 80000 for real implementation
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
    for bit in bloom:
        print(str(bit) + ' ')
        if (i % 10 == 9):
            print('\n')
        i += 1

def merge_blooms(bloom1, bloom2):

    newbloom = [0] * BLOOM_FILTER_SIZE
    for i in range(BLOOM_FILTER_SIZE):
        if (bloom1[i] or bloom2[i]): # OR the bits
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
    print()

if __name__ == "__main__":
    # put desired tests here
    # sample_test()
    merge_test()