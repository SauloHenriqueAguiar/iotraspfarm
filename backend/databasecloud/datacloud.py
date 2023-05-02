import pandas as pd
from firebase import firebase
import csv
import time
import datetime
import os
import sqlite3
import json

firebase = firebase.FirebaseApplication(
    'https://projiotfarm-default-rtdb.firebaseio.com', None)


def update_firebase():
    # tabela 1 do banco
    database = r"/home/saulo/iotraspfarm/backend/databaseedge/db/bancosensor.db"
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SensorValores")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[
                      'Time', 'Data', 'Dia', 'Semana', 'Mes', 'Humidity', 'Temperature', 'pH', 'pHpred'])
    conn.close()

    if df.empty or not all(col in df.columns for col in ['Time', 'Humidity', 'Temperature', 'pH', 'Dia', 'Mes']):
        # O dataframe está vazio ou não tem todas as colunas necessárias
     return

    get_time = df['Time'].tail(1).iloc[0]
    get_humi = df['Humidity'].tail(1).iloc[0]
    get_temp = df['Temperature'].tail(1).iloc[0]
    get_pH = df['pH'].tail(1).iloc[0]
    get_dia = df['Dia'].tail(1).iloc[0]
    get_mes = df['Mes'].tail(1).iloc[0]

    # tabela 2 do banco
    conn = sqlite3.connect(r'/home/saulo/iotraspfarm/backend/databaseedge/db/bancosensor.db')
    cursor = conn.cursor()

    # Executar consulta SQL para recuperar os dados da tabela
    cursor.execute("SELECT * FROM TablePrevDiaSema")

    # Recuperar os resultados da consulta
    results = cursor.fetchall()

    # Exibir os valores na tela
    for row in results:
        # pegar dados DiaAtual
        #dataatual = row[0]
        # pegar dados PrevDiariaSemanal
        prevdiariasemanal = row[1]
        data = row[2]
        # print("Data Atual: %s, PrevDiariaSemanal: %s" % (dataatual, prevdiariasemanal))
        phprev = row[3]
    # Fechar a conexão com o banco de dados
    conn.close()

    # prevdiariasemanal =
    # phprev =

    data = {
        "Time": get_time,
        "Humidity": get_humi,
        "Temperature": get_temp,
        "pH": get_pH,
        "pHpred": phprev,
        "Dia": get_dia,
        "Mes": get_mes,
        "PrevpHDiariaSemanal": prevdiariasemanal,


    }

    result = firebase.post('/sensordata', json.dumps(data))
    print(result)


while True:
    update_firebase()
    time.sleep(30)

