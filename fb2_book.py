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

    def add_attribute(self, name, value):
        self.attr[name] = value

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
                if child.tag == 'empty-line/':
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
                if child.tag == 'empty-line/':
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
        if self.tag == 'empty-line/':
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
                if child.tag == 'empty-line/':
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
                if child.tag == 'empty-line/':
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
        if self.tag == 'empty-line/':
            element = bookframe.BookFrame(None, 'empty', {})
        elif self.tag == 'image':
            element = bookframe.BookFrame(None, 'image', self.attr)
        else:
            element = bookframe.BookFrame(self.text, self.tag, self.attr)
        result.append(element)
        return result

def get_tag_arguments(tag:str):
    attr = {}
    space_pos = tag.find(' ')
    if space_pos == -1:
        return tag, attr
    real_tag = tag[:space_pos]
    pos = space_pos + 1
    while pos < len(tag):
        eq_pos = tag.find('=',pos)
        if eq_pos == -1:
            pos = len(tag) + 10
        else:
            name = tag[pos:eq_pos].strip()
            val_start = tag.find('"',eq_pos)
            val_end = tag.find('"', val_start+1)
            value = tag[val_start+1:val_end]
            pos = val_end + 1
            attr[name] = value
    return real_tag, attr

def fb2_parser(text:str, pos=0):
    root = FB2_tag()
    while pos < len(text) and text[pos] != '<':
        pos += 1
    close = text.find('>', pos)
    tag = text[pos+1:close]
    # divide tag and xml arguments here!!
    root.tag, root.attr = get_tag_arguments(tag)
    tag = root.tag
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
        close_tag = text.find('</subtitle>', close)
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
            if text[pos:pos+13] != '</annotation>':
                sub_tag, new_pos = fb2_parser(text, pos)
                root.append(sub_tag)
                pos = new_pos
                if pos >= len(text):
                    closed = True
            else:
                closed = True
                pos += 12
    
    elif 'coverpage' in tag:
        pos = close + 1
        closed = False
        while not closed:
            while text[pos] != '<':
                pos += 1
            if text[pos:pos+12] != '</coverpage>':
                sub_tag, new_pos = fb2_parser(text, pos)
                root.append(sub_tag)
                pos = new_pos
                if pos >= len(text):
                    closed = True
            else:
                closed = True
                pos += 11

    elif 'history' in tag:
        pos = close + 1
        closed = False
        while not closed:
            while text[pos] != '<':
                pos += 1
            if text[pos:pos+10] != '</history>':
                sub_tag, new_pos = fb2_parser(text, pos)
                root.append(sub_tag)
                pos = new_pos
                if pos >= len(text):
                    closed = True
            else:
                closed = True
                pos += 9

    else:
        print('---uncnown---')
        print(tag)
        pos -= 1
    return root, pos

def work_free_text(text: str) -> str:
    text = text.strip()
    return text
