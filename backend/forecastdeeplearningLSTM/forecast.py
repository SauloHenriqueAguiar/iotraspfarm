import os
import json
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from core.data_processor import DataLoader
from core.model import Model
import sqlite3
from datetime import datetime, timedelta


def plot_results_live(predicted_data, true_data):

    print("Dados Reais:", true_data)
    print("Previsão:", predicted_data)

def day_of_week(idx):
    dias_da_semana = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    if idx >= 0 and idx < len(dias_da_semana):
        return dias_da_semana[idx]
    else:
        return 'Invalid index'

def previsao():

    # carrega dados do modelo e salva modelo
    configs = json.load(open('config.json', 'r'))
    if not os.path.exists(configs['model']['save_dir']):
        os.makedirs(configs['model']['save_dir'])

    model = Model()
    model.build_model(configs)

    seq_len = configs['data']['sequence_length'],
    sensor_data = []
    predictions_data = []
    live_data = np.arange(seq_len[0]-1)

    # carrega dados do banco de dados
    database = r"C:\Users\saulo\PrevDailyWeakly\backend\databaseedge\db\bancosensor.db"
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SensorValores")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[
                      'Time', 'Data', 'Dia', 'Semana', 'Mes', 'Humidity', 'Temperature', 'pH', 'pHpred'])
    conn.close()

    # pega ultimos 20 valores do banco de dados
    get_pH = df['pH'].tail(20).values[0]
    get_Time = df['Time'].tail(20).values[0]
    get_pH = df['pH'].tail(1)
    # format get_ph to float com 2 casas decimais
    get_pH = float(get_pH)
    get_pH = round(get_pH, 2)
    

    sensor_port = get_pH

    #print ("Sensor Port:", sensor_port)

    while True:
        i = 0
        # armazenar os dados de entrada no array de dados de teste
        while i < seq_len[0]-1:

            live_data[i] = sensor_port
            live_data = live_data.astype(float)

            sensor_data.append(live_data[i])
            i += 1
            # converter dados de live_data para float com duas casas decimais
            live_data = live_data.astype(float)
            #print(  "Dados de entrada:", live_data)
        # construir dados in live da LSTM
        sensor_struct_data = live_data[np.newaxis, :, np.newaxis]

        #### previsão em live tempo real(in live)  ####

        predictions = model.predict_sequence_live(
            sensor_struct_data, configs['data']['sequence_length'])
        predictions_data.append(predictions)
        plot_results_live(predictions_data[-120:], sensor_data[-100:])
        time.sleep(2)  # tempo espera para mostrar nova previsão
        predict = predictions[-1]
        predicaopH = float(predict)
        # format predicaopH to float com 2 casas decimais
        previsaopH = round(predicaopH, 2)
        # pegar data e hora atual
        get_Time = time.strftime("%Y-%m-%d %H:%M:%S")

        # treinamento a cada 1 minuto
        if len(sensor_data) > 10 * seq_len[0] and int(time.time() % 20) == 0:
            np.savetxt('data\sensor.csv', sensor_data,
                       delimiter=',', header='sensor_value')

        # carregar dados para treinamento
            data = DataLoader(
                os.path.join('data', configs['data']['filename']),
                configs['data']['train_test_split'],
                configs['data']['columns']
            )

            x, y = data.get_train_data(
                seq_len=configs['data']['sequence_length'],
                normalise=configs['data']['normalise']
            )

        # treinamento do modelo
            model.train(
                x,
                y,
                epochs=configs['training']['epochs'],
                batch_size=configs['training']['batch_size'],
                save_dir=configs['model']['save_dir']
            )
            sensor_data = sensor_data[-100:]

            # criar tabela com nome PredictValues no banco de dados C:\Users\saulo\PrevDailyWeakly\databaseedge\db\bancosensor.db e inserir valores predicaopH e get_time no banco de dados
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS PredictValues (Time TEXT, pHpred FLOAT)")
            cursor.execute("INSERT INTO PredictValues VALUES (?, ?)",
                           (get_Time, previsaopH))
            conn.commit()
            conn.close()

     #### previsão diaria semanal  ####

        if (int(time.time() % 10) == 0):
            data = DataLoader(
                os.path.join('data', configs['data']['filename']),
                configs['data']['train_test_split'],
                configs['data']['columns']
            )
            x_test, y_test = data.get_test_data(
                seq_len=configs['data']['sequence_length'],
                normalise=configs['data']['normalise']
            )

            predictions = model.predict_sequence_full(
                x_test, configs['data']['sequence_length'])
            predictions_daily = predictions[-10:]

            # pegar dados dia da semana
            get_Dia = datetime.now().strftime("%A")
            print("Dia da semana:", get_Dia)
            today = datetime.now().date()
            day_idx = (today.weekday() + 1) % 7
            previsaopH = float(predictions_daily[0])
            # format predicaopH to float com 2 casas decimais
            previsaopH = round(previsaopH, 2)
            


            num_days = 0
            if get_Dia == 'Monday':
                num_days = 3
            elif get_Dia == 'Tuesday':
                num_days = 2
            elif get_Dia == 'Wednesday':
                num_days = 1
            elif get_Dia == 'Thursday':
                num_days = 0
            elif get_Dia == 'Friday':
                num_days = 6
            elif get_Dia == 'Saturday':
                num_days = 5
            elif get_Dia == 'Sunday':
                num_days = 4

            print("Previsão próximos dias:")

            def day_of_week(idx): return [
                'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][idx]
            
            for i in range(0, num_days):
                print(day_of_week(day_idx), predictions_daily[i])
                day_idx = (day_idx + 1) % 7
           
        #    for i in range(num_days, 7):
         #       print(day_of_week(day_idx), predictions_daily[i])
         #       day_idx = (day_idx + 1) % 7

            
            # imprimir day_of_week e predictions_daily na forma de diciionario. exemplo: {'Monday': 6.5, 'Tuesday': 6.5, 'Wednesday': 6.5, 'Thursday': 6.5, 'Friday': 6.5, 'Saturday': 6.5, 'Sunday': 6.5} 
            dic_pred_dia_semana = dict(zip([day_of_week(day_idx % 7) for day_idx in range(day_idx, day_idx + 7)], predictions_daily))
            print(dic_pred_dia_semana)   
 
            dic_pred_dia_semana_json = {k: float(v) if isinstance(v, np.float32) else v for k, v in dic_pred_dia_semana.items()}
            # colocar dic_pred_dia_semana valores  em float com duas casas decimais
            dic_pred_dia_semana_json = {k: round(v, 2) if isinstance(v, float) else v for k, v in dic_pred_dia_semana_json.items()}
            json_str = json.dumps(dic_pred_dia_semana_json)
            # gravar no banco de dados dic_pred_dia_semana 
            conn = sqlite3.connect(database)
            cursor = conn.cursor()
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS TablePrevDiaSema (DiaAtual TEXT, PrevpHDiariaSemanal TEXT,Data TEXT, pHpred FLOAT)")
            cursor.execute("INSERT INTO TablePrevDiaSema VALUES (?, ?, ?, ?)",
                           (get_Dia, json_str, get_Time, previsaopH))
            conn.commit()
            conn.close()





if __name__ == '__main__':
    # execute main a cada 1 minuto
    while True:
        previsao()
        
