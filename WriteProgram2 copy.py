#!/usr/bin/env python
# -*- coding: utf8 -*-

import mfrc522 as MFRC522
import signal
import itertools
import time
from pathlib import Path

continue_reading = True


# data_blocks = [4, 5, 6,
#                8, 9, 10,
#                12, 13, 14,
#                16, 17, 18,
#                20, 21, 22,
#                24, 25, 26,
#                28, 29, 30,
#                32, 33, 34,
#                36, 37, 38,
#                40, 41, 42,
#                44, 45, 46,
#                48, 49, 50,
#                52, 53, 54,
#                56, 57, 58,
#                60, 61, 62]

def end_read(signal, frame):
    '''
    Capture SIGINT for cleanup when the script is aborted
    '''
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False

# string = 'print("hello, world");print("hello, borld");print("hello, corld");print("hello, world");print("hello, borld");print("hello, corld")'
string=Path('program.txt').read_text()

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

def splitArrayIntoGroupsOfThree(array):
    groupsOfThree = []
    for i in range(0, len(array), 3):
        groupsOfThree.append(array[i:i + 3])
    return groupsOfThree

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

def writeSector(sector, data):
    print(sector["control"])
    # Data is an list of 16-int lists with max length 3 
    key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, sector["control"], key, uid)
    if status == MIFAREReader.MI_OK:
        blocks = sector["blocks"]
        for i,block in enumerate(blocks):
            if len(data) > i:
                print(f"writing to block {block}:")
                print(data[i])
                MIFAREReader.MFRC522_Write(block, data[i])
        # time.sleep(2)
        # Make sure to stop reading for cards
        continue_reading = False
    else:
        print("Authentication error")

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

sectors = generateSectors()
# sectors = [
#     {
#         "control": 4,
#         "blocks": [4,5,6]
#     },
#     ...
# ]

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print("Card detected")

    # Get the UID of the card
    (status, uid) = MIFAREReader.MFRC522_Anticoll()
    data = splitArrayIntoGroupsOfThree(splitIntArrayToSixteenIntGroups(stringToIntArray(string)))
    # print(data)
    MIFAREReader.MFRC522_SelectTag(uid)
    for i,intsTriple in enumerate(data):
        writeSector(sectors[i], intsTriple)

    MIFAREReader.MFRC522_StopCrypto1()
    continue_reading = False
