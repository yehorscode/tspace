import os
from tqdm import tqdm
from collections import deque
from concurrent.futures import CancelledError
import logging
logging.basicConfig(filename='scan.log', format='%(asctime)s %(levelname)s:%(message)s')

def _normalize_path(path: str) -> str:
    return os.path.abspath(os.path.expandvars(os.path.expanduser(path)))


def getSpaceFile(path: str) -> int:
    path = _normalize_path(path)
    try:
        return os.path.getsize(path)
    except OSError as e:
        logging.error(f"getSpaceFile: cannot space out '{path}': {e}")
        return 0


def getSpace(path: str = "~/Desktop", debug: bool = False):
    path = _normalize_path(path)
    try:
        root, dirs, files = next(os.walk(path))
    except (OSError, StopIteration) as e:
        if debug:
            logging.error(f"getSpace: cannot walk '{path}': {e}")
        return [path, [], []]
    if debug:
        logging.debug(f"[0]: {root}")
        logging.debug(f"[1]: {dirs}")
        logging.debug(f"[2]: {files}")
    return [root, dirs, files]


def getSize(
    path_tuple,
    debug: bool = False,
    pbar_enabled: bool = False,
    count_hardlinks_once: bool = True,
    cancel_event=None
) -> int:
    base_path, folders, files = path_tuple
    to_scan = deque(os.path.join(base_path, f) for f in folders)
    to_scan.extend(os.path.join(base_path, f) for f in files)

    visited_inodes = set() if count_hardlinks_once else None
    progress = tqdm(total=len(to_scan), unit='items') if pbar_enabled else None

    size = 0
    while to_scan:
        if cancel_event and cancel_event.is_set():
            raise CancelledError()
        item = to_scan.popleft()
        try:
            if os.path.islink(item):
                try:
                    st = os.lstat(item)
                    size += st.st_size
                    if debug:
                        logging.debug(f"{st.st_size}  {item} (symlink)")
                except OSError as e:
                    if debug:
                        logging.error(f"getSize: cannot lstat symlink '{item}': {e}")
                continue

            try:
                is_dir = os.path.isdir(item)
            except OSError as e:
                if debug:
                    logging.warning(f"getSize: cannot access '{item}': {e}")
                continue

            if is_dir:
                if cancel_event and cancel_event.is_set():
                    raise CancelledError()
                try:
                    temp = getSpace(item, debug=debug)
                except Exception as e:
                    if debug:
                        logging.error(f"getSize: failed to getSpace for '{item}': {e}")
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
                        logging.debug(f"getSize: cannot stat file '{item}': {e}")
                    continue

                if visited_inodes is not None:
                    inode_key = (st.st_dev, st.st_ino)
                    if inode_key in visited_inodes:
                        if debug:
                            logging.debug(f"skip hardlink duplicate  {item}")
                        continue
                    visited_inodes.add(inode_key)

                size += st.st_size
                if debug:
                    logging.debug(f"{st.st_size}  {item}")
        except Exception as e:
            if debug:
                logging.error(f"getSize: unexpected error with '{item}': {e}")
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

def getFolderSpace(
    path: str = "~/Desktop",
    pbar_enabled: bool = False,
    debug: bool = True,
    cancel_event=None
) -> int:
    path = _normalize_path(path)
    logging.error("test")
    try:
        return getSize(
            getSpace(path, debug=debug),
            debug=debug,
            pbar_enabled=pbar_enabled,
            cancel_event=cancel_event
        )
    except CancelledError:
        raise
    except Exception as e:
        logging.error(f"getFolderSpace: error scanning '{path}': {e}")
        return -1