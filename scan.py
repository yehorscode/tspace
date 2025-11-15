import os
from tqdm import tqdm
import humanize
from collections import deque

def _normalize_path(path: str) -> str:
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))

def getSpaceFile(path):
    path = _normalize_path(path)
    try:
       return os.path.getsize(path)
    except OSError as e:
        print(f"getSpaceFile: cannot space out '{path}': {e}")
        return 0

def getSpace(path = "/home/yehors/tspace/counter", debug = False):
    path = _normalize_path(path)
    try:
        root, dirs, files = next(os.walk(path))
    except (OSError, StopIteration) as e:
        if debug:
            print(f"getSpace: cannot walk '{path}': {e}")
        return [path, [], []]
    if debug:
        print("[0]: ", root)
        print("[1]: ", dirs)
        print("[2]: ", files)
    return [root, dirs, files]

def getSize(path, debug: bool = False, pbar_enabled: bool = False, count_hardlinks_once: bool = True):
    """
    Path (str, empty) = where to scan
    Debug (bool, False) = wether to print all scanning operations
    pbar_enabled (bool, False) = enable/disable progress bar
    count_hardlinks_once (bool, True) = count hardlinks only once  
    """
    base_path, folders, files = path

    to_scan = deque([os.path.join(base_path, f) for f in folders])
    to_scan.extend(os.path.join(base_path, f) for f in files)

    visited_inodes = set() if count_hardlinks_once else None
    progress = tqdm(total=len(to_scan), unit='items') if pbar_enabled else None

    size = 0
    while to_scan:
        item = to_scan.popleft()
        try:
            if os.path.islink(item):
                try:
                    st = os.lstat(item)
                    size += st.st_size
                    if debug:
                        print(st.st_size, "  ", item, "(symlink)")
                except OSError as e:
                    if debug:
                        print(f"getSize: cannot lstat symlink '{item}': {e}")
                continue

            try:
                is_dir = os.path.isdir(item)
            except OSError as e:
                if debug:
                    print(f"getSize: cannot access '{item}': {e}")
                continue

            if is_dir:
                try:
                    temp = getSpace(item)
                except Exception as e:
                    if debug:
                        print(f"getSize: failed to getSpace for '{item}': {e}")
                    continue
                new_folders = [os.path.join(item, folder) for folder in temp[1]]
                new_files = [os.path.join(item, file) for file in temp[2]]
                to_scan.extend(new_folders)
                to_scan.extend(new_files)
                if progress is not None:
                    added = len(new_folders) + len(new_files)
                    if added:
                        try:
                            progress.total = (progress.total or 0) + added
                            progress.refresh()
                        except Exception:
                            pass
            else:
                try:
                    st = os.stat(item, follow_symlinks=False)
                except OSError as e:
                    if debug:
                        print(f"getSize: cannot stat file '{item}': {e}")
                    continue

                if visited_inodes is not None:
                    inode_key = (st.st_dev, st.st_ino)
                    if inode_key in visited_inodes:
                        if debug:
                            print("skip hardlink duplicate  ", item)
                        continue
                    visited_inodes.add(inode_key)

                file_size = st.st_size
                if debug:
                    print(file_size, "  ", item)
                size += file_size
        except Exception as e:
            if debug:
                print(f"getSize: unexpected error with '{item}': {e}")
            continue
        finally:
            if progress is not None:
                try:
                    progress.update(1)
                except Exception:
                    pass

    if progress is not None:
        try:
            progress.close()
        except Exception:
            pass

    return size


def getFolderSpace(path = "/home/yehors/tspace"):
    path = _normalize_path(path)
    try:
        return getSize(getSpace(path), False, True)
    except Exception as e:
        print(f"getFolderSpace: error scanning '{path}': {e}")
        return -1

# size = getFolderSpace()
# print(humanize.naturalsize(size))