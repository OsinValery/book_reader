import io
import base64
from kivy.core.image import Image
from kivy.utils import escape_markup
import page_widgets

class BookFrame():
    def __init__(self, content, _type, args) -> None:
        self.content = content
        self.type = _type
        self.attributs = args
        self.have_note = False
        self.notes = {}

    def escape_text(self, text: str)-> str:
        # service symbols
        text = escape_markup(text)
        # work link

        while '</a>' in text:
            start = text.find('<a') + 1
            link_pos = text.find('l:href=', start)
            src = ''
            if link_pos >= 0:
                src_start = link_pos + 8
                finish = text.find('"', src_start)
                if finish != -1:
                    src = text[src_start:finish]
            content = ''
            if src != '':
                if src[0] != '#':
                    # website link
                    content = f'[u][color=#0000ffff] {src} [/color][/u] '
                else:
                    self.have_note = True

            close = text.find('>', start)
            try:
                end = text.find('</a>', start) 
                link_text = text[close+1:end]
            except Exception as e:
                link_text = ''
            if src != '' and src[0] == '#':
                # notes
                self.notes[src] = link_text
                link_text = ' [color=#00a400][size=20] ' + link_text + ' [/size][/color] '
            head, tail = text[0:start-1], text[end+5:]
            text = head + content + link_text + tail

        # bold text + cursive etc
        text = text.replace('<strong>', ' [b] ').replace('</strong>', ' [/b] ')
        text = text.replace('<emphasis>',' [i] ').replace('</emphasis>',' [/i] ')
        text = text.replace('<strikethrough>', ' [s] ').replace('</strikethrough>', ' [/s] ')
        text = text.replace('<sub>', ' [sub] ').replace('</sub>',' [/sub] ')
        text = text.replace('<sup>', ' [sup] ').replace('</sup>',' [/sup] ')
        return text

    def referize_text(self, text):
        refers = []
        i = 0
        result = ''
        words = text.split()

        for word in words:
            result += f'[ref={i}]{word}[/ref] '
            refers.append(word)
            i += 1
        return result, refers
    
    def make_content(self):
        "returns widget view to present it to user"
        if self.type == 'empty':
            return page_widgets.Space()
        elif self.type == 'p':
            text = self.content.strip()
            n = 8
            if text[0] in ['-', '—']:
                n = 3        
            text = self.escape_text(text)
            text, refs = self.referize_text(text)
            text = ' ' * n + text
            return page_widgets.Paragraph(text= text, referization=refs)
        elif self.type == 'title':
            text = self.content.strip()
            text = self.escape_text(text)
            text, refs = self.referize_text(text)
            return page_widgets.Title(text=text,referization=refs)
        elif self.type == 'subtitle':
            text = self.content.strip()
            text = self.escape_text(text)
            text, refs = self.referize_text(text)
            return page_widgets.SubTitle(text=text,referization=refs)
        elif self.type == 'image':
            if 'broken' in self.attributs:
                return page_widgets.Mistake(text=f'picture don\'t found: {self.content}')            
            try:
                data = self.content
                data = base64.decodebytes(data.encode('utf-8'))
                data = io.BytesIO(data)
                ext = self.attributs['type'][6:] 
                img = Image(data, ext=ext)
                return page_widgets.ImageData(texture=img.texture)
            except Exception as e:
                print(e)
                return page_widgets.Mistake(text=f'picture wasn\'t loaded! ')
        else:
            text = self.type + '\n' + self.content + '\n' + str(self.attributs)
            text = 'Uncnown element;\nThat\'s content:\n' + text
            return page_widgets.Unknown(text = text)
