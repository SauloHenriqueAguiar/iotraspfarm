

import sqlite3
import serial
import datetime
import time
import pandas as pd
import csv
from datetime import datetime
import json

if __name__ == '__main__':

    PORT = 'COM4'
    ser = serial.Serial('COM4', 115200, timeout=2)
    # ser.flush()

    dataatualArray = []
    datacompatualArray = []
    diaArray = []
    semanaArray = []
    mesArray = []
    humArray = []
    tempArray = []
    pHArray = []
    pHpredArray = []

while True:
    message = ser.readline()
    data = message.strip().decode('utf8')
    # print(data)
    split_string = data.split(',')  # split string
    # converter a primeira parte da string em float
    humidity = float(split_string[0])
    # converter a segunda parte da string em float
    temperature = float(split_string[1])
    # converter a terceira parte da string em float
    pH = float(split_string[2])

    # now = datetime.now()
    # dt_string = now.strftime("%Y-%m-%d %H:%M:%S")

    # Finding the current time and day
    now = datetime.now()  # dataatual
    currentTime = now.strftime("%Y-%m-%d %H:%M:%S")
    day = now.strftime("%A")  # dia da semana
    week = now.strftime("%W")  # semana do ano
    month = now.strftime("%B")  # mês do ano

  

    # pegar os valores da coluna pH
    pHpred = pH


    print(currentTime, now, day,week,month, humidity, temperature, pH, pHpred)

    dataatualArray.append(now)
    datacompatualArray.append(currentTime)
    diaArray.append(day)
    semanaArray.append(week)
    mesArray.append(month)

    humArray.append(humidity)  # adicionar valores de umidade ao array
    tempArray.append(temperature)  # adicionar valores de temperatura do array
    pHArray.append(pH)
    pHpredArray.append(pHpred)

    # Criar um dicionário de dados
    df = pd.DataFrame({'Time': dataatualArray, 'Data': datacompatualArray, 'Dia': diaArray,'Semana': semanaArray, 'Mês': mesArray, 'Humidity': humArray, 'Temperature': tempArray, 'pH': pHArray, 'pHpred': pHpredArray})
                      


    database = r"C:\Users\saulo\PrevDailyWeakly\backend\databaseedge\db\bancosensor.db"
    conn = sqlite3.connect(database)
    '''conn = mysql.connect(host='localhost',
                  database='banco_sensor',
                     user='root',
                     password='sql_root_45t6')
     '''
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS SensorValores;')

    criatabela = ''' CREATE TABLE SensorValores(
                        Time TEXT,
                        Data TEXT,
                        Dia TEXT,
                        Semana TEXT,
                        Mês TEXT,
                        Humidity FLOAT,
                        Temperature FLOAT,
                        pH FLOAT,
                        pHpred FLOAT
                        
    );'''

    cursor.execute(criatabela)

    df.to_sql('SensorValores', conn, if_exists='append', index=False)


    print('Records are adding into table ..........')
    conn.commit()
    conn.close()

    
    