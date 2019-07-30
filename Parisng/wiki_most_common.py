'''

В приложении парсинга википедии получить первую ссылку на соседнюю страницу
и вывести все значимые слова из неё. Результат записать в файл в форматированном виде
2.* Научить приложение определять количество ссылок в статье.
Спарсить каждую ссылку и результаты записать в отдельные файлы.

'''

from requests import get
import json
import pprint
import re
from collections import Counter


#Определили ссылку
def get_link(topic):
    link = "https://ru.wikipedia.org/wiki/" + topic.capitalize()
    return link

#Скачали весь  текст по ссылке
def get_topic_page(topic):
    link = get_link(topic)
    html = get(link).text
    return html

#Нашли все слова длиннее 3 букв
def get_topic_text(topic):
    html_content = get_topic_page(topic)
    words = re.findall("[а-яА-Я]{3,}",html_content)
    return words

#Сделали словарь слово-количество упоминаний
def get_common_words(topic):
    words = get_topic_text(topic)
    rate = Counter(words)
    return rate

#Вывели топ10 в столбик
def visualize_common_words(topic):
    words = get_common_words(topic).most_common(10)
    i = 0
    for word in words:
        print(words[i])
        i += 1


def get_relink(topic):
    html_content = get_topic_page(topic)
    relink = re.findall(r'<li><a rel="nofollow" class="external text" href=[\'"]?([^\'" >]+)', html_content)
    print( '\n'.join(relink))
    return relink

def file_data(topic):
    new_link = get_relink(topic)
    #считаем строки
    i =0
    for line in new_link:
        i+=1
        new_html = get(line).text
        new_words = re.findall("[а-яА-Я]{3,}",new_html)
        new_rate = Counter(new_words)
        file = open(topic + str(i) +'.txt','w', encoding='UTF-8')
        file.write(f'{line}\n')
        commons = new_rate.most_common(10)
        k = 0
        for _ in commons:
            file.write(commons[k][0]+' ,')
            k += 1
        file.close()
    print(f'По запросу {topic} найдено {i} дополнительных ссылок')
    
 

topic = 'тигр'
lists = visualize_common_words(topic)
lists = file_data(topic)
#pprint.pprint(lists)
