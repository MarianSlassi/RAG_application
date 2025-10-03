from typing import Literal
import re

from transformers import AutoTokenizer

from ..schemas import Document, Chunk, Meta

class Chunker:
    """
    This class takes list[Document] produced by DocumentLoader class and convert them into list[Chunk], where Chunk schema which contains of id, text, and Meta schema.\n
    
    class Chunk(BaseModel):
        id: str = Field(..., regex=r"^[\\w\\-]+_\\d+_$", description="ID in format slug_section_subsection")
        text: str = Field(..., min_length=1, description="Chunk text")
        meta: Meta

    class Meta(BaseModel):
        section_id: int = Field(..., ge=0, description="Section number, non-negative")
        sub_section_id: int = Field(..., ge=0, description="Subsection number, non-negative")
        section_title: str = Field("", max_length=200, description="Section title (can be empty)")
        document_title: str = Field(..., min_length=1, max_length=300, description="Document title")
        path: str = Field(..., regex=r"^data/.+\\.(pdf|md|docx)$", description="Path to file inside the data/ directory") # type: ignore # type: ignore
        tokens: int = Field(..., ge=1, le=2048, description="Number of tokens in the chunk")


    """
    def __init__(self, tokenizer = None, max_length = None):
        """
        Initializing chunker instance, pass tokenizer or use "sentence-transformers/all-MiniLM-L6-v2" as fallback\n
        tokenization object used for further strings tokenization and for checking validity of chunks length\n
        **Maximum context length of all-MiniLM-L6-v2 is 512 tokens!**
        """
        self.tokenizer = tokenizer or AutoTokenizer.from_pretrained(
            "sentence-transformers/all-MiniLM-L6-v2"
        )
        self.context_window = max_length or self.tokenizer.model_max_length
    
    def _count_tokens(self, text: str) -> int:
        """
        This method takes text string and returns number of tokens with tokenizer of this object instance
        Args:
            text(str):
                text to tokenize
        """
        if not self.tokenizer:
            raise RuntimeError("Tokenizer is not defined. Please provide a tokenizer.")
        return len(self.tokenizer.encode(text))
    
    def _split_text(self, document: Document) -> list[str]:
        """
        Splits the text of a single Document into smaller textual chunks based on section headings.

        The method takes a Document instance, reads its text, and uses a regular expression
        to split the text at positions where Markdown-style section titles occur
        (patterns like **Section name**). It returns a list of string fragments, each representing
        a logical chunk of the original document's content. 
        This method implies that originall document will have structure where every heading is bold and separated with double '\\n'. \n Example: \\n\\n\\*\\*Heading\\*\\*\\n\\n

        Args:
            document (Document): The Document object whose text is to be chunked.

        Returns:
            list[Chunk]: A list of Chunk objects created from the split text segments.

        RISKS:: splitting pattern migh split te
        """
        chunks_list = []
        pattern = re.compile(r'\n+\*\*[^*\n]+\*\*\n+')
        text = document.text
        chunks = pattern.split(text)
        for chunk in chunks:
            if chunk:
                chunks_list.append(chunk)
        return chunks_list
    
    def _cut_long_text(self, text: str, overlap_percent: float = 0.10)-> list[str] :
        """
        Splits overly long text into overlapping segments that fit within the model's context window.

        This method takes a text string and splits it into smaller chunks if its token count exceeds
        the tokenizer's maximum context length. The chunks overlap by a proportion specified by
        overlap_percent (default is 10%) to preserve context between segments. If the text length is
        already within the context window, it is returned unchanged as a string.

        Args:
            text (str): The input text to be split if too long.
            overlap_percent (float): The fraction of overlap between consecutive chunks (default 0.10).

        Returns:
            list[str] | str: A list of overlapping text segments if splitting occurs, otherwise the original text string.
        """
        if self._count_tokens(text) <= self.context_window:
            #print('Given text is shorter than desired length, exiting _cut_long_text() method')
            return [text]
        else:
            overlap = self.context_window*overlap_percent
            new_text: list[str] = []
            current_tokens = []
            tokens = self.tokenizer.tokenize(text)
            for number, token in enumerate(tokens):
                current_tokens.append(token)
                if len(current_tokens) >= self.context_window:
                    sequence = self.tokenizer.convert_tokens_to_string(current_tokens)
                    new_text.append(sequence)
                    current_tokens = current_tokens[-overlap:] # returns last {-overlap} tokens, by default last 25 (due to default variable value and default tokenizer)
            if current_tokens:
                sequence = self.tokenizer.convert_tokens_to_string(current_tokens)
                new_text.append(sequence)
            return new_text

    def _merge_short_text(self, sequences : list[str], min_tokens: int = 150) -> list[str]:
        """
        Merges consecutive short text fragments into larger chunks without exceeding the context window.

        This method scans a list of text fragments and tries to merge those whose token count is below 150
        with the next or previous fragment so long as the combined length stays within the tokenizer's
        maximum context window (`self.context_window`). The purpose is to reduce fragmentation of very
        small chunks while respecting the upper token limit of the model.

        TODO: In rare cases a fragment may remain shorter than 150 tokens if neither merging forward
        nor backward is possible without exceeding the maximum context length. Such short fragments
        are currently left as-is.
        """
        current_chunk = ''
        new_sequence = []
        for num, text in enumerate(sequences):
            if self._count_tokens(text) < min_tokens: # Found small string
                if self._count_tokens(current_chunk + text) <= self.context_window : # Could we add it to buffer?
                    current_chunk = current_chunk + '\n' + text
                    continue
                else: # If next str is long, we should save existing buffer to final sequence, if buffer exist
                    if current_chunk:
                        if self._count_tokens(current_chunk) < min_tokens and new_sequence: # What if sequence in buffer too short?
                            prev = new_sequence[-1] + current_chunk 
                            if self._count_tokens(prev) <= self.context_window: # We can add buffer to previous string in parrent list
                                new_sequence[-1] = prev
                                current_chunk = ''
                                continue
                        new_sequence.append(current_chunk)
                        current_chunk = ''
            else: # If not small string then clean buffer and add this string to new sequences list
                new_sequence.append(text)
                current_chunk = ''
        if current_chunk:
            new_sequence.append(current_chunk)
        if len(new_sequence) == 1:
            return new_sequence
        return new_sequence
    
    def _process_split_text(self, sequence: list[str], min_tokens: int = 150)->list[str]:
        """
        Processes a list of text fragments by first cutting overly long segments
        and then merging too short ones to produce balanced chunks.

        The method takes a list of strings, typically produced by _split_text,
        and applies two internal steps in sequence:
        1. _cut_long_text — splits each fragment that exceeds the tokenizer's
           context window into smaller overlapping segments.
        2. _merge_short_text — combines consecutive small fragments (under
           min_tokens, default 150) into larger ones, ensuring each final chunk
           stays within the model's maximum context length.

        Args:
            sequence (list[str]): List of text fragments to normalize.
            min_tokens (int): Minimum desirable token count for a chunk. 
                Currently used only for documentation and readability,
                because the value is hardcoded (150) inside _merge_short_text.

        Returns:
            list[str]: A list of well-sized text chunks ready for further processing.

        Note:
            min_tokens is not actively enforced in this method,
            but kept as an argument for future flexibility.
        """
        new_sequence = []
        for each in sequence:
            temp = self._cut_long_text(each)
            new_sequence.extend(temp)
        new_sequence = self._merge_short_text(sequences = new_sequence, min_tokens = min_tokens)
        return new_sequence
    
    def documents_to_chunks(self, documents: list[Document], min_tokens:int = 150, max_tokens = None) -> list[Chunk]:
        """
        Takes list of Documents objects and iterate among them. For each\
        saves title and path fields. Then call self._split_text() method to split\
        text and get chunks strings list. For each chunk text counts section_id and number of tokens inside.\
        Then assign document_title, path, section_id, tokens number and section title (mocked) to Meta schem,\
        and transfer it with 'id' and text of chunk string to Chunk shem object. 

        Notes:
            'section_title' field mocked with '' for future expansion. 
        """
        self.context_window = max_tokens or self.tokenizer.model_max_length
        if min_tokens >= self.context_window:
            raise ValueError(f'min_tokens argument should be not grater or equal to the context window of tokenizer, current context_window: {self.context_window}')
        chunks_array = []
        for doc in documents:
            document_title, path = None, None
            document_title = doc.title
            path = doc.path
            updated_at = doc.updated_at
            splitted_document_text = self._split_text(document= doc)
            splitted_document_text = self._process_split_text(splitted_document_text, min_tokens=min_tokens)

            for section_id , chunk in enumerate(splitted_document_text):     
                id = document_title + '_' +  str(section_id)
                tokens = self._count_tokens(chunk)

                meta = Meta(document_title = document_title, path=path, section_id=section_id,tokens=tokens, section_title='',updated_at=updated_at)
                chunk_object = Chunk(id = id, text = chunk, meta = meta)
                chunks_array.append(chunk_object)

        return chunks_array
