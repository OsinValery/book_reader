from typing import List
import bookframe

class FB2_tag:
    def __init__(self) -> None:
        self.attr = {}
        self.tag = ''
        self.text = ''
        self.content : List[FB2_tag] = []

    def append(self, tag):
        self.content.append(tag)

    def work(self, n=0) -> List[bookframe.BookFrame]:
        """returns list of bookframe.Bookframe of this element"""
        result = []

        if self.tag == 'title':
            result.append(bookframe.BookFrame(None,'title_empty', {}))
            for child in self.content:
                if child.tag == 'empty-line/':
                    result.append(bookframe.BookFrame(None, 'empty', {}))
                else:
                    # p
                    result.append(bookframe.BookFrame(child.text, 'title', {}))
            result.append(bookframe.BookFrame(None,'title_empty', {}))
            return result

        elif self.tag == 'poem':
            for child in self.content:
                if child.tag == 'stanza':
                    result += child.work()
                    result.append(bookframe.BookFrame(None, 'stanza_empty' , {}))

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
                    result.append(child.text, 'date', {})
            
            return result

        elif self.tag == 'epigraph':
            for child in self.content:
                if child.tag == 'empty-line/':
                    result += child.work()
                elif child.tag == 'p':
                    temp_tag = child.work()[0]
                    temp_tag.add_attribute('epigraph', True)
                    result.append(temp_tag)
                elif child.tag == 'text-author':
                    result.append(bookframe.BookFrame(child.text, 'text-author', {'epigraph': True}))
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

        if self.tag in ['body', 'section', 'stanza', 'annotation']:
            return result

        element = None
        if self.tag == 'empty-line/':
            element = bookframe.BookFrame(None, 'empty', {})
        elif self.tag[:5] == 'image':
            start = self.tag.find('"')
            close = self.tag.find('"', start + 1)
            link = self.tag[start+1:close]
            element = bookframe.BookFrame(link, 'image', {})
        else:
            element = bookframe.BookFrame(self.text, self.tag, self.attr)
        result.append(element)
        return result


def fb2_parser(text:str, pos=0):
    root = FB2_tag()
    while pos < len(text) and text[pos] != '<':
        pos += 1
    close = text.find('>', pos)
    tag = text[pos+1:close]
    root.tag = tag
    pos = close + 1
    if tag == 'p':
        close_tag = text.find('</p>', close)
        tag_text = text[close+1:close_tag]
        pos = close_tag + 3
        root.text = tag_text
    elif tag == 'v':
        close_tag = text.find('</v>', close)
        tag_text = text[close+1:close_tag]
        pos = close_tag + 3
        root.text = tag_text
    elif tag == 'stanza':
        pos = close + 1
        closed = False
        while not closed:
            while text[pos] != '<':
                pos += 1  
            if text[pos:pos + 9] != '</stanza>':
                sub_tag, new_pos = fb2_parser(text, pos)
                root.append(sub_tag)
                pos = new_pos
                if pos >= len(text):
                    closed = True
            else:
                closed = True
                pos = pos + 8
    elif tag == 'text-author':
        close_tag = text.find('</text-author>',close)
        tag_text = text[close+1:close_tag]
        pos = close_tag + len('</text-author>') - 1
        root.text = tag_text
    elif tag == 'subtitle':
        close_tag = pos + text[close:].find('</subtitle>')
        tag_text = text[close+1:close_tag]
        pos = close_tag + len('</subtitle>') - 1
        root.text = tag_text
    elif tag[:5] == 'image':
        pos = close + 1
        root.text = tag
    elif tag == 'empty-line/':
        pos = close + 1
        root.text = tag
    elif tag == 'title':
        pos = close + 1
        closed = False
        while not closed:
            while text[pos] != '<':
                pos += 1  
            if text[pos:pos + 8] != '</title>':
                sub_tag, new_pos = fb2_parser(text, pos)
                root.append(sub_tag)
                pos = new_pos
                if pos >= len(text):
                    closed = True
            else:
                closed = True
                pos = pos + 8 - 1
    
    elif tag == 'poem':
        pos = close + 1
        closed = False
        while not closed:
            while text[pos] != '<':
                pos += 1
            if text[pos:pos+7] != '</poem>':
                sub_tag, new_pos = fb2_parser(text, pos)
                root.append(sub_tag)
                pos = new_pos
                if pos >= len(text):
                    closed = True
            else:
                closed = True
                pos += 6
    
    elif tag == 'epigraph':
        pos = close + 1
        closed = False
        while not closed:
            while text[pos] != '<':
                pos += 1
            if text[pos:pos+11] != '</epigraph>':
                sub_tag, new_pos = fb2_parser(text, pos)
                root.append(sub_tag)
                pos = new_pos
                if pos >= len(text):
                    closed = True
            else:
                closed = True
                pos += 10
    
    elif tag == 'cite':
        pos = close + 1
        closed = False
        while not closed:
            while text[pos] != '<':
                pos += 1
            if text[pos:pos+7] != '</cite>':
                sub_tag, new_pos = fb2_parser(text, pos)
                root.append(sub_tag)
                pos = new_pos
                if pos >= len(text):
                    closed = True
            else:
                closed = True
                pos += 6

    elif tag[:7] == 'section':
        pos = close + 1
        closed = False
        while not closed:
            if text[pos] == '>':
                pos += 1
            new_pos = text.find('<', pos)
            if new_pos == -1:
                free_text = text[pos:]
            else:
                free_text = text[pos:new_pos]
            
            free_text = work_free_text(free_text)
            if free_text != '':
                add_tag = FB2_tag()
                add_tag.tag = 'text'
                add_tag.text = free_text
                root.append(add_tag)
            
            if new_pos == len(text) or new_pos == -1:
                return root, len(text)
            pos = new_pos
            

            if text[pos:pos+10] != '</section>':
                sub_tag, new_pos = fb2_parser(text, pos)
                root.append(sub_tag)
                pos = new_pos
                if pos >= len(text):
                    closed = True
            else:
                closed = True
                pos = pos + 9

    elif tag[:4] == 'body':
        pos = close + 1
        closed = False
        while not closed:
            while text[pos] != '<':
                pos += 1  
            if text[pos:pos+7] != '</body>':
                sub_tag, new_pos = fb2_parser(text, pos)
                root.append(sub_tag)
                pos = new_pos
                if pos >= len(text):
                    closed = True
            else:
                return root, pos + 7

    elif tag[:10] == 'annotation':
        pos = close + 1
        closed = False
        while not closed:
            while text[pos] != '<':
                pos += 1
            if text[pos:pos+11] != '</annotation>':
                sub_tag, new_pos = fb2_parser(text, pos)
                root.append(sub_tag)
                pos = new_pos
                if pos >= len(text):
                    closed = True
            else:
                closed = True
                pos += 12

    else:
        print('---uncnown---')
        print(tag)
        pos -= 1
    return root, pos

def work_free_text(text: str) -> str:
    text = text.strip()
    return text
