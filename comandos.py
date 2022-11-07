#pip(request, bs4, duckduckgo_search )
import re
import requests
from duckduckgo_search import ddg
#from beautifulSoup import BeautifulSoup
import urllib
import os
import subprocess
import sys
from queue import Queue
import threading

LINKS = []
cola = Queue()
terminado = False

#si esta vacio enviamos eco, de lo contrario el eco de la palabra
def Echo(string):
    if string == '?':
        return 'echo.', 'text'
    else:
        return string, 'text'


# Mostrando los comandos sisponibles
def Help(string):
    Ayuda = '''
    Los comandos disponibles son:\n
    /echo Comando para saber si el bot se encuentra activo.\n
    /help Presenta esta ayuda.\n
    /web Busca una palabra, frase o dirección URL en la web devolviendo la página html asociada.\n
    /chip Realiza una búsqueda DataSheet en formato pdf.\n
    Nota: No abusen que soy nuevo :)
    '''
    return Ayuda, 'text'
    
    
def AdminHelp(string):
    Ayuda = '''
    Los comandos disponibles son:\n
    /echo Comando para saber si el bot se encuentra activo\n
    /help Presenta esta ayuda.\n
    /web Busca una palabra, frase o dirección URL en la web devolviendo la página html asociada.\n
    /chip Realiza una búsqueda DataSheet en formato pdf.\n
    /reset Fuerza el reinicio del bot par su actualizacion
    '''
    return Ayuda, 'text'
    


#************** AUN TRABAJANDO DESDE ACA ******************************

#si esta vacio solicitamos entre algo y sugerimos con ayuda
#de lo contrario verificamos si es una url o solo texto
def Buscador(string):
    if string == '?':
        return 'Requiere de una palabra, frase o dirección web.', 'text'
    else:
        if re.match('http://', string) or re.match('https://', string):
            # Es URL
            response = requests.get(string)
        else:
            #print("Solo es texto grande")
            new_s = string.replace(' ', '+')
            response = requests.get('https://google.com/search?client=opera&q=' + new_s)
    return response.text, 'html'
    
"""
    #desde aca es lo nuevo eliminando etiquetas
    VALID_TAGS = 'div', 'p'
    value = response.text
    soup = BeautifulSoup(value)

    for tag in soup.findAll(True):
        if tag.name not in VALID_TAGS:
            for i, x in enumerate(tag.parent.contents):
                if x == tag: break
            else:
                print("Can't find", tag, "in", tag.parent)
                continue
            for r in reversed(tag.contents):
                tag.parent.insert(i, r)
            tag.extract()
    print(soup.renderContents())
"""
    

    
def DataSh(string):
    # print('Buscando: '+string)
    keyword = string + ' filetype:pdf'
    results = ddg(keyword, region='es-es', time=2, max_results=25)

    for link in results:#recorremos los resultados
        URL = link.get('href', [])#selecciono solo los link
        for LK in sitios:#recorremos cada sitio
            if re.match(LK, URL): #si esta entre los preferidos
                break
    try:       
        urllib.request.urlretrieve(URL, string+'.pdf')# lo descargo
        cola.put(string+'.pdf')
        print ('añadiendo contenido a la cola')
        print (string+'.pdf')
    except IndexError:
        #return ('Hoja de datos no encontrada, intente otra búsqueda', 'text')
        cola.put(f'Hoja de datos no encontrada para {string}, intente otra búsqueda')
        
    


def ResetApp():#Reiniciar app para actualizaciones
    subprocess.call([sys.executable, os.path.realpath('Bot_Email.py')]+ sys.argv[1:])
    print('Reinicio realizado..')
    return 'Reinicio realizado..', 'text'


sitios = ['https://www.elektronik-kompendium.de',
          'https://www.electronicoscaldas.com',
          'https://www.ic-components.com',
          'https://mvelectronica.com',
          'https://media.digikey.com',
          'https://www.electroschematics.com',
          'https://www.onsemi.com',
          'https://datasheet.octopart.com',
          'https://udpeo.uni.edu.ni',
          'https://ldsound.info',
          'https://www.100circuits.com',
          'https://diagramas.diagramasde.com',
          'https://www.st.com',
          'https://www.onsemi.com',
          'http://hobbykit.eu',
          'https://media.digikey.com',
          'https://www.itisff.it',
          'https://www.rcscomponents.kiev.ua',
          'https://media.digikey.com',
          'https://www.ic-components.es',
          'https://www.semiee.com',
          'https://www.ariat-tech.es',
          'https://www.futurlec.com',
          'http://www.staner.com'
          ]   


def Crear_hilo(string):
    hilo = threading.Thread(target=DataSh, 
                            args=(string,),
                            name=string)
    hilo.start()
    hilo.join()
    x=cola.get()
    print('Ya lo saque: '+x)
    return x, 'adj'


commands = {
    '/echo': Echo,
    '/help': Help,
    '/web': Buscador,
    '/chip': Crear_hilo
}

admincommand = {
    '/echo': Echo,
    '/help': AdminHelp,
    '/web': Buscador,
    '/chip': Crear_hilo, 
    '/reset':ResetApp
}