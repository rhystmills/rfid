# Execute a string as a python script
# exec('print("hello, world")')
string = 'print("hello, world");print("hello, borld");print("hello, corld")'

maxBytes = 16 * 3 * 16
# 16 bytes * 3 blocks * 15 sectors (first sector should have two additional data blocks but not having luck writing to it)

def stringToIntArray(string):
    bytes = [elem.encode("utf-8") for elem in string]
    intsFromBytes = [int.from_bytes(byte) for byte in bytes]
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
        



print(splitArrayIntoGroupsOfThree(splitIntArrayToSixteenIntGroups(stringToIntArray(string))))
print(generateSectors())