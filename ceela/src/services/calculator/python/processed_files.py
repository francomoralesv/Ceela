

class ProcessedFiles:
    
    def __init__(self):
        self.processed_files = []

    def add_file(self, file_path):
        if file_path not in self.processed_files:
            self.processed_files.append(file_path)

    def get_processed_files(self):
        return self.processed_files

    def clear_processed_files(self):
        self.processed_files = []