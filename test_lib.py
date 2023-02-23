import deep_translator

text = "test"


t = deep_translator.GoogleTranslator()
print(t.translate(text, source = 'en', target = "ru"))
t  = deep_translator.LibreTranslator()
print(t.translate(text, source = 'english', target = "russian"))
t  = deep_translator.LingueeTranslator(source = 'english', target = "russian")
print(t.translate(text, source = 'english', target = "russian"))





