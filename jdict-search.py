import xml.sax

class EntryFoundException(Exception):
    pass

class EntryHandler(xml.sax.ContentHandler):
    def __init__(self, search_word):
        super().__init__()
        self.search_word = search_word
        self.current_element = None
        self.keb_content = None
        self.reb_content = None
        self.gloss_content = None
        self.entry = {}
        self.found = False
        self.reb_added = False
        self.gloss_added = False

    def startElement(self, name, attrs):
        self.current_element = name

    def characters(self, content):
        if self.current_element == 'keb':
            self.keb_content = content
        if self.found is True:
            if self.current_element == 'reb':
                self.reb_content = content
            if self.current_element == 'gloss':
                self.gloss_content = content
                self.gloss_added = True

    def endElement(self, name):
        if name == 'keb':
            # Check if the keb content matches the search word
                if self.keb_content == self.search_word:
                    if self.found is not True:
                        self.found = True
                        self.entry['word'] = self.keb_content
        if self.found is True:
            if name == 'reb':
                self.entry['reading'] = self.reb_content
                self.reb_added = True
            if name == 'gloss':
                self.entry['definition'] = self.gloss_content
                self.gloss_added = True
            if self.reb_added and self.gloss_added:
                raise EntryFoundException()

    def get_matched_entries(self):
        return self.entry
    
    @staticmethod
    def get_fullwidth_characters(word: str) -> str:
        """
        takes a string of half-width characters and returns a string of full-width equivalents
        """
        split_word = [char for char in word]
        full_width_word = "".join(chr(0xFEE0 + ord(character)) for character in split_word)
        return full_width_word

# Example usage:
search_word = '地球温暖化'
handler = EntryHandler(search_word)
parser = xml.sax.make_parser()
parser.setContentHandler(handler)
try:
    parser.parse(open(r'JMdict_e_examp.xml', encoding='utf-8'))
except EntryFoundException:
    matched_entries = handler.get_matched_entries()
    titles = [EntryHandler.get_fullwidth_characters(word) for word in ["Word", "Reading", "Definition"]]
    format_specifier = f"{chr(0x3000)}<20"
    
    print(f"{titles[0]:{format_specifier}}{titles[1]:{format_specifier}}{titles[2]:{format_specifier}}")
    print(f"{matched_entries['word']:{format_specifier}}{matched_entries['reading']:{format_specifier}}{matched_entries['definition']:{format_specifier}}")

    # matched_entries = handler.get_matched_entries()
    # titles = [EntryHandler.get_fullwidth_characters(word) for word in ["Word", "Reading", "Definition"]]

    # # Construct format string dynamically
    # format_string = '{:<20}' * len(titles)

    # print(format_string.format(*titles))