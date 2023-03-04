
from typing import Dict, Tuple, Union, List
from .xml_tag import Xml_Tag
import time

class XmlParser:

    @staticmethod 
    def determine_xml_encoding(file_path:str) -> str:
        with open(file_path, 'rb') as file:
            line = str(file.readline())
        start_word = line.find('encoding=')
        if start_word == -1:
            return 'utf-8'
        enc_pos = start_word + 10
        enc_end = line.find('"', enc_pos)
        encoding = line[enc_pos:enc_end]
        return encoding

    @staticmethod
    def get_close_tag(name: str) -> str:
        return "</" + name + ">"
    
    def taste_another_seqs(self, text, pos) -> Union[None, Tuple[str, str]]:
        '''
        pos = position of '&'
        if can't determine code by sims seq, returns None
        else returns sims seq and simbol, should be replaced
        ex: text = 'abc &amp;' -> ('amp', '&')
        ex2: text = 'abc &seq;' -> None
        use that for non-xml sequences, like html codes
        '''
        return None
    
    def decode_unicode_simbols(self,text: str) -> str:
        pos = 0
        while pos != -1:
            pos = text.find('&', pos)
            if pos != -1:
                if text[pos+1:pos+4] == 'amp':
                    text = text.replace('&amp;', '&')
                    pos += 1
                elif text[pos+1:pos+3] == 'lt':
                    text = text.replace('&lt;', '<')
                    pos += 1
                elif text[pos+1:pos+3] == 'gt':
                    text = text.replace('&gt;', '>')
                    pos += 1
                elif text[pos+1:pos+5] == 'quot':
                    text = text.replace('&quot;', '"')
                    pos += 1
                elif text[pos+1:pos+5] == 'apos':
                    text = text.replace('&apos;', "'")
                    pos += 1
                elif text[pos+1] == '#':
                    # decimal or hex code
                    code_start = pos + 1
                    while (text[code_start] != ';') and code_start < len(text):
                        code_start += 1
                    if code_start == len(text):
                        pos += 1
                    else:
                        code = text[pos+2:code_start]
                        base = 10
                        if code[0] == 'x':
                            base = 16
                            code = code[1:]
                        code = int(code, base=base)
                        text = text.replace(text[pos:code_start+1], chr(code))
                        pos += 1
                else:
                    substitution = self.taste_another_seqs(text, pos)
                    if not substitution:
                        print('unknown code cheme:', text[pos:pos+10])
                        pos += 1
                    else:
                        repl_str = '&' + substitution[0] + ';'
                        text = text.replace(repl_str, substitution[1])
                        pos += 1
        return text

    def find_comment_end_position(self, text, comment_pos):
        '''returns pos of simbol after "-->" '''
        comment_pos += 4
        # go through <!--
        while comment_pos != len(text):
            comment_pos += 1
            if self.is_comment_start(text, comment_pos):
                comment_pos = self.find_comment_end_position(text, comment_pos) - 1
            if text[comment_pos:comment_pos+3] == '-->':
                return comment_pos + 3
        return len(text)

    def remove_comments_from_string(self, text: str) -> str:
        pos = 0
        while pos != -1:
            pos = text.find('<!--', pos)
            if pos != -1:
                end = self.find_comment_end_position(text, pos)
                text = text[:pos] + text[end:]
        return text

    def find_simbols_outside_comments(self, sims: List[str] , text:str, pos:int) -> int:
        ''' returns position of any simbol in [text], given in [sims], starting with position [pos]'''
        while (pos < len(text)) and (not text[pos] in sims):
            if self.is_comment_start(text, pos):
                pos = self.find_comment_end_position(text, pos) - 1
            pos += 1
        return pos

    def is_comment_start(self, text, pos):
        return text[pos:pos + 4] == '<!--'

    def get_tag_arguments(self,tag:str) -> Tuple[str, Dict[str, str]]:
        attr = {}
        space_pos = tag.find(' ')
        if space_pos == -1:
            if tag[-1] == '/':
                return tag[:-1], attr
            return tag, attr
        if tag[space_pos-1] == '/':
            real_tag = tag[:space_pos-1]
        else:
            real_tag = tag[:space_pos]
        pos = space_pos + 1
        while pos < len(tag):
            #time.sleep(1)
            eq_pos = pos
            while (eq_pos < len(tag)) and tag[eq_pos] != '=':
                eq_pos += 1
                if tag[eq_pos:eq_pos + 4] == '<!--':
                    comment_end = self.find_comment_end_position(tag, eq_pos)
                    pos = comment_end
                    eq_pos = comment_end
            if eq_pos >= len(tag):
                pos = len(tag) + 10
            else:
                name = tag[pos:eq_pos].strip()
                val_start = eq_pos + 1

                while val_start < len(tag) and tag[val_start] == ' ':
                    val_start += 1
                    if tag[val_start:val_start+4]== '<!--':
                        comment_end = self.find_comment_end_position(tag, val_start)
                        val_start = comment_end
                
                if tag[val_start] in ['"', '\'']:
                    val_end = tag.find(tag[val_start], val_start+1)
                    if val_end == -1: val_end = len(tag)
                    value = tag[val_start+1:val_end]
                else:
                    # without string definition
                    val_end = tag.find(' ', val_start)
                    if val_end == -1: val_end = len(tag)
                    value = tag[val_start:val_end]

                pos = val_end + 1
                attr[name] = self.decode_unicode_simbols(value)
        return real_tag, attr

    def is_self_closed(self, tag: str) -> bool:
        if tag == '': return False
        pos = -1
        while (tag[pos].isspace()) and (pos > -len(tag)):
            pos -= 1
        if pos == -len(tag): return False
        return tag[-1] == '/'

    def parce_string(self, string:str, pos:int) -> Tuple[Xml_Tag, int]:
        root = Xml_Tag()
        if string[pos] != '<':
            pos = self.find_simbols_outside_comments(['<'], string, pos)
        close = self.find_simbols_outside_comments(['>'], string, pos)

        tag_txt = string[pos+1:close]
        self_closed = self.is_self_closed(tag_txt)
        # divide tag and xml arguments here!!
        root.tag, root.attr = self.get_tag_arguments(tag_txt)
        if self_closed:
            return root, close + 1
        pos = close + 1
        closed = False
        while (not closed) and (pos < len(string)):
            content_start = pos
            pos = self.find_simbols_outside_comments(['<'], string, content_start)
            if (pos >= len(string)): return root, pos
            plain_text = string[content_start:pos]
            if plain_text != '' and not plain_text.isspace():
                plain_tag = Xml_Tag()
                plain_tag.tag = "plain_text"
                plain_text = self.remove_comments_from_string(plain_text)
                plain_tag.text = self.decode_unicode_simbols(plain_text)
                root.append(plain_tag)
            # work '<'
            if pos + 1 == len(string):
                closed = True
            if string[pos+1] == '/':
                closed = True
                close_pos = self.find_simbols_outside_comments(['>'], string, pos+1)
                pos = close_pos + 1
            #it is internal tag
            if not closed:
                if self.is_comment_start(string, pos):
                    pos = self.find_comment_end_position(string, pos)
                else:
                    sub_tag, pos = self.parce_string(string, pos)
                    root.append(sub_tag)
        return root, pos

    def parce_xml_file(self, full_path: str) -> Xml_Tag:
        try:
            encoding = self.determine_xml_encoding(full_path)
            with open(full_path, mode="r", encoding=encoding) as file:
                content = file.read()
                if not '<?hml' in content[:20]:
                    pos = 0
                else:
                    pos = content.find('>') + 1
                return self.parce_string(content, pos)[0]
        except Exception as e:
            print(e)
            return Xml_Tag()


            







