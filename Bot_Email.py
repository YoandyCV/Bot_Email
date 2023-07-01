from config import *
from comandos import *
import imapclient, imaplib, pyzmail, smtplib, time, os, re
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from email.mime.audio import  MIMEAudio
from email.mime.application import MIMEApplication



# Ampliando la limitacion imap
imaplib._MAXLINE = 1000000
cliente = ''


def imap_init():
    global i
    i = imapclient.IMAPClient(imapserver)
    c = i.login(radr, pwd)
    i.select_folder('INBOX')


def smtp_init():
    global s
    s = smtplib.SMTP(smtpserver, smtpserverport,timeout=60)
    c = s.starttls()[0]
    if c != 220: # if c is not 220
        raise Exception('Conexion tls fallida: ' + str(c))
    c = s.login(radr, pwd)[0]
    if c != 235: # if c is not 235
        raise Exception('SMTP login fallido: ' + str(c))


def get_unread():
    i.select_folder('INBOX')
    uids = i.search(['UNSEEN'])
    if not uids:
        return None #no hay mensajes disponibles
    else:
        #print("Encontrados %s Sin leer" % len(uids))
        return i.fetch(uids, ['BODY[]', 'FLAGS']) #retornamos el mensaje y lo marco como leido


def mail(text, tipo):
    msg = MIMEMultipart()
    msg['From'] = radr
    msg['To'] = cliente
    msg['Subject'] = ""
    # print('mensaje saliente:'+ cliente)
    if tipo == 'text':
        msg_p = MIMEText(text, 'plain')
    elif tipo == 'html':
        msg_p = MIMEText(text, 'html')
        msg_p.add_header('content-disposition', 'attachment', filename='web_index.html')
    elif tipo == 'audio':
        msg_p = MIMEAudio('audio.mp3')
        msg_p.add_header('Content-Disposition', 'attachment', filename='audio.mp3')
    elif tipo == 'image':
        msg_p = MIMEImage('image.jpg')
        msg_p.add_header('Content-Disposition', 'attachment', filename='image.jpg')
    elif tipo == 'adj':
        msg.attach(MIMEText('Encontrada la hoja de datos del: '+text, 'html'))#plain
        msg_p = MIMEApplication(open(text, 'rb').read())
        msg_p.add_header('Content-Disposition', 'attachment', filename=text)
    elif tipo == 'pdf':
        with open(text, 'rb') as f:
            pdf_data = f.read()
        msg.attach(MIMEText('Encontrada la hoja de datos del: '+text, 'html'))#plain
        msg_p = MIMEApplication(pdf_data, Name=text)
        msg_p['Content-Disposition'] = f'attachment; filename={text}'
        
    msg.attach(msg_p)
    s.sendmail(radr, cliente, msg.as_string())
    s.close()
    #print('Enviado un ' +tipo+' a '+cliente )
    #print('contenido: '+text)
    try:
        os.unlink(text)
    except:
        pass



def analyze_msg(raws, a):
    global cliente
    global cmd
    msg = pyzmail.PyzMessage.factory(raws[a][b'BODY[]'])
    frm = msg.get_addresses('from')
    cliente = frm[0][1]

    # Get text from message and remove signature
    text = msg.text_part.get_payload().decode(msg.text_part.charset)
    text = re.sub(r'--\s*\n.*', '', text, flags=re.DOTALL)

    # Extract command from text
    match = re.search(r'^/(\w+)', text.strip())
    if match:
        cmd = '/'+match.group(1)
        print(cmd)
        if frm[0][1] != admin:
            
            if cmd not in commands:
                return False
            else:
                try:
                    arg = text.split(' ', 1)[1]
                    arg =  arg.replace("\n", "").strip()
                except IndexError:
                    arg = '?'
                return [cmd, arg]
        else:
            if cmd not in admincommand:
                return False
            else:
                try:
                    arg = text.split(' ', 1)[1]
                    arg =  arg.replace("\n", "").strip()
                except IndexError:
                    arg = '?'
                return [cmd, arg]
    else:
        return False




"""def analyze_msg(raws, a):
    global cliente
    # print("Analizar mensaje segun ID " + str(a))
    msg = pyzmail.PyzMessage.factory(raws[a][b'BODY[]'])
    frm = msg.get_addresses('from')
    cliente = frm[0][1] # obtenemos a quien responder la solicitud
    #print(cliente)



    # Administracion del bot
    if frm[0][1] != admin:
        print('Cliente: '+cliente)
        text = msg.text_part.get_payload().decode(msg.text_part.charset)
        cmds = text.replace('\r\n', '').split(' ', 1)
        #print('Comando solicitado: '+cmds)
        if cmds[0] not in commands:
             #Para USUARIOS
             #verificando si existe el comando
            #print("El comando %s no es válido" % cmds[0])
            return False
        else: # si no hay accion asignamos un esacio de array
            try:
                cmds[1]
                return cmds
            except IndexError:
                cmds.append('?')
                return cmds
    else: #Para ADMIN
        #print('Admin: ' + admin)
        text = msg.text_part.get_payload().decode(msg.text_part.charset)
        cmds = text.replace('\r\n', '').split(' ', 1)
        if cmds[0] not in admincommand:
         #verificando si existe el comando
        #print("El comando %s no es válido" % cmds[0])
            return False
        else: # si no hay accion asignamos un esacio de array
            try:
                cmds[1]
                return cmds
            except IndexError:
                cmds.append('?')
                return cmds"""





if __name__ == '__main__':
    imap_init()
    print(f'Bot iniciado en ({radr})')



    

while True:  # Revicion constante
    print('En espera...')
    try:
        msgs = get_unread()
        while msgs is None:# si no hay esperamos un tiempo para revisar nuevamente
            time.sleep(check_freq)
            #imap_init()#por si se queda dormido
            #smtp_init()
            msgs = get_unread()#reintento
        for a in msgs.keys():
            if type(a) is not int:#Clasificarlo
                continue
            cmds = analyze_msg(msgs, a)#lo analizamos en busca e comandos
            if cmds is None:
                continue
            elif cmds is False:  # Comando no valido
                t = 'Comando no válido!!!\nLos comandos disponibles son: \n'
                for l in commands.keys():
                    t = t + str(l) + "\n"
                mail(t, 'text') #enviamos un email de tipo texto
                continue
            else:
                if cliente != admin: #Salida para los clientes
                    print('Como USER')
                    salida = commands[cmds[0]](cmds[1])
                    smtp_init()
                    mail(salida[0], salida[1])
                    #print(salida)
                else: #salida para el admin
                    print('Como ADMIN')
                    salida = admincommand[cmds[0]](cmds[1])
                    smtp_init()
                    mail(salida[0], salida[1])

    except OSError as e:
        print("Error de tipo:", type(e).__name__)
        time.sleep(30)
        imap_init()
        continue
    except smtplib.SMTPServerDisconnected:
        print("Re intento de conexion en breve")
        time.sleep(30)
        imap_init()
        continue
    