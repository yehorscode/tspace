import os
def getSpaceFile(path):
        return os.path.getsize(path)
# print(getSpace()) # returns in bytes

def getSpace(path = "/home/yehors/tspace/counter", debug = False):
    root, dirs, files = next(os.walk(path))
    if debug:
        print("[0]: ", root)
        print("[1]: ", dirs)
        print("[2]: ", files)
    return [root, dirs, files]

def getSize(path):
    size = 0
    base_path = path[0]
    folders = path[1]
    files = path[2]
    to_scan = []

    for folder in folders:
        to_scan.append(os.path.join(base_path, folder))
    for file in files:
        to_scan.append(os.path.join(base_path, file))

    counter = 0
    for item in to_scan:
        if os.path.isdir(item):
            temp = getSpace(item)
            for folder in temp[1]:
                to_scan.append(os.path.join(item, folder))
            for file in temp[2]:
                to_scan.append(os.path.join(item, file))
    while len(to_scan) > 0:
        for item in to_scan:
            if os.path.isdir(item):
                to_scan.remove(item)
            else:
                file_size = os.path.getsize(item)
                print(file_size, "  ", item)
                size += file_size
                to_scan.remove(item)
    print(len(to_scan))
    return to_scan, size


def getFolderSpace(path = "/home/yehors/tspace/counter"):
    return getSize(getSpace(path))


print(getFolderSpace())