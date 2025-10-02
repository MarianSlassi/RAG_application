# script for chunking and indexating files
from src  import DocumentLoader
from src  import Config
from src  import Chunker
from src  import Indexer

def main():
    config = Config()
    document_loader = DocumentLoader(config = config)
    files_paths = document_loader.find_files() 
    testing_on_all_files = document_loader.load_files(files = files_paths)
    chunker = Chunker()
    chunks = chunker.documents_to_chunks(testing_on_all_files) 
    indexer = Indexer()
    indexer.build_index(chunks)


if __name__ == '__main__':
    main()