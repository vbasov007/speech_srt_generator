import os
from mylogger import mylog
import time

def remove_files_after_completion(file_paths: list, delay: int = 600, repeat: int = 10):
    not_deleted = file_paths.copy()
    for i in range(repeat):
        if len(not_deleted) == 0:
            break
        time.sleep(delay)
        remaining = not_deleted.copy()
        for f in remaining:
            try:
                os.remove(f)
            except Exception as e:
                mylog.error(f'Failed to remove {f}: {e}')
            else:
                mylog.info(f'Removed {f}')
                not_deleted.remove(f)