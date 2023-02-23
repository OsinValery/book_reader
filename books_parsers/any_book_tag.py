
from typing import List


class AnyBookTag:
    def __init__(self) -> None:
        self.attr = {}
        self.tag = ''
        self.text = ''
        self.content : List[AnyBookTag] = []

    def append(self, tag: 'AnyBookTag'):
        self.content.append(tag)

    def add_attribute(self, name, value):
        self.attr[name] = value
    
    def work(self, n = 0):
        raise NotImplementedError("you should implement function work for class" + type(self))

