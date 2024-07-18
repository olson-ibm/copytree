import os
import shutil

def copytree(source, destination):
    if not os.path.exists(destination):
        os.makedirs(destination)
        shutil.copystat(source, destination)
    file_list = os.listdir(source)
    # Have a list of directory objects, now iterate over them.
    for item in file_list:
        source_file = os.path.join(source, item)
        destination_file = os.path.join(destination, item)
        if os.path.isdir(source_file):
            # recursive call for subdirectories
            copytree(source_file, destination_file)
        else:
            # straight copy.
            shutil.copy2(source_file, destination_file)
            