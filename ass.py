
import time
import uuid
# Task 1
# Generate a 16-Byte Ephemeral ID
# generate Xat (rand num)
class ephID:
    def __init__(self, id, exp):
        self.id = ''
        self.exp = False

    def getID():
        return self.id

    def genEphid():
        id = uuid.uuid1()

    def expire():
        self.exp = True
    
def genEphid():
    return uuid.uuid1()
starttime = time.time()
# frequency in seconds
freq = 1.0
while True:
    id = genEphid()
    print(id)
    time.sleep(freq - ((time.time() - starttime) % freq))