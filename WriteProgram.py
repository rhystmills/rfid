#!/usr/bin/env python
# -*- coding: utf8 -*-

import mfrc522 as MFRC522
import signal
import itertools

continue_reading = True


data_blocks = [4, 5, 6,
               8, 9, 10,
               12, 13, 14,
               16, 17, 18,
               20, 21, 22,
               24, 25, 26,
               28, 29, 30,
               32, 33, 34,
               36, 37, 38,
               40, 41, 42,
               44, 45, 46,
               48, 49, 50,
               52, 53, 54,
               56, 57, 58,
               60, 61, 62]

sectors = [{
    "control": 0,
    "blocks": [1,2]
},
{
    "control": 4,
    "blocks": [4,5,6]
}]

def end_read(signal, frame):
    '''
    Capture SIGINT for cleanup when the script is aborted
    '''
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False

string = 'print("hello, world")'

maxBytes = 16 * 3 * 16
# 16 bytes * 3 blocks * 15 sectors (first sector should have two additional data blocks but not having luck writing to it)

def stringToIntArray(string):
    bytes = [elem.encode("utf-8") for elem in string]
    intsFromBytes = [int.from_bytes(byte, 'little') for byte in bytes]
    return intsFromBytes

def padInts(ints):
    last = ints[-1]
    if len(last) < 16:
        while len(last) < 16:
            last.append(0)

def splitIntArrayToSixteenIntGroups(intArray):
    desiredByteLength = len(intArray)
    if desiredByteLength > maxBytes:
        print(f"Error: attempted to write too many bytes ({desiredByteLength}) to card, max length is {maxBytes}")
        return
    grouped = []
    for i in range(0, len(intArray), 16):
        grouped.append(intArray[i:i + 16])
    padInts(grouped)
    return grouped


# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:

    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print("Card detected")

    # Get the UID of the card
    (status, uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:

        # Print UID
        print("Card read UID: " + str(uid[0]) + "," + str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3]))

        # This is the default key for authentication
        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        # ...for sector 3, 8 would be the block to auth - i.e. MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)
        # ...we auth per sector, so would need to re-auth for sector 4
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 0, key, uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:

            # Variable for the data to write
            data = splitIntArrayToSixteenIntGroups(stringToIntArray(string))

            # Fill the data with 0x00 - 0x0F
            # for x in range(0, 16):
            #     data.append(x)

            print("Sector 8 looked like this:")
            # Read block 8
            print(MIFAREReader.MFRC522_Read(1))

            print("Sector 8 will now be filled with 0xFF:")
            # Write the data
            MIFAREReader.MFRC522_Write(1, data[0])
            MIFAREReader.MFRC522_Write(2, data[1])

            print("It now looks like this:")
            # # Check to see if it was written
            print(MIFAREReader.MFRC522_Read(1))

            # print("Sector 8 will now be filled with 0xFF:")
            # # Write the data        
            # MIFAREReader.MFRC522_Write(9, data)

            # Stop
            MIFAREReader.MFRC522_StopCrypto1()

            # Make sure to stop reading for cards
            continue_reading = False
        else:
            print("Authentication error")
