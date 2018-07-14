import re

from khard import khard, config
from deoplete.source.base import Base

COLON_PATTERN = re.compile(':\s?')
COMMA_PATTERN = re.compile('.+,\s?')
HEADER_PATTERN = re.compile('^(Bcc|Cc|From|Reply-To|To):(\s?|.+,\s?)')


def remove_accents(string):
    string = re.sub(u"[àáâãäå]", 'a', string)
    string = re.sub(u"[èéêë]", 'e', string)
    string = re.sub(u"[ìíîï]", 'i', string)
    string = re.sub(u"[òóôõö]", 'o', string)
    string = re.sub(u"[ùúûü]", 'u', string)
    string = re.sub(u"[ýÿ]", 'y', string)
    string = re.sub(u"[ÀÁÂÃÄÅ]", 'A', string)
    string = re.sub(u"[ÈÉÊË]", 'E', string)
    string = re.sub(u"[ÌÍÎÏ]", 'I', string)
    string = re.sub(u"[ÒÓÔÕÖ]", 'O', string)
    string = re.sub(u"[ÙÚÛÜ]", 'U', string)
    string = re.sub(u"[ÝŸ]", 'Y', string)

    return string


class Source(Base):
    def __init__(self, vim):
        super().__init__(vim)

        self.name = 'khard'
        self.mark = '[khard]'
        self.min_pattern_length = 2
        self.filetypes = ['mail']

        self.__cache = []

    def get_complete_position(self, context):
        colon = COLON_PATTERN.search(context['input'])
        comma = COMMA_PATTERN.search(context['input'])
        return max(colon.end() if colon is not None else -1,
                   comma.end() if comma is not None else -1)

    def gather_candidates(self, context):
        if HEADER_PATTERN.search(context['input']):
            if not self.__cache:
                self.__fill_cache()
            return self.__cache

    def __fill_cache(self):
        khard_config = config.Config()
        abooks = []
        for addressbook in khard_config.get_all_address_books():
            abooks.append(
                khard_config.get_address_book(addressbook.name, None))

        for vcard in khard.get_contacts(abooks, '', 'name', False, False):
            for type, email_list in vcard.get_email_addresses().items():
                for email in email_list:
                    self.__cache.append({
                        'word':
                        "{0} <{1}>".format(
                            remove_accents(vcard.get_first_name_last_name()),
                            email)
                    })
