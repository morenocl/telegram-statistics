from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.tl.types import UserStatusOnline, UserStatusOffline, UserStatusRecently, UserStatusLastWeek, UserStatusLastMonth, UserStatusEmpty

from datetime import datetime, timedelta
import csv


# Estos valores de ejemplo no van a funcionar. Debes obtener tu api_id y
# api_hash de https://my.telegram.org
api_id =  12345
api_hash = '0123456789abcdef0123456789abcdef'
phone = '+541234567890'
groups = []
last_msg_date = {}
delta = timedelta(hours = -3)
fifteendays = timedelta(days = 15)
date_zero = datetime(1, 1, 1, 0, 0)
today = date_zero.today()

# crea un cliente y lo conecta como me.
client = TelegramClient(phone, api_id, api_hash)
client.start()

def get_username(user):
    if user.username:
        username= user.username
    else:
        username= ""
    return username

def get_name(user):
    if user.first_name:
        first_name= user.first_name
    else:
        first_name= ""
    if user.last_name:
        last_name= user.last_name
    else:
        last_name= ""
    return (first_name + ' ' + last_name).strip()


async def main():
    # obtengo la lista de chats y filtro los de interes.
    async for d in client.iter_dialogs():
        if 'nombre del grupo' in d.title or 'parte del nombre' in d.title:
            groups.append({'id': d.id, 'title': d.title, 'list': []})

    for group in groups:
        # obtengo la lista total de participantes.
        group['list'] = await client.get_participants(group['id'])
        print('Cantidad participantes ' + group['title'] + ': ', len(group['list']))

    # obtengo la fecha del ultimo mensaje
    for group in groups:
        for user in group['list']:
            msj = await client.get_messages(group['id'], from_user= user)
            if len(msj) > 0:
                last_msg_date[user.id] = msj[0].date + delta
            else:
                last_msg_date[user.id] = date_zero


    # Se crea un csv con los participantes filtrados
    print('\nSaving In file...')
    for group in groups:
        print('\tsaving ' + str(len(group['list'])) + ' in: ', group['title'])
        if len(group['list']) > 0:
            name_file = str(group['title']) + "_lastMessage" + ".csv"
            with open(name_file,"w",encoding='UTF-8') as f:
                writer = csv.writer(f,delimiter=",",lineterminator="\n")
                writer.writerow(['Ultimo mensaje','Username','Nombre','Grupo','user id', 'group id','access hash'])
                for user in group['list']:
                    user_date = last_msg_date[user.id].strftime('%d/%m/%y %H:%M')
                    writer.writerow([user_date, get_username(user), get_name(user), group['title'], user.id, group['id'], user.access_hash])

    for group in groups:
        print('\nGrupo: ' + group['title'])
        for user in group['list']:
            # aqui debajo va la accion correspondiente a cada intervalo de tiempo
            if last_msg_date[user.id] < today - fifteendays
                client.send_message(user.id, 'Hace mas de 15 dias no escribis!')
        print('--')

with client:
    client.loop.run_until_complete(main())
