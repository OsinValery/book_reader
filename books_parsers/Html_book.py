from .html_parser import Html_Parser
from .css_descriptor import CssDescriptor
from page_elements.html_bookframe import HtmlBookFrame
import os
from typing import List


class HtmlBook():
    def split_content(self, content: List[HtmlBookFrame], page_split_counter:int) -> List[List[HtmlBookFrame]]:
        result = []
        page_content = []
        for el in content:
            page_content.append(el)
            if len(page_content) == page_split_counter:
                result.append(page_content)
                page_content = []
        if len(page_content) != 0:
            result.append(page_content)
        return result

    def get_book_content(self, path:str, page_split_counter:int):
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
                pages += self.split_content(page_content, page_split_counter)

        return pages, {}
    

    def get_html_folder_book_content(self, path:str, page_split_counter: int):
        """path - path to folder"""
        files = [f 
                for f in os.listdir(path) 
                if f.endswith(('.css', '.html', '.htm')) and 
                os.path.isfile(os.path.join(path, f))
                ]
        html_parser = Html_Parser()
        pages = []
        css = CssDescriptor()
        for file in files:
             if file.endswith('.css'):
                  css.update_from_file(os.path.join(path, file))

        for html_file in files:
            if not html_file.endswith('.css'):
                html_tag = html_parser.parce_xml_file(os.path.join(path, html_file))
                style_tag = html_tag.find_tag_in_tree('style')
                if style_tag != None:
                    css.update_from_string(style_tag.text)
                body_tag = html_tag.find_tag_in_tree('body')

                if body_tag != None:
                    page_content = body_tag.work(css, path)
                    pages += self.split_content(page_content, page_split_counter)

        return pages, {}





