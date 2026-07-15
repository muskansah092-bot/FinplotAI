from pathlib import Path


class StatementParser:
    """
    Detects the type of financial statement.
    It DOES NOT read the file.
    """

    SUPPORTED_TYPES = {
        ".csv": "csv",
        ".xlsx": "excel",
        ".xls": "excel",
        ".pdf": "pdf",
        ".png": "image",
        ".jpg": "image",
        ".jpeg": "image"
    }

    def __init__(self, file_path):
        self.file_path = Path(file_path)

    def parse(self):
        extension = self.file_path.suffix.lower()

        if extension in self.SUPPORTED_TYPES:
            return self.SUPPORTED_TYPES[extension]

        raise ValueError(f"Unsupported file format: {extension}")