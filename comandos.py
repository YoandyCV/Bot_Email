from config import *
import os, re, requests, queue
from bs4 import BeautifulSoup
import urllib.parse
from urllib.parse import urlparse
from duckduckgo_search import ddg
import threading
from telegram.ext import Updater, CommandHandler, MessageHandler#, Filters


class MyThread(threading.Thread):
    def __init__(self, target, args=()):
        super().__init__(target=target, args=args)
        self._result = None

    def run(self):
        self._result = self._target(*self._args)

    @property
    def result(self):
        return self._result

def run_data_sh(string):
    t = MyThread(target=DataSh, args=(string,))
    t.start()
    t.join()
    return t.result        


def DataSh(string):
    # Crear un evento para indicar cuando se ha recibido un archivo PDF
    pdf_recibido = threading.Event()
    # Variable para almacenar el nombre del archivo PDF
    nombre_pdf = None

    # Función para manejar los mensajes de documento
    def handle_document(update, context):
        document = update.message.document
        # Verificar si el tipo de archivo es PDF
        if document.mime_type == 'application/pdf':
            # Descargar el archivo PDF con el mismo nombre
            nombre_archivo = document.file_name
            file = context.bot.get_file(document.file_id)
            file.download(nombre_archivo)
            # Almacenar el nombre del archivo PDF
            nonlocal nombre_pdf
            nombre_pdf = nombre_archivo
            # Establecer el evento de PDF recibido
            pdf_recibido.set()

    # Crear un objeto Updater y pasarle el token de acceso
    updater = Updater(token=TOKEN, use_context=True)
    # Obtener el despachador para registrar los controladores de mensajes
    dispatcher = updater.dispatcher
    # Registrar el controlador para los documentos
    document_handler = MessageHandler(Filters.document, handle_document)
    dispatcher.add_handler(document_handler)
    # Iniciar el bot en un hilo de ejecución separado
    updater.start_polling()
    # Enviar el texto proporcionado al bot
    updater.bot.send_message(chat_id=ID_CHAT, text='/c '+string)
    # Esperar a que se reciba un archivo PDF
    pdf_recibido.wait()
    # Detener el bot
    updater.stop()
    # Retornar el nombre del archivo PDF
    return ( nombre_pdf, 'pdf')





"""def DataSh(string):
    # Crear un evento para indicar cuando se ha recibido una respuesta
    respuesta_recibida = threading.Event()
    # Variable para almacenar la respuesta generada por el bot
    respuesta_generada = None

    # Función para manejar los mensajes de texto
    def handle_message(update, context):
        message = update.message.text
        # Almacenar la respuesta generada por el bot
        nonlocal respuesta_generada
        respuesta_generada = message
        # Establecer el evento de respuesta recibida
        respuesta_recibida.set()

    # Crear un objeto Updater y pasarle el token de acceso
    updater = Updater(token=TOKEN, use_context=True)
    # Obtener el despachador para registrar los controladores de comandos y mensajes
    dispatcher = updater.dispatcher
    # Registrar el controlador para los mensajes de texto
    message_handler = MessageHandler(Filters.text & (~Filters.command), handle_message)
    dispatcher.add_handler(message_handler)

    # Función para asignar los valores de update y context
    def assign_update_context(update, context):
        nonlocal respuesta_recibida
        nonlocal respuesta_generada
        respuesta_recibida = context.event
        respuesta_generada = context.user_data['respuesta_generada']

    # Registrar el controlador para asignar los valores de update y context
    assign_handler = MessageHandler(Filters.all, assign_update_context)
    dispatcher.add_handler(assign_handler)
    # Iniciar el bot en un hilo de ejecución separado
    updater.start_polling()
    # Enviar el texto proporcionado al bot
    updater.bot.send_message(chat_id=chat_id, text=string)
    # Esperar a que se reciba una respuesta
    respuesta_recibida.wait()
    # Detener el bot
    updater.stop()
    # Retornar la respuesta generada
    return (respuesta_generada, 'text')"""




        
"""def DataSh(string):
    URL = []
    keyword = string + ' filetype:pdf'
    results = requests.get(f"https://www.google.com/search?q={keyword}")
    soup = BeautifulSoup(results.text, 'html.parser')
    for link in soup.find_all('a'):
        href = link.get('href')
        if "url?q=" in href and not "webcache" in href:
            URL.append(href.split("?q=")[1].split("&sa=U")[0])
    for URL_t in URL:
        domain = urlparse(URL_t).hostname
        if domain in sitios:
            print('\nURL: '+URL_t)
            print('URL Encontrada: '+ domain)
            break
    else:
        return (f'Datasheet {string} no encontrado.', 'text')
    filename = URL_t.split('/')[-1]
    try:
        #print('Intentando descargar...')
        #print('La direccion seria:\n'+URL_t)
        response = requests.get(URL_t)
        with open(filename, 'wb') as f:
            f.write(response.content)
        return (filename, 'pdf')
    except:
        return ('No se pudo descargar', 'text')"""



#si esta vacio enviamos eco, de lo contrario el eco de la palabra
def Echo(string):
    if string == '?':
        return ('Estoy activo!!!', 'text')
    else:
        return (string, 'text')


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
    return (Ayuda, 'text')


def AdminHelp(string):
    Ayuda = '''
    Los comandos disponibles son:\n
    /echo Comando para saber si el bot se encuentra activo.\n
    /help Presenta esta ayuda.\n
    /web Busca una palabra, frase o dirección URL en la web devolviendo la página html asociada.\n
    /chip Realiza una búsqueda DataSheet en formato pdf.\n
    /reset Fuerza el reinicio del bot para su actualizacion
    '''
    return (Ayuda, 'text')


#si esta vacio solicitamos entre algo y sugerimos con ayuda
#de lo contrario verificamos si es una url o solo texto
def Buscador(string):
    # Verificar si el parámetro está vacío
    if not string:
        return ("Debe ingresar una palabra, frase o URL.",'text')
    else:
        # Verificar si la entrada es una URL
        if string.startswith("http"):
            try:
                # Verificar si la URL es un archivo
                if os.path.isfile(string):
                    # Descargar el archivo y retornar el nombre
                    response = requests.get(string)
                    filename = os.path.basename(string)
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    return (f"Se ha descargado el archivo {filename}.",'text')
                else:
                    # Obtener el HTML de la URL
                    response = requests.get(string)
                    html = response.text
            except requests.exceptions.RequestException as e:
                # Manejar la excepción y retornar un mensaje al usuario
                return (f"No se pudo obtener la página web: {str(e)}",'text')
        else:
            # Realizar la búsqueda en Google
            query = string.replace(" ", "+")
            url = f"https://google.com/search?client=opera&q={query}"
            try:
                response = requests.get(url)
                html = response.text
            except requests.exceptions.RequestException as e:
                # Manejar la excepción y retornar un mensaje al usuario
                return (f"No se pudo realizar la búsqueda: {str(e)}",'text')

        # Modificar los enlaces de la página web
        soup = BeautifulSoup(html, "html.parser")
        for link in soup.find_all("a", href=True):
            if link["href"].startswith("http"):
                email_body = f"/web {link['href']}"
                link["href"] = f"mailto:{radr}?body={urllib.parse.quote(email_body)}"
            else:
                # Convertir URL relativa a completa
                base_url = "https://www.google.com"
                complete_url = urllib.parse.urljoin(base_url, link["href"])
                email_body = f"/web {complete_url}"
                link["href"] = f"mailto:{radr}?body={urllib.parse.quote(email_body)}"

    # Retornar la HTML resultante
    return (str(soup), 'html')


def ResetApp():#Reiniciar app para actualizaciones
    subprocess.call([sys.executable, os.path.realpath('Bot_Email.py')]+ sys.argv[1:])
    print('Reinicio realizado..')
    return ('Reinicio realizado..', 'text')


sitios = ['panda-bg.com',
        'www.elektronik-kompendium.de',
          'www.electronicoscaldas.com',
          'www.ic-components.com',
          'mvelectronica.com',
          'media.digikey.com',
          'www.electroschematics.com',
          'www.onsemi.com',
          'datasheet.octopart.com',
          'udpeo.uni.edu.ni',
          'ldsound.info',
          'www.100circuits.com',
          'diagramas.diagramasde.com',
          'www.st.com',
          'hobbykit.eu',
          'media.digikey.com',
          'www.itisff.it',
          'www.rcscomponents.kiev.ua',
          'media.digikey.com',
          'www.ic-components.es',
          'www.semiee.com',
          'www.ariat-tech.es',
          'www.futurlec.com',
          'www.staner.com',
          'www.datasheetcatalog.com',
          'http://www.kontest.ru',
          'radio-hobby.org',
          'rutronic.eu',
          'www.elektronikjk.com',
          'www.e-ele.net'
          ]


commands = {
    '/echo': Echo,
    '/help': Help,
    '/web': Buscador,
    '/chip': run_data_sh
}

admincommand = {
    '/echo': Echo,
    '/help': AdminHelp,
    '/web': Buscador,
    '/chip': run_data_sh,
    '/reset': ResetApp
}