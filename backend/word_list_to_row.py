with open('words.txt', 'r') as f:
    word_list = f.read().splitlines()

words = []
for word in word_list:
    words.extend(word.split(','))

with open('translations.csv', 'w') as f:
    for word in words:
        f.write(f'{word.strip()};\n')