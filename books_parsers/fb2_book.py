from typing import List, Tuple
from .xml_tag import Xml_Tag
from .xml_parser import XmlParser
import bookframe

class FB2_tag(Xml_Tag):
    def work(self, n=0) -> List[bookframe.BookFrame]:
        """returns list of bookframe.Bookframe of this element"""
        note = False
        if 'note' in self.attr and self.attr['note']:
            note = True
            for child in self.content:
                child.add_attribute('note', True)

        if self.tag == 'title':
            yield bookframe.BookFrame(None,'title_empty', {})
            for child in self.content:
                if child.tag == 'empty-line':
                    yield bookframe.BookFrame(None, 'empty', child.attr)
                else:
                    # p
                    yield bookframe.BookFrame(child.text, 'title', child.attr)
            if not note: 
                yield bookframe.BookFrame(None,'title_empty', {})
            return

        elif self.tag == 'poem':
            for child in self.content:
                if child.tag == 'stanza':
                    for _el in child.work():
                        yield _el
                    yield bookframe.BookFrame(None, 'stanza_empty' , child.attr)

                elif child.tag == 'epigraph':
                    for _el in child.work():
                        yield _el

                elif child.tag in ['title', 'text-author']:
                    # list of BookFrame
                    for el in child.work():
                        el.add_attribute('poem', True)
                        yield el

                elif child.tag[:4] == 'date':
                    print('note for poem -> date')
                    print('date can contain key "value" in tag')
                    bookframe.BookFrame(child.text, 'date', child.attr)
            return 

        elif self.tag == 'epigraph':
            for child in self.content:
                if child.tag == 'empty-line':
                    for _el in child.work():
                        yield _el
                elif child.tag == 'p':
                    for temp_tag in child.work():
                        temp_tag.add_attribute('epigraph', True)
                        yield temp_tag
                elif child.tag == 'text-author':
                    for frame in child.work():
                        frame.add_attribute('epigraph',True)
                        yield frame
                elif child.tag in ('poem','cite'):
                    elements = child.work()
                    for el in elements:
                        el.add_attribute('epigraph', True)
                        yield el
                else:
                    print('unknown content for')
                    print('epigraph:')
                    print(child.tag)
            return

        elif self.tag == 'cite':
            for child in self.content:
                for el in child.work():
                    el.add_attribute('cite', True)
                    yield el
            return

        for child in self.content:
            for _el in child.work():
                yield _el

        if self.tag == 'annotation':
            yield bookframe.BookFrame(None,'annotation_empty', {})

        if self.tag in ['body', 'section', 'stanza', 'annotation', 'coverpage', 'history']:
            return 

        element = None
        if self.tag == 'empty-line':
            element = bookframe.BookFrame(None, 'empty', {})
        elif self.tag == 'image':
            element = bookframe.BookFrame(None, 'image', self.attr)
        else:
            element = bookframe.BookFrame(self.text, self.tag, self.attr)
        yield element

    def work2(self, n=0) -> List[bookframe.BookFrame]:
        """returns list of bookframe.Bookframe of this element. Works without yields"""
        result = []
        note = False
        if 'note' in self.attr and self.attr['note']:
            note = True
            for child in self.content:
                child.add_attribute('note', True)

        if self.tag == 'title':
            result.append(bookframe.BookFrame(None,'title_empty', {}))
            for child in self.content:
                if child.tag == 'empty-line':
                    result.append(bookframe.BookFrame(None, 'empty', child.attr))
                else:
                    # p
                    result.append(bookframe.BookFrame(child.text, 'title', child.attr))
            if not note: 
                result.append(bookframe.BookFrame(None,'title_empty', {}))
            return result

        elif self.tag == 'poem':
            for child in self.content:
                if child.tag == 'stanza':
                    result += child.work()
                    result.append(bookframe.BookFrame(None, 'stanza_empty' , child.attr))

                elif child.tag == 'epigraph':
                    result += child.work()

                elif child.tag in ['title', 'text-author']:
                    # list of BookFrame
                    title_content = child.work()
                    for el in title_content:
                        el.add_attribute('poem', True)
                        result.append(el)

                elif child.tag[:4] == 'date':
                    print('note for poem -> date')
                    print('date can contain key "value" in tag')
                    result.append(child.text, 'date', child.attr)
            
            return result

        elif self.tag == 'epigraph':
            for child in self.content:
                if child.tag == 'empty-line':
                    result += child.work()
                elif child.tag == 'p':
                    temp_tag = child.work()[0]
                    temp_tag.add_attribute('epigraph', True)
                    result.append(temp_tag)
                elif child.tag == 'text-author':
                    frames = child.work()
                    for frame in frames:
                        frame.add_attribute('epigraph',True)
                        result.append(frame)
                elif child.tag in ('poem','cite'):
                    elements = child.work()
                    for el in elements:
                        el.add_attribute('epigraph', True)
                        result.append(el)
                else:
                    print('unknown content for')
                    print('epigraph:')
                    print(child.tag)
            return result

        elif self.tag == 'cite':
            for child in self.content:
                content = child.work()
                for el in content:
                    el.add_attribute('cite', True)
                    result.append(el)
            return result

        for child in self.content:
            result += child.work()

        if self.tag == 'annotation':
            result.append(bookframe.BookFrame(None,'annotation_empty', {}))

        if self.tag in ['body', 'section', 'stanza', 'annotation', 'coverpage', 'history']:
            return result

        element = None
        if self.tag == 'empty-line':
            element = bookframe.BookFrame(None, 'empty', {})
        elif self.tag == 'image':
            element = bookframe.BookFrame(None, 'image', self.attr)
        else:
            element = bookframe.BookFrame(self.text, self.tag, self.attr)
        result.append(element)
        return result


class FB2Book(XmlParser):
    ignore_tags = ['a', 'p', 'v', 'strong', 'description', 'binary', 'emphasis', 'text-author', 'subtitle', 'image']

    def parce_string(self, string:str, pos:int) -> Tuple[FB2_tag, int]:
        root = FB2_tag()
        if string[pos] != '<':
            pos = string.find("<", pos)
        close = string.find(">", pos)
        tag_txt = string[pos+1:close]
        self_closed = self.is_self_closed(tag_txt)
        # divide tag and xml arguments here!!
        root.tag, root.attr = self.get_tag_arguments(tag_txt)

        if self_closed:
            return root, close + 1
        pos = close + 1
        # ignore parsing content of tags with text content
        # this code only takes text inside tag
        if root.tag in self.ignore_tags:
            close_tag_text = self.get_close_tag(root.tag)
            close_tag_pos = string.find(close_tag_text, pos)
            if close_tag_pos == -1:
                close_tag_pos = len(string)
            root.text = string[pos:close_tag_pos]
            return root, close_tag_pos + len(close_tag_text)
        closed = False
        while (not closed) and (pos < len(string)):
            content_start = pos
            while (pos < len(string)) and string[pos] != "<":
                pos += 1
            if (pos >= len(string)): return root, pos
            plain_text = string[content_start:pos]
            if plain_text != '' and not plain_text.isspace():
                plain_tag = FB2_tag()
                plain_tag.tag = "plain_text"
                plain_tag.text = plain_text
                root.append(plain_tag)
            # work '<'
            if pos + 1 == len(string):
                closed = True
            if string[pos+1] == '/':
                closed = True
                close_pos = string.find('>', pos)
                pos = max(close_pos + 1, pos + 1)
            #it is internal tag
            if not closed:
                sub_tag, pos = self.parce_string(string, pos)
                root.append(sub_tag)
        return root, pos

