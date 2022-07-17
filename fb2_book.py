from typing import List
import bookframe

class FB2_tag:
    def __init__(self) -> None:
        self.attr = {}
        self.tag = ''
        self.text = ''
        self.content = []

    def append(self, tag):
        self.content.append(tag)

    def work(self, n=0) -> List:
        """returns list of bookframe.Bookframe of this element"""
        result = []

        if self.tag == 'title':
            for child in self.content:
                if child.tag == 'empty-line/':
                    result.append(bookframe.BookFrame(None, 'empty', {}))
                else:
                    # p
                    result.append(bookframe.BookFrame(child.text, 'title', {}))
            return result

        elif self.tag == 'poem':
            for child in self.content:
                if child.tag == 'stanza':
                    result += child.work()
                    result.append(bookframe.BookFrame(None, 'stanza_empty' , {}))

                elif child.tag == 'epigraph':
                    result += child.work()

                elif child.tag == 'title':
                    # list of BookFrame
                    title_content = child.work()
                    for el in title_content:
                        if el.type == 'empty':
                            result.append(el)
                        else:
                            # title -> poem_title
                            el.goTo('poem_title')
                            result.append(el)

                elif child.tag == 'text-author':
                    result += child.work()

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
                    temp_tag.goTo('epigraph_p')
                    result.append(temp_tag)
                elif child.tag == 'text-author':
                    result.append(bookframe.BookFrame(child.text, 'epigraph_author', {}))
                elif child.tag == 'poem':
                    elements: List[bookframe.BookFrame] = child.work()
                    for el in elements:
                        if el.type == 'v':
                            el.goTo('epigraph_poem_line')
                            result.append(el)
                        elif el.type == 'empty':
                            result.append(el)
                        elif el.type == 'date':
                            print('work date for epigraph -> poem -> date')
                        
                        elif el.type == 'text-author':
                            result.append(el)
                        
                        elif 'epigraph' in el.type:
                            result.append(el)

                        elif el.type == 'poem_title':
                            el.goTo('epigraph_poem_title')
                            result.append(el)

                        elif el.type == 'stanza_empty':
                            result.append(el) 
                elif child.tag == 'cite':
                    content = child.work()
                    for el in content:
                        if 'cite' in el.type:
                            result.append(el)
                        
                        elif 'date' in el.type:
                            result.append(el)

                        else:
                            el.goTo('cite_' + el.type)
                            result.append(el)
                else:
                    print('unknown content for')
                    print('epigraph:')
                    print(child.tag)
            return result

        elif self.tag == 'cite':
            for child in self.content:
                if child.tag == 'p':
                    el = child.work()[0]
                    el.goTo('cite_p')
                    result.append(el)
                elif child.tag == 'text-author':
                    el = child.work()[0]
                    el.goTo('cite_author')
                    result.append(el)
                elif child.tag == 'empty-line/':
                    result.append(bookframe.BookFrame(None, 'empty', {}))
                elif child.tag == 'subtitle':
                    result += child.work()
                elif child.tag == 'poem':
                    content = child.work()
                    for el in content:
                        if 'cite' in el.type:
                            result.append(el)
                        elif 'empty' in el.type:
                            result.append(el)
                        elif 'date' in el.type:
                            result.append(el)
                        else:
                            el.goTo('cite_' + el.type)
                            result.append(el)
            return result

        for child in self.content:
            result += child.work()

        if self.tag in ['body', 'section', 'stanza']:
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


def fb2_parser(text, pos=0):
    root = FB2_tag()
    while pos < len(text) and text[pos] != '<':
        pos += 1
    close = pos + text[pos:].find('>')
    tag = text[pos+1:close]
    root.tag = tag
    pos = close + 1
    if tag == 'p':
        close_tag = text[close:].find('</p>')
        tag_text = text[close+1:close_tag+close]
        pos += close_tag + 3
        root.text = tag_text
    elif tag == 'v':
        close_tag = text[close:].find('</v>')
        tag_text = text[close+1:close_tag+close]
        pos += close_tag + 3
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
                pos = pos + 9 - 1
    elif tag == 'text-author':
        close_tag = pos + text[close:].find('</text-author>')
        tag_text = text[close+1:close-pos+close_tag]
        pos = close_tag + len('</text-author>') - 1
        root.text = tag_text
    elif tag == 'subtitle':
        close_tag = pos + text[close:].find('</subtitle>')
        tag_text = text[close+1:close-pos+close_tag]
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
                pos += 7 - 1
    
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
                pos += 11 - 1
    
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
                pos += 7 - 1

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
    elif tag[:7] == 'section':
        pos = close + 1
        closed = False
        while not closed:
            while pos < len(text) and text[pos] != '<':
                pos += 1           
            if pos >= len(text):
                return root, pos
            if text[pos:pos+10] != '</section>':
                sub_tag, new_pos = fb2_parser(text, pos)
                root.append(sub_tag)
                pos = new_pos
                if pos >= len(text):
                    closed = True
            else:
                closed = True
                pos = pos + 10 - 1
    else:
        print('---uncnown---')
        print(tag)
        pos -= 1
    return root, pos


