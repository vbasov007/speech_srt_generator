import os
import time


def delete_old_files(directory_path, ext_list: list, age_seconds):


    # Get the current time in seconds since the epoch
    current_time = time.time()

    # Iterate over files in the specified directory
    for file_name in os.listdir(directory_path):
        _, file_ext = os.path.splitext(file_name)
        # Create absolute file path
        abs_file_path = os.path.join(directory_path, file_name)

        # Check if this is a file (not a subdirectory)
        if os.path.isfile(abs_file_path):

            # Check if file has the specified extension
            if file_ext in ext_list:
                # Get the file's modification time
                file_mod_time = os.path.getmtime(abs_file_path)

                # If the file is older than specified age_seconds, delete it
                if current_time - file_mod_time > age_seconds:
                    os.remove(abs_file_path)
