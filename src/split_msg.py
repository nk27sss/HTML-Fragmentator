import os
import re
from collections.abc import Generator
from bs4 import BeautifulSoup,Tag

# ловить ошибку
CATCH_ERR = False
# сжимать пробелы
IS_STRIP = False
# делить текст
IS_SPLITTEXT = False
# макс длина
MAX_LEN = 4096
# блочные теги, которые можно открывать и закрывать
BLOCK_TAGS = ['p', 'b', 'strong', 'i', 'ul', 'ol', 'div', 'span']


class FragmentatorException(Exception):
    pass

class FragmentatorHTML():
    def __init__(self, html, max_len=150, autocompile=True, block_tags=BLOCK_TAGS, is_splittext=False, is_strip=False, *args, **kwargs):
        self.raw_html = html
        self.max_len = max_len
        self.block_tags = block_tags
        self.is_splittext = is_splittext
        self.is_strip = is_strip
        
        self.atoms = []
        self.fragments = []
        self.start_pos = 0
        self.curr_pos = 0
        self.current_atoms = []
        self.current_fragment_text = ""
        
        if autocompile:
            self.compile()

    
    def compile(self):
        soup = BeautifulSoup(self.raw_html, "html.parser")
        self.atoms = self._frag_atoms(soup)
        
        
    def _get_tagname(self, tagname: str) -> str:
        match = re.match(r'<\/?(\w+)', tagname)
        if not match:
            return None
        return match.group(1)

    def _opentags2closetags(self, opentags: list):
        result=[]
        for t in opentags[::-1]:
            tagname = self._get_tagname(t)
            result.append(f'</{tagname}>')
        return result
        

    def _build_html(self, atoms: list) -> str:
        html = ""
        if not atoms:
            return None

        html += ''.join(atoms[0][1])
        
        for atom, parents in atoms:
            html += atom
            
        html += ''.join(self._opentags2closetags(parents))

        return html

        
        
    def _frag_atoms(self, elem:BeautifulSoup|Tag|str, parent_tags=[]) -> list|None:
        if isinstance(elem, BeautifulSoup):
            # если элемент - документ
            childrens = []
            for child in elem:
                c = self._frag_atoms(child, parent_tags)
                if c is not None:
                    childrens.extend(c)
            return childrens
        
        elif tag_name := elem.name:
            # Если элемент - тег
            result = []
            current_tag = str(elem).strip().split('>')[0] + '>'
            
            if elem.isSelfClosing:
                return [(current_tag, parent_tags[:])]
            
            if tag_name not in self.block_tags:
                return [(str(elem), parent_tags[:])]
            
            # открывающий тег
            result.append((current_tag, parent_tags[:]))
            parent_tags.append(current_tag)

            for child in elem.children:
                atoms=self._frag_atoms(child, parent_tags)
                if atoms is not None:
                    result.extend(atoms)

            # закрывающий тег
            parent_tags.pop()
            result.append((f'</{tag_name}>', parent_tags[:]))

            return result
            
        elif isinstance(elem, str):
            # Если элемент - текст
            if self.is_splittext:
                if self.is_strip:
                    darr = [match.group(0) for match in re.finditer(r'(\s+)|([^<>\s]+)', str(elem).strip())]
                else:
                    darr = [match.group(0) for match in re.finditer(r'(\s+)|([^<>\s]+)', str(elem))]
                    
                return [(d, parent_tags[:]) for d in darr]
            else:
                
                if self.is_strip:
                    txt = str(elem).strip()
                    if txt:
                        return [(txt, parent_tags[:])]
                else:
                    return [(str(elem), parent_tags[:])]
                
            
        return None
    
    
    def get_fragments(self) -> Generator[str]:
        self.start_pos=0
        self.curr_pos=0
        self.prev_pos=0
        
        if not self.atoms:
            raise FragmentatorException("Parsing is empty!")
        
        while True:
            atoms = self.atoms[self.start_pos : self.curr_pos+1]

            if atoms is None:
                raise FragmentatorException("Fragment is empty!")
                        
            fragment = self._build_html(atoms)
            
            
            if len(fragment) >= self.max_len:
                # набрали с перебором, возвращаем предпоследн.
                if not self.current_fragment_text:
                    raise FragmentatorException(f"Failed to create fragment shorter than max_len({self.max_len})!")
                
                self.prev_pos = self.start_pos
                self.start_pos = self.curr_pos
                self.fragments.append(self.current_fragment_text)
                
                yield self.current_fragment_text
                self.current_fragment_text=""

            elif self.curr_pos>=len(self.atoms):
                # конец
                self.current_atoms = atoms
                self.current_fragment_text = fragment
                    
                self.prev_pos = self.start_pos
                self.start_pos = self.curr_pos
                self.fragments.append(fragment)
                
                yield fragment
                break
            
            else:
                # если последний тег открывающий
                if len(atoms)>0 and atoms[-1][0].startswith('<') and not atoms[-1][0].startswith('</'):
                    self.curr_pos+=1
                    continue
                
                # набираем больше
                self.current_atoms = atoms
                self.current_fragment_text = fragment

            self.curr_pos+=1
            

    def get_fragments_list(self):
        return list(self.get_fragments())
    



def split_message(source: str, max_len=MAX_LEN, is_splittext=IS_SPLITTEXT, is_strip=IS_STRIP) -> Generator[str]:
    """Splits the original message (`source`) into fragments of the specified length
    (`max_len`)."""
    
    if not source:
        raise Exception('Source is ""!')
    if not os.path.exists(source) and not os.path.isfile(source):
        raise Exception(f'File "{source}" not found!')
    
    with open(source, "r", encoding="utf-8") as f:
        source_html = f.read()
    
    fg = FragmentatorHTML(source_html, max_len, is_splittext=is_splittext, is_strip=is_strip)
    return fg.get_fragments()
    


def split_message_print(source: str, max_len:int=MAX_LEN, catch_err:int=0, is_splittext=IS_SPLITTEXT, is_strip=IS_STRIP):
    """added info mode, no crashes"""
    print(f"\033[94m### split_message({max_len=}, {source=})\033[0m")

    try:
        for i, fragment in enumerate(split_message(source, max_len, is_splittext=is_splittext, is_strip=is_strip), start=1):
            print(f"\033[94m-- fragment #{i}: {len(fragment)} chars --\033[0m")
            print(fragment)

    except FragmentatorException as e:
        if catch_err:
            print(f"\033[91mFragmentatorException: {e}\033[0m")
            return 1
        else:
            raise e
    
    print(f"\033[94mtotal fragments: {i}\033[0m")
    return 0

if __name__ == "__main__":
    
    import click
    
    @click.command()
    @click.option('-e', '--catch-err', is_flag=True, default=CATCH_ERR, help='ловить ошибку')
    @click.option('-s', '--is-strip', is_flag=True, default=IS_STRIP, help='сжимать пробелы')
    @click.option('-t', '--is-splittext', is_flag=True, default=IS_SPLITTEXT, help='делить текст')
    @click.option('-l', '--max-len', type=int, default=MAX_LEN, help='MAX_LEN')
    @click.argument('source', required=False)
    def split_message_args(source: str, max_len=MAX_LEN, catch_err=CATCH_ERR, is_strip=IS_STRIP, is_splittext=IS_SPLITTEXT):
        if not source:
            source = click.prompt('Enter source file', type=str)
        return split_message_print(source, max_len, catch_err=catch_err, is_strip=is_strip, is_splittext=is_splittext)
        
    c=split_message_args()
    exit(c)



