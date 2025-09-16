from src.helpers import Config

class DocumentLoader():
    def __init__(self, path: str = None):
        self.path = path

    def load(self):
        if not self.path:
            raise ValueError("Path must be provided to load documents.")
        # Logic to load documents from the specified path
        with open(self.path, 'r') as file:
            documents = file.readlines()
        return documents