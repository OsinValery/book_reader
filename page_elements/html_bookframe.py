import io
import page_elements.page_widgets as page_widgets
from kivy.core.image import Image
from kivy.utils import escape_markup
from .bookframe import BookFrame


class HtmlBookFrame(BookFrame):
    def referize_text(self, text:str):
        refers = []
        i = 0
        result = ''
        pos = 0

        while (pos < len(text)) and text[pos].isspace():
            pos += 1
        
        result += text[0:pos]
        word_start = pos
        is_word = True

        while pos < len(text):
            if is_word:
                if text[pos].isspace():
                    is_word = False
                    word = text[word_start:pos]
                    refers.append(word)
                    result += '[ref=' + str(i) + ']' + word + '[/ref]'
                    i += 1
                    word_start = pos
            else:
                if not text[pos].isspace():
                    is_word = True
                    result += text[word_start:pos]
                    word_start = pos
            pos += 1
        
        if is_word:
            word = text[word_start:]
            result += '[ref=' + str(i) + ']' + word + '[/ref]'
            refers.append(word)
        else:
            result += text[word_start:]

        print('clear markup in refers')
        return result, refers

    def escape_text(self, text: str):
        text = text.replace('&', '&amp;')
        return text

    def make_content(self):
        another = self.attributs['another'] if 'another' in self.attributs else {}
        if self.cashed_widget:
            return self.cashed_widget

        widget = page_widgets.Unknown(
            text='Initial widget. It means, that it wasn\'t choosen. Tag = ' + self.type , 
            cite=False,
            epigraph=False,
            poem=False,
            note=False,
        )
        if self.type == 'html_p':
            text: str = self.content.lstrip()
            n = 8
            # 2 different unicode simbols
            if text[0] in ['-', '—']:
                n = 3        
            text = self.escape_text(text)
            text, refs = self.referize_text(text)
            text = ' ' * n + text
            widget = page_widgets.HTML_Paragraph(
                text= text, 
                referization=refs, 
                another_properties=another,
            )
        
        elif self.type == 'text':
            text: str = self.content.lstrip()   
            text = self.escape_text(text)
            text, refs = self.referize_text(text)
            widget = page_widgets.Html_text(
                text= text, 
                referization=refs, 
                another_properties=another,
            )
        
        elif self.type == 'file_image':
            extansion: str = self.attributs['path'][-4:]
            extansion = extansion.replace('.', '')
            if extansion in ['png', 'jpg', 'jpeg']:
                try:
                    with open(self.attributs['path'], mode='rb') as file:
                        data = file.read()
                    data = io.BytesIO(data)
                    img = Image(data, ext=extansion)
                    is_cover = 'cover' in self.attributs and self.attributs['cover']
                    return page_widgets.ImageData(texture=img.texture, cover = is_cover, another_properties=another)
                except Exception as e:
                    print(e)
                    return page_widgets.Mistake(text=f'picture wasn\'t loaded! ')
            else:
                print("\"", extansion, "\"", 'is not supported yet')
                widget = page_widgets.Space()
        
        else:
            print("from htmlBookframe!")
            print('unknown tag: ', self.type)
            print('content:')
            print(self.attributs)
            print(self.content)
            text = self.type + '\n' + self.content + '\n' + str(self.attributs)
            text = 'Uncnown element;\nThat\'s content:\n' + text
            widget = page_widgets.Unknown(text = text)
        
        self.cashed_widget = widget
        return widget
