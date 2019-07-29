#Доработать приложение по поиску авиабилетов, чтобы оно возвращало билеты
#по названию города, а не по IATA коду.
#Пункт отправления и пункт назначения должны передаваться в качестве параметров.
#Сделать форматированный вывод, который содержит в себе пункт отправления,
#пункт назначения, дату вылета, цену билета

import requests
import json
import pprint


#Ввод городов на русском
def iata_code(origin, destination):
    search ="https://www.travelpayouts.com/widgets_suggest_params?q=%20" + origin + " , %20" + destination
    predata = requests.get(search)
    iata = {}
    iata = predata.json()
    iata_origin = iata['origin']['iata']
    iata_destination = iata['destination']['iata']
    return(iata_origin, iata_destination)
    

def best_value(origin, destination):
    iata_origin, iata_destination = iata_code(origin, destination)
    preload = {'origin': iata_origin, 'destination': iata_destination,}
    req = requests.get("http://min-prices.aviasales.ru/calendar_preload", params=preload)
    data = json.loads(req.text)
    #Вывод отдельных полей
    price = [data['best_prices'][0]['value']]
    dep_date = data['best_prices'][0]['depart_date']
    return_date = data['best_prices'][0]['return_date']
    print(f'Лучшая цена {origin} - {destination}, \n на период с {dep_date} по {return_date}\n {price} руб. ')


best_value('Москва', 'Барселона')
