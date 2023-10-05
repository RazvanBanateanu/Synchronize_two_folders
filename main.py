import os
import shutil
import hashlib
import time
import argparse

# Calculate SHA-256 hash of a file
def hash_file(file_path):
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while True:
            data = file.read(65536)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()

def sync_folders(source_folder, replica_folder, log_file):
    global initial_files

    # If replica folder doesn't exist, we create it
    if not os.path.exists(replica_folder):
        os.makedirs(replica_folder)

    source_files = os.listdir(source_folder)
    replica_files = os.listdir(replica_folder)

    # Log file creation or deletion in source folder
    new_files = set(source_files) - initial_files
    deleted_files = initial_files - set(source_files)

    # Check if any files have been created
    if new_files:
        for file in new_files:
            print(f"File {file} has been created in {source_folder}")
            log_file.write(f"File {file} has been created in {source_folder}\n")
    
    if deleted_files:
        for file in deleted_files:
            print(f"File {file} has been deleted in {source_folder}")
            log_file.write(f"File {file} has been deleted in {source_folder}\n")

    # Update the initial_files set with the new list of files
    initial_files = set(source_files)


    # Synchronize files from source to replica
    for file in source_files:
        source_path = os.path.join(source_folder, file)
        replica_path = os.path.join(replica_folder, file)

        # Check if file exists in replica and is the same
        if file in replica_files and hash_file(source_path) == hash_file(replica_path):
            continue

        # Copy the file from source to replica
        shutil.copy2(source_path, replica_path)
        log_file.write(f"File {file} copied in {replica_folder}\n")
        print(f"File {file} copied in {replica_folder}")

    # Remove files from replica that don't exist in source
    for file in replica_files:
        replica_path = os.path.join(replica_folder, file)
        if file not in source_files:
            os.remove(replica_path)
            log_file.write(f"File {file} was removed from {replica_folder}.\n")
            print(f"File {file} was removed from {replica_folder}.")

def main():
    global initial_files

    parser = argparse.ArgumentParser(description="Synchronize two folders")
    parser.add_argument("source_folder", help="Path to the source folder")
    parser.add_argument("replica_folder", help="Path to the replica folder")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")

    args = parser.parse_args()

    initial_files = set(os.listdir(args.source_folder))

    while True:
        with open(args.log_file, "a") as log_file:
            log_file.write(f"\nSynchronization at {time.ctime()}\n")
            print(f"\nSynchronization at {time.ctime()}")
            
            sync_folders(args.source_folder, args.replica_folder, log_file)
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
