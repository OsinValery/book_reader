import io
import page_elements.page_widgets as page_widgets
from kivy.core.image import Image
from kivy.utils import escape_markup
from .bookframe import BookFrame


class HtmlBookFrame(BookFrame):
    def referize_text(self, text:str) -> str:
        return super().referize_text(text)

    def make_content(self):
        return super().make_content()
