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
        self.cashed_widget = None

    def add_attribute(self, name, value):
        self.attributs[name] = value
    
    def add_list_of_notes(self, notes: dict):
        if notes != {}:
            self.have_note = True
            self.notes.update(notes)
    
    @property
    def is_cover(self):
        return self.type == 'image' and 'cover' in self.attributs and self.attributs['cover']

    def escape_text(self, text: str):
        # service symbols
        text = text.replace('&amp;', '&')
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

    def referize_text(self, text:str):
        refers = []
        i = 0
        result = ''

        for word in text.split(' '):
            if word == '' or (word != '\n' and word.isspace()):
                continue
            # this solution works faster then format strings
            result += '[ref=' + str(i) + ']' + word + '[/ref] '
            refers.append(word)
            i += 1
        return result, refers
    
    def make_content(self):
        "returns widget view to present it to user"
        if self.cashed_widget is not None:
            return self.cashed_widget
        is_cite = (('cite' in self.attributs) and self.attributs['cite'])
        is_poem = (('poem' in self.attributs) and self.attributs['poem'])
        is_note = (('note' in self.attributs) and self.attributs['note'])
        is_epigraph = (('epigraph' in self.attributs) and self.attributs['epigraph'])

        widget = page_widgets.Unknown(
            text='Initial widget. It means, that it wasn\'t choosen. Tag = ' + self.type , 
            cite=is_cite,
            epigraph=is_epigraph,
            poem=is_poem,
            note=is_note,
        )

        if self.type == 'p':
            text: str = self.content.lstrip()
            n = 8
            # 2 different unicode simbols
            if text[0] in ['-', '—']:
                n = 3        
            text = self.escape_text(text)
            text, refs = self.referize_text(text)
            text = ' ' * n + text
            widget = page_widgets.Paragraph(
                text= text, 
                referization=refs, 
                cite=is_cite,
                epigraph=is_epigraph,
                poem=is_poem,
                note=is_note,
            )

        elif self.type == 'txt_p':
            text: str = self.content.lstrip()
            n = 8
            # 2 different unicode simbols
            if text[0] in ['-', '—']:
                n = 3
            text, refs = self.referize_text(text)
            text = ' ' * n + text
            widget = page_widgets.Paragraph(
                text= text, 
                referization=refs, 
                cite=is_cite,
                epigraph=is_epigraph,
                poem=is_poem,
                note=is_note,
            )

        elif self.type == 'v':
            text = self.escape_text(self.content)
            text, refs = self.referize_text(text)
            return page_widgets.Poem_line(
                text = text, 
                referization=refs,
                cite=is_cite,
                epigraph=is_epigraph,
                poem=is_poem,
                note=is_note,
            )
        elif self.type == 'empty':
            return page_widgets.Space()
        
        elif self.type == 'title':
            text = self.escape_text(self.content)
            text, refs = self.referize_text(text)
            widget = page_widgets.Title(
                text=text,
                referization=refs, 
                cite=is_cite,
                epigraph=is_epigraph,
                poem=is_poem,
                note=is_note,
            )
        
        elif self.type == 'title_empty':
            return page_widgets.Title_Empty()

        elif self.type == 'subtitle':
            text = self.content.strip()
            text = self.escape_text(text)
            text, refs = self.referize_text(text)
            widget = page_widgets.SubTitle(
                text=text,
                referization=refs,
                cite=is_cite,
                epigraph=is_epigraph,
                poem=is_poem,
                note=is_note,
            )

        elif self.type == 'stanza_empty':
            return page_widgets.Stanza_empty()
        
        elif self.type == 'annotation_empty':
            return page_widgets.Annotation_empty()

        elif self.type == 'text-author':
            text = self.escape_text(self.content)
            text, refs = self.referize_text(text)
            widget = page_widgets.Author(
                text=text, 
                referization=refs,
                cite=is_cite,
                epigraph=is_epigraph,
                poem=is_poem,
                note=is_note,
            )

        elif self.type == 'text':
            text = self.escape_text(self.content)
            text, refs = self.referize_text(text)
            widget = page_widgets.Text(
                text=text, 
                referization=refs,
                cite=is_cite,
                epigraph=is_epigraph,
                poem=is_poem,
                note=is_note,
            )
        
        elif self.type == 'note':
            text = self.escape_text(self.content.strip())
            text, refs = self.referize_text(text)
            widget = page_widgets.Note(
                text=text, 
                referization=refs,
                cite=is_cite,
                epigraph=is_epigraph,
                poem=is_poem,
                note=is_note,
            )

        elif self.type == 'image':
            if 'broken' in self.attributs:
                return page_widgets.Mistake(text=f'picture don\'t found: {self.content}')            
            try:
                data = self.content
                data = base64.decodebytes(data.encode('utf-8'))
                data = io.BytesIO(data)
                ext = self.attributs['type'][6:] 
                img = Image(data, ext=ext)
                is_cover = 'cover' in self.attributs and self.attributs['cover']
                return page_widgets.ImageData(texture=img.texture, cover = is_cover)
            except Exception as e:
                print(e)
                return page_widgets.Mistake(text=f'picture wasn\'t loaded! ')
        else:
            text = self.type + '\n' + self.content + '\n' + str(self.attributs)
            text = 'Uncnown element;\nThat\'s content:\n' + text
            widget = page_widgets.Unknown(text = text)

        if is_epigraph:
            self.cashed_widget = page_widgets.SelectablePair(pad = 0.5,child = widget)
        else:
            self.cashed_widget = widget
        return self.cashed_widget
