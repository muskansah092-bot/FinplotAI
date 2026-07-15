import pandas as pd
import pdfplumber
from pathlib import Path
import PyPDF2
import cv2
import easyocr


import pandas as pd
import pdfplumber
from pathlib import Path
import PyPDF2
import cv2
import easyocr


class StatementExtractor:
    """
    Extract raw text from different financial statement formats.

    This class DOES NOT perform transaction parsing.

    Every extractor returns a single raw text string.

    Agent 1 LLM will later convert this raw text into
    structured JSON.
    """

    def __init__(self, file_path=None, file_type=None, manual_data=None):
        self.file_path = Path(file_path) if file_path else None
        self.file_type = file_type
        self.manual_data = manual_data

    def extract(self):

        if self.file_type == "csv":
            return self._extract_csv()

        elif self.file_type == "excel":
            return self._extract_excel()

        elif self.file_type == "manual":
            return self._extract_manual()

        elif self.file_type == "pdf":
            return self._extract_pdf()

        elif self.file_type == "image":
            return self._extract_image()

        else:
            raise ValueError(f"Unsupported file type: {self.file_type}")

    # ---------------------------------------------------
    # CSV
    # ---------------------------------------------------

    def _extract_csv(self):

        df = pd.read_csv(self.file_path)

        return df.to_csv(index=False)

    # ---------------------------------------------------
    # Excel
    # ---------------------------------------------------

    def _extract_excel(self):

        df = pd.read_excel(self.file_path)

        return df.to_csv(index=False)

    # ---------------------------------------------------
    # Manual
    # ---------------------------------------------------

    def _extract_manual(self):

        if self.manual_data is None:
            raise ValueError("Manual data cannot be None.")

        if isinstance(self.manual_data, list):

            return "\n".join(
                [str(item) for item in self.manual_data]
            )

        return str(self.manual_data)

    # ---------------------------------------------------
    # PDF
    # ---------------------------------------------------

    def _extract_pdf(self):
        """
        Extract raw text from PDF.

        Priority:
        1. pdfplumber
        2. PyPDF2 fallback
        """

        text = ""

        try:

            with pdfplumber.open(self.file_path) as pdf:

                for page in pdf.pages:

                    page_text = page.extract_text()

                    if page_text:
                        text += page_text + "\n"

            if text.strip():
                return self._clean_text(text)

        except Exception as e:

            print(f"pdfplumber failed: {e}")

        print("Using PyPDF2 fallback...")

        text = ""

        try:

            with open(self.file_path, "rb") as file:

                reader = PyPDF2.PdfReader(file)

                for page in reader.pages:

                    page_text = page.extract_text()

                    if page_text:
                        text += page_text + "\n"

        except Exception as e:

            raise RuntimeError(f"PyPDF2 failed: {e}")

        return self._clean_text(text)

    # ---------------------------------------------------
    # IMAGE
    # ---------------------------------------------------

    def _extract_image(self):
        """
        Extract raw text from image using OCR.
        """

        image = cv2.imread(str(self.file_path))

        if image is None:
            raise ValueError(f"Unable to open image: {self.file_path}")

        reader = easyocr.Reader(["en"], gpu=False)

        results = reader.readtext(image, detail=0)

        text = "\n".join(results)

        return self._clean_text(text)

    # ---------------------------------------------------
    # Helpers
    # ---------------------------------------------------

    def _clean_text(self, text):
        """
        Normalize extracted text while preserving line breaks.
        """

        cleaned_lines = []

        for line in text.splitlines():

            line = " ".join(line.split())

            if line:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)