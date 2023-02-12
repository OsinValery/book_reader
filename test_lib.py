import deep_translator

text = "test"
t = deep_translator.GoogleTranslator()



print(t.translate(text, source = 'en', target = "ru"))