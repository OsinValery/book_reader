import libretranslatepy as tr

lt = tr.LibreTranslateAPI("https://translate.argosopentech.com/")

result = lt.translate(
    'Hey, guys! I\'m gotta to visit Fried tomorrow. Who would like to go with?',
    source='en', target='ru',
)

print(result)