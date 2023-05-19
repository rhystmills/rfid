import RPi.GPIO as GPIO
import mfrc522 as MFRC522
import signal
import itertools

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print("Welcome to the MFRC522 data read example")
print("Press Ctrl-C to stop.")

def stringToIntArray(string):
    bytes = [elem.encode("utf-8") for elem in string]
    intsFromBytes = [int.from_bytes(byte) for byte in bytes]
    return intsFromBytes

def intArrayToString(ints):
    stringAsBytes = bytes(ints)
    string = stringAsBytes.decode("utf-8") 
    strippedOfNullBytes = string.rstrip('\x00')
    return strippedOfNullBytes

def generateSectors():
    numberOfSectors = 15
    firstSector = 1
    sectors = []
    for sectorIndex in range(firstSector, firstSector + numberOfSectors):
        sectorControl =  sectorIndex * 4
        sector = {
            "control": sectorControl,
            "blocks": []  
        }
        for i in range (0, 3):
            sector["blocks"].append(sectorControl + i)
        sectors.append(sector)
    return sectors

sectors = generateSectors()

def readSector(sector):
    print(sector["control"])
    # Data is an list of 16-int lists with max length 3 
    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, sector["control"], key, uid)
    sectorData = []
    if status == MIFAREReader.MI_OK:
        blocks = sector["blocks"]
        for block in blocks:
            print(f"reading from block {block}:")
            sectorData.append(MIFAREReader.MFRC522_Read(block))
        # time.sleep(1)
        # Make sure to stop reading for cards
        continue_reading = False
        ints = list(itertools.chain(*sectorData))
        string = intArrayToString(ints)
        return string
    else:
        print("Authentication error")


# This loop keeps checking for chips. If one is near it will get the UID and authenticate
# while continue_reading:
    
#     # Scan for cards    
#     (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

#     # If a card is found
#     if status == MIFAREReader.MI_OK:
#         print("Card detected")
    
#     # Get the UID of the card
#     (status,uid) = MIFAREReader.MFRC522_Anticoll()

#     # If we have the UID, continue
#     if status == MIFAREReader.MI_OK:

#         # Print UID
#         print("Card read UID: %s,%s,%s,%s" % (uid[0], uid[1], uid[2], uid[3]))
    
#         # This is the default key for authentication
#         key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
        
#         # Select the scanned tag
#         MIFAREReader.MFRC522_SelectTag(uid)

#         # Authenticate
#         status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 0, key, uid)

#         # Check if authenticated
#         if status == MIFAREReader.MI_OK:
#             data = []
#             datum0 = MIFAREReader.MFRC522_Read(1)
#             datum1 = MIFAREReader.MFRC522_Read(2)
#             # datum2 = MIFAREReader.MFRC522_Read(7)
#             data.append(datum0)
#             data.append(datum1)
#             # data.append(datum2)
#             ints = list(itertools.chain(*data))
#             string = intArrayToString(ints)
#             print("String is:")
#             print(string)
#             print("Executing string:")
#             exec(string)
#             MIFAREReader.MFRC522_StopCrypto1()
#         else:
#             print("Authentication error")

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print("Card detected")

    # Get the UID of the card
    (status, uid) = MIFAREReader.MFRC522_Anticoll()
    # data = splitArrayIntoGroupsOfThree(splitIntArrayToSixteenIntGroups(stringToIntArray(string)))
    # print(data)
    MIFAREReader.MFRC522_SelectTag(uid)
    data = []
    for sector in sectors:
        data.append(readSector(sector))
    program = ''.join(data)
    print(program)
    exec(program)
    MIFAREReader.MFRC522_StopCrypto1()
    continue_reading = False
