from    src.qabot.ingest.loader    import DocumentLoader
from    src.qabot.helpers.config   import Config
from    src.qabot.ingest.chunker   import Chunker
from    src.qabot.indexer          import Indexer


def main():
    """
    This script used to rebuild index
    """
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