import xml.sax
from typing import Generator, Union
import os



class EntryFoundException(Exception):
    pass

class EntryHandler(xml.sax.ContentHandler):
    def __init__(self, searched_words: list):
        super().__init__()
        self.search_words = searched_words
        self.current_element = None
        self.keb_content = None
        self.reb_content = None
        self.gloss_content = None
        self.entries_list = []
        self.entry = {}
        self.matched_chars = []
        self.found_word = False
        self.reb_added = False
        self.gloss_added = False
        self.split_word_list = self.split_searched_words(searched_words)

    def startElement(self, name, attrs):
        self.current_element = name

    def characters(self, content):
        if self.current_element == 'keb':
            self.keb_content = content
        if self.found_word:
            if self.current_element == 'reb':
                self.reb_content = content
            if self.current_element == 'gloss':
                self.gloss_content = content

    def endElement(self, name):
        if name == 'keb':
            self.found_word = False
            gen = (x for x in self.split_word_list)
            self.found_word = self.find_char_matches(gen, self.keb_content)
        if self.found_word:
            if name == 'reb':
                self.entry['reading'] = self.reb_content
                self.reb_added = True
            if name == 'gloss':
                self.entry['definition'] = self.gloss_content
                self.gloss_added = True
            if self.reb_added and self.gloss_added:
                print("Found matching word!")
                self.entries_list.append(self.entry)

    def get_matched_entries(self):
        return self.entries_list
    
    @staticmethod
    def get_fullwidth_characters(word: str) -> str:
        """
        takes a string of half-width characters and returns a string of full-width equivalents
        """
        split_word = [char for char in word]
        full_width_word = "".join(chr(0xFEE0 + ord(character)) for character in split_word)
        return full_width_word
    
    def split_searched_words(self, words: list) -> list:
        """
        takes a list of words and returns a 2D list where each element is a list comprising the kanji used in the input words
        """
        split_list = []
        for word in words:
            split_list.append([char for char in word])
        return split_list
    
    def find_char_matches(self, the_gen: Generator, current_keb: str) -> bool:
        """
        1. yields a list comprising the kanji in one of the searched terms
        2. iterates through the yielded list, checking each kanji to see if it is inside the current keb node
        3. if a kanji's characters are  not found in keb, returns False
        4. if the generator exhausts, a match has been found; returns True
        """
        try:
            while True:
                found_char_flag = False
                list_for_current_searched_word = next(the_gen)
                for char in list_for_current_searched_word:
                    if char in current_keb:
                        found_char_flag = True
                        break
                if found_char_flag:
                    continue
                else:
                    return False  
        except StopIteration:
            return True


# Example usage:
# Get the directory of the current script
current_directory = os.path.dirname(__file__)
file_path = os.path.join(current_directory, 'dictionary_entry_example.xml')
searched_words = ['政治', '情熱']
handler = EntryHandler(searched_words)
parser = xml.sax.make_parser()
parser.setContentHandler(handler)

parser.parse(open(file_path, 'r', encoding='utf8'))
matched_entries = handler.get_matched_entries()

if not matched_entries:
    print("No matches found.")
else:
    titles = [EntryHandler.get_fullwidth_characters(word) for word in ["Word", "Reading", "Definition"]]
    format_specifier = f"{chr(0x3000)}<20"

    print(f"{titles[0]:{format_specifier}}{titles[1]:{format_specifier}}{titles[2]:{format_specifier}}")
    for entry in matched_entries:
        print(f"{entry['word']:{format_specifier}}{entry['reading']:{format_specifier}}{entry['definition']:{format_specifier}}")

