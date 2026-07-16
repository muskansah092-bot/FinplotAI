import json

def load_json(file_path):
    """
    Reads a JSON file from disk and returns it as a Python dictionary.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def save_json(data, file_path):
    """
    Writes a Python dictionary to disk as a JSON file.
    Uses indent=4 so the output file is human-readable.
    """
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def read_text_file(file_path):
    """
    Reads a plain text file (like our knowledge files) and
    returns its full content as a single string.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content