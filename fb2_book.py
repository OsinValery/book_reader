import bookframe

class FB2_tag:
    def __init__(self) -> None:
        self.attr = {}
        self.tag = ''
        self.text = ''
        self.content = []
        
    def append(self, tag):
        self.content.append(tag)
    
    def work(self, n=0):
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


        for child in self.content:
            result += child.work()

        if self.tag in ['body', 'section']:
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
    while text[pos] != '<':
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
                pos = pos + 8

    elif tag == 'body':
        pos = close + 1
        while pos < len(text):
            if text[pos:pos+7] != '</body>':
                sub_tag, new_pos = fb2_parser(text, pos)
                root.append(sub_tag)
                pos = new_pos
            else:
                pos += 8
    elif tag[:7] == 'section':
        pos = close + 1
        closed = False
        while not closed:
            while text[pos] != '<':
                pos += 1            
            if text[pos:pos+10] != '</section>':
                sub_tag, new_pos = fb2_parser(text, pos)
                root.append(sub_tag)
                pos = new_pos
                if pos >= len(text):
                    closed = True
            else:
                closed = True
                pos = pos + 10
    else:
        print('---uncnown---')
        print(tag)
        pos -= 1
    return root, pos


