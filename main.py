import requests
import os
import datetime
import pymongo
from bs4 import BeautifulSoup
from colorama import init, Fore
from apscheduler.schedulers.blocking import BlockingScheduler
from dotenv import load_dotenv

init()
load_dotenv()

cliente = pymongo.MongoClient(os.environ.get("URL_MONGO"))
db = cliente["sec"]
tabla = db["sello_sec"]
inicio = db["ultimo"].find_one()["codigo"] + 1


def busca_sello(codigo):
    try:
        url = f'https://ww6.sec.cl/qr/qr.do?a=prod&i={codigo:013d}'
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')

        tablas = soup.find_all('div', class_='texto')
        if len(tablas) == 2:
            dato = {}
            certificado_raw = []
            certificado = []
            producto_raw = []
            producto = []
            emision = tablas[0].text.splitlines()
            equipo = tablas[1].text.splitlines()

            for n in emision:
                certificado_raw.append(n.strip())

            for n in range(2, len(certificado_raw), 3):
                certificado.append(certificado_raw[n])

            for n in equipo:
                producto_raw.append(n.strip())

            for n in range(2, len(producto_raw), 3):
                producto.append(producto_raw[n])

            datos = {'_id': codigo, 'codigo': f'{codigo:013d}', 'res_excenta': certificado[1], 'fecha_resolucion': certificado[2],
                     'emisor': certificado[3], 'producto': producto[0], 'marca': producto[2], 'modelo': producto[3], 'pais': producto[1]}
            tabla.insert_one(datos)
            print(Fore.GREEN + f'Sello: {codigo:013d} guardado' + Fore.RESET)

        else:
            print(Fore.RED + f'Sello: {codigo:013d} no existe' + Fore.RESET)

    except Exception as e:
        print(Fore.CYAN + f'{e}' + Fore.RESET)

    finally:
        db["ultimo"].update_one(
            {"_id": 1},
            {"$set": {"codigo": codigo, "actualizado": datetime.datetime.utcnow()}},
        )



def obtener_sellos():
    print(Fore.YELLOW + f'Iniciando desde {inicio}' + Fore.RESET)
    for codigo in range(inicio, 9999999999999+1):
        busca_sello(codigo)

"""
sched = BlockingScheduler(timezone="America/Santiago")
sched.add_job(obtener_sellos, 'cron', day_of_week='mon', hour=6, minute=15)
sched.start()
"""

obtener_sellos()
