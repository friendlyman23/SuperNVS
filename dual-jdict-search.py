import xml.sax
from typing import Generator
import os



class EntryFoundException(Exception):
    pass

class EntryHandler(xml.sax.ContentHandler):
    def __init__(self, searched_words: list):
        super().__init__()
        self.current_element = None
        self.entries_list = []
        self.matched_chars = []
        self.keb_content = None
        self.keb_added = False
        self.found_match = False
        self.reb_added = False
        self.reb_content = None
        self.gloss_added = False
        self.gloss_content = None
        self.split_word_list = self.split_searched_words(searched_words)

    def startElement(self, name, attrs):
        if name == "entry":
            self.found_match = False
            self.keb_added = False
            self.matched_chars = []
            self.reb_added = False
            self.reb_content = None
            self.gloss_added = False
            self.gloss_content = None
            self.current_element = None
        if name == "keb":
            if not self.found_match:
                self.current_element = "keb"
        if name == "reb":
            if not self.reb_added:
                self.current_element = "reb"
        if name == "gloss":
            if not self.gloss_added:
                self.current_element = "gloss"

# to do: why does initial 捨て猫　get replaced by 捨猫 after found has been set to true

    def characters(self, content):
        if content != "\n":
            if self.current_element == "keb":
                    gen = (x for x in self.split_word_list)
                    if self.find_char_matches(gen, content):
                        self.found_match = True
                        self.keb_content = content
            if self.current_element == "reb":
                if not self.reb_added:
                    if content != "\n":
                        self.reb_content = content
                        self.reb_added = True
            if self.current_element == "gloss":
                if not self.gloss_added:
                    if content != "\n":
                        self.gloss_content = content
                        self.gloss_added = True

    def endElement(self, name):
        if name == "entry":
            if self.found_match:
                self.entries_list.append({"Word": self.keb_content, "Reading": self.reb_content, "Definition": self.gloss_content})
    
    def split_searched_words(self, words: list) -> list:
        """
        takes a list of words and returns a 2D list where each element is a list comprising the kanji used in each input word
        """
        split_list = []
        for word in words:
            split_list.append(list(word))
        return split_list
    
    def get_matched_entries(self) -> list:
        return self.entries_list
    
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

def get_fullwidth_characters(word: str) -> str:
    """
    takes a string of half-width characters and returns a string of full-width equivalents
    """
    split_word = list(word)
    full_width_word = "".join(chr(0xFEE0 + ord(character)) for character in split_word)
    return full_width_word

current_directory = os.path.dirname(__file__)
file_path = os.path.join(current_directory, 'JMdict_e_examp.xml')
searched_words = ['精神', '鋭']
handler = EntryHandler(searched_words)
parser = xml.sax.make_parser()
parser.setContentHandler(handler)

with open(file_path, 'r', encoding='utf8') as f:
    parser.parse(f)

matched_entries = handler.get_matched_entries()

if not matched_entries:
    print("No matches found.")
else:
    titles = [get_fullwidth_characters(word) for word in ["Word", "Reading", "Definition"]]
    format_specifier = f"{chr(0x3000)}<20"

    print(f"{titles[0]:{format_specifier}}{titles[1]:{format_specifier}}{titles[2]:{format_specifier}}")
    for entry in matched_entries:
        print(f"{entry['Word']:{format_specifier}}{entry['Reading']:{format_specifier}}{entry['Definition']:{format_specifier}}")

