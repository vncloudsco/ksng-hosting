import os

def find_sub(dirs=None, name=None):
    """
    find subfolder
    :param dirs:
    :param name:
    :return:
    """
    folders = os.walk(dirs)
    list_folder = []
    for folder in folders:
        if name == '*' or name is None:
            list_folder.append(folder[0])
        elif name == folder[0].split('/')[-1]:
            list_folder.append(folder[0])
    return list_folder


def find_file(dirs=None, name=None):
    """
    find sub file
    :param dirs:
    :param name:
    :return:
    """
    list_file = []
    for dirpath, subdirs, files in os.walk(dirs):
        for file in files:
            if file == name:
                list_file.append(os.path.join(dirpath, file))
            elif file == None or file == "*":
                list_file.append(os.path.join(dirpath, file))
    return list_file
