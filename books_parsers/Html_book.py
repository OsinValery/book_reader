from .html_parser import Html_Parser
from .css_descriptor import CssDescriptor



class HtmlBook():
    def get_book_content(self, path):
        html_parser = Html_Parser()
        css = CssDescriptor()
        html_tag = html_parser.parce_xml_file(path)
        style_tag = html_tag.find_tag_in_tree('style')
        if style_tag != None:
            css.update_from_string(style_tag.text)
        body_tag = html_tag.find_tag_in_tree('body')
        pages = []
        if body_tag != None:
                page_content = body_tag.work(css, path)
                pages.append(page_content)
        return pages, {}
