'''
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и
реализовать функцию, записывающую собранные вакансии в созданную БД
2. Написать функцию, которая производит поиск и выводит на экран вакансии
с заработной платой больше введенной суммы

'''


#Введем переменные по поиску вакансий
VACANCY = 'java'        #название
MAX_PAGE = 1                #сколько страниц смотрим
HISTO_DAYS = 2             #за сколько дней смотрим (чтобы смотреть свежие)
BOTTOM = 100                #минимальный уровень зп, в тыс.рублей

import re
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
import pprint


#Поскольку зп указывается в разных валютах и с интервалами, приведем все в стандарт
def convert(salary):
    currency = 1
    if 'EUR' in salary:
        currency = 70
    if 'USD' in salary:
        currency = 60
    if salary == 'Не указанно':
        salary = '0.0'
    salary = salary.replace(' ', '')   #убираем пробелы 
    salary = salary[:salary.find('-')]  #если зп задана интервалом, берем нижнюю
    salary = re.findall("\d+", salary)
    salary = float(salary[0]) * currency
    return salary

#Основная функция парсинга. Данные складываем в датафрейм
def get_vacation_data(VACANCY, MAX_PAGE, HISTO_DAYS):
    n = 0
    position_data = []
    wages = []
    salary_convert = []
    hrefs = []
    
    hh_url = 'https://hh.ru/search/vacancy?search_period='+str(HISTO_DAYS)+'&text='+VACANCY+'&area=1'
    headers = {'accept': '*/*',
           'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/35.0.1916.47 Safari/537.3'}
    
    session = requests.session()
    
    while n < MAX_PAGE:
        request = session.get(hh_url+'&page='+str(n), headers=headers)
        html = bs(request.content, 'html.parser')
        divs = html.find_all('div', attrs={'data-qa': 'vacancy-serp__vacancy'})
        for div in divs:
            title = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'}).text
            salary = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
            if salary == None:
                salary = 'Не указанно'
            else:
                salary = div.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).text

            href = div.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})['href']
            payroll = convert(salary)
            position_data.append(title)
            wages.append(salary)
            salary_convert.append(payroll)
            hrefs.append(href)
        n += 1
    df = pd.DataFrame({'Title': position_data,
                       'Salary': wages,
                       'Salary_Convert': salary_convert,
                       'Link': hrefs}, columns=['Title', 'Salary', 'Salary_Convert', 'Href'])
    df.replace(u'\xa0', u'', regex=True, inplace=True)
    return df

hh_df = get_vacation_data(VACANCY, MAX_PAGE, HISTO_DAYS)

#Подключаем монго. Закидываем данные в базу
client = MongoClient('mongodb://127.0.0.1:27017')
db = client['headhunter']
hh_db = db.headhunter

#Для записи используем генератор , который выдает индекс и строку
for index, row in hh_df.iterrows():
    hh_data={
        'Title': row['Title'],
        'Salary': row['Salary'],
        'Salary_Convert': row['Salary_Convert'],
        'Href': row['Href']
    }
    hh_db.insert_one(hh_data)

#Сортируем и фильтруем данные по зарплате
for vacancies in hh_db.find().sort('Salary_Convert').where('this.Salary_Convert >' + str(BOTTOM)):
    pprint.pprint(vacancies)   




