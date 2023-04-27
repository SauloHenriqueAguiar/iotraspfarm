

import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import pandas as pd
import sqlite3
import json


app = dash.Dash(__name__)

# server = app.server

# carrega dados do banco de dados
database = r"/home/saulo/iotraspfarm/backend/databaseedge/db/bancosensor.db"
conn = sqlite3.connect(database)
cursor = conn.cursor()
cursor.execute("SELECT * FROM SensorValores")
rows = cursor.fetchall()
df = pd.DataFrame(rows, columns=[
    'Time', 'Data', 'Dia', 'Semana', 'Mes', 'Humidity', 'Temperature', 'pH', 'pHpred'])
conn.close()

get_pH = df['pH'].tail(20)
get_Time = df['Time'].tail(20)
get_pH = df['pH'].tail(1)
get_temp = df['Temperature'].tail(20)
get_humi = df['Humidity'].tail(20)
get_Dia = df['Dia'].tail(1)

app.layout = html.Div(

    [
        html.Div(
            [
                html.Img(src=app.get_asset_url('sun.png'), style={
                    'width': '50px', 'height': '50px', 'position': 'absolute', 'textAlign': 'center',
                    "margin-left": "10px",
                    "padding-top": "10px",
                }),

                html.Div(
                    [
                        html.H1(
                            "Sistema IoT Smartfarm",
                            style={
                                "margin-left": "100px",
                                "padding-top": "10px",
                                "color": "white",
                            },
                        )
                    ]
                ),
            ],
            style={
                "background-color": "#2ECC71",
                "height": "70px",
            },
        ),

        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Div(id='temp'),
                        html.Div(id='humi'),
                        html.Div(id='ph'),
                        html.Div(id='prev-diaria-semanal'),
                        html.Div(id='data-atual'), 
                        html.Div(id='ph-atual'),                       
                    ], className='temp_humidity_row')
                ], className='temp_humidity_column')
            ], className='temp_humidity twelve columns')
        ], className='row'),
        

        dcc.Graph(id='live-graph', animate=False,
                  style={'background-color': 'rgba(0,0,0,0)', 'opacity': '0.7',
                         'width': '60%', 'height': '90%', 'position': 'center',
                         'textAlign': 'center',
                         "margin-left": "270px",
                         "padding-top": "40px",
                         },),

        dcc.Interval(
            id='graph-update',
            interval=1000,
            n_intervals=0
        ),
    ]
)




@ app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals')]
)
def update_graph_scatter(n):
    database = r"/home/saulo/iotraspfarm/backend/databaseedge/db/bancosensor.db"
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SensorValores")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[
                      'Time', 'Data', 'Dia', 'Semana', 'Mes', 'Humidity', 'Temperature', 'pH', 'pHpred'])
    conn.close()

    get_pH = df['pH'].tail(15)
    get_Time = df['Time'].tail(20)

    # pegar dados de do banco C:\Users\saulo\PrevDailyWeakly\databaseedge\db\bancosensor.db da tabela TablePrevDiaSema
    databasepHpred = r"/home/saulo/iotraspfarm/backend/databaseedge/db/bancosensor.db"
    conn = sqlite3.connect(databasepHpred)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM PredictValues")
    rows = cursor.fetchall()
    datapredpH = pd.DataFrame(rows, columns=['Time', 'pHpred'])
    conn.close()

    get_pH_pred = datapredpH['pHpred'].tail(20)

    X = get_Time

    Y1 = get_pH_pred

    Y2 = get_pH

    data = go.Scatter(
        x=list(X),
        y=list(Y1),
        name='Previsão do pH',
        mode='lines+markers'
    )

    data2 = go.Scatter(

        x=list(X),
        y=list(Y2),
        name='Valor pH Real',
        mode='lines+markers'
    )

    layout = go.Layout(
        title='Valores pH',
        xaxis=dict(
            title='Tempo'
        ),
        yaxis=dict(
            title='Valor pH'
        )
    )

    return {'data': [data, data2],
            'layout': go.Layout(xaxis=dict(
                title='Tempo'
            ), yaxis=dict(
                title='Valores de pH'
            ))}


@ app.callback(
    Output('temp', 'children'),
    [Input('graph-update', 'n_intervals')]
)
def update_temp(n):
    database = r"/home/saulo/iotraspfarm/backend/databaseedge/db/bancosensor.db"
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SensorValores")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[
                      'Time', 'Data', 'Dia', 'Semana', 'Mes', 'Humidity', 'Temperature', 'pH', 'pHpred'])
    conn.close()

    get_temp = df['Temperature'].tail(20)

    temp = get_temp.iloc[-1]
    return [
        html.Div([
            html.Img(src=app.get_asset_url('hot.png'),
                     style={'height': '50px',
                            'width': '50px',
                            'position': 'absolute',
                            'textAlign': 'center',
                            "margin-left": "400px",
                            "padding-top": "10px",
                            }),
            html.Div([

                html.Div('°C', className='symbol',
                         style={'height': '50px',
                                'width': '50px',
                                "margin-left": "530px",
                                'top': '130px'

                                }),


                html.Div('{0:.1f}'.format(temp),
                         className='numeric_value',
                         style={'height': '50px',
                                'width': '50px',
                                "margin-left": "460px",
                                "padding-top": "10px",
                                'font-size': '32px',
                                'margin-bottom': '-10px',
                                'font-weight': 'bold',
                                'textAlign': 'center',
                                'position': 'absolute',
                                'top': '70px',
                                'color': '#666666',
                                }),


            ], className='temp_symbol')
        ], className='image_temp_row'),




        html.P('Temperatura', style={'color': '#666666',
                                     'width': '10px',
                                     "margin-left": "460px",
                                     "padding-top": "10px",
                                     'font-size': '12px',
                                     'margin-bottom': '-10px',
                                     'font-weight': '10',
                                     'textAlign': 'center',
                                     'position': 'absolute',
                                     'top': '120px',
                                     }),
    ]


@ app.callback(
    Output('humi', 'children'),
    [Input('graph-update', 'n_intervals')]
)
def update_humi(n):
    database = r"/home/saulo/iotraspfarm/backend/databaseedge/db/bancosensor.db"
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM SensorValores")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[
                      'Time', 'Data', 'Dia', 'Semana', 'Mes', 'Humidity', 'Temperature', 'pH', 'pHpred'])
    conn.close()

    get_humi = df['Humidity'].tail(20)

    hum = get_humi.iloc[-1]
    return [
        html.Div([
            html.Img(src=app.get_asset_url('humidity.png'),
                     style={'height': '50px',
                            'width': '50px',
                            'position': 'absolute',
                            'textAlign': 'center',
                            "margin-left": "570px",
                            "padding-top": "10px",
                            'top': '70px'
                            }),
            html.Div([
                html.Div('%', className='symbol',
                         style={'height': '50px',
                                'width': '50px',
                                "margin-left": "700px",
                                'top': '20px',
                                }),



                html.Div('{0:.1f}'.format(hum),
                         className='numeric_value',
                         style={'height': '50px',
                                'width': '50px',
                                "margin-left": "630px",
                                "padding-top": "10px",
                                'font-size': '32px',
                                'margin-bottom': '-10px',
                                'font-weight': 'bold',
                                'textAlign': 'center',
                                'position': 'absolute',
                                'top': '70px',
                                'color': '#666666'
                                })
            ], className='temp_symbol')
        ], className='image_temp_row'),

        html.P('Humidade', style={'color': '#666666',
                                  'width': '10px',
                                  "margin-left": "560px",
                                  "padding-top": "10px",
                                  'font-size': '12px',
                                  'margin-bottom': '-10px',
                                  'font-weight': '10',
                                  'textAlign': 'center',
                                  'position': 'absolute',
                                  'top': '120px',
                                  })
    ]

# mostrar na pagina os valores do dicionario vindo do banco de dados da tabela TablePrevDiaSema


@app.callback(
    Output('prev-diaria-semanal', 'children'),
    Output('ph-atual', 'children'),
    Output('data-atual', 'children'),
    [Input('graph-update', 'n_intervals')]
    
)
def update_prev_diaria_semanal(n):

    conn = sqlite3.connect(r'/home/saulo/iotraspfarm/backend/databaseedge/db/bancosensor.db')
    cursor = conn.cursor()

    # Executar consulta SQL para recuperar os dados da tabela
    cursor.execute("SELECT * FROM TablePrevDiaSema")

    # Recuperar os resultados da consulta
    results = cursor.fetchall()

    # Exibir os valores na tela
    for row in results:
        # pegar dados DiaAtual
        dataatual = row[0]
        # pegar dados PrevDiariaSemanal
        prevdiariasemanal = row[1]
        data = row[2]
        # print("Data Atual: %s, PrevDiariaSemanal: %s" % (dataatual, prevdiariasemanal))
        phatual = row[3]
    # Fechar a conexão com o banco de dados
    conn.close()

    # mostrar na pagina dataatual e prevdiariasemanal
    # Retornar os valores atualizados na forma de uma string formatada
    
    #formatar data deixar 01/01/2023
    data = data[8:10] + '/' + data[5:7] + '/' + data[0:4]

    # formatar dataatual deixar para exibir em portugues BR
    dataatual = dataatual.replace('Monday', 'Segunda')
    dataatual = dataatual.replace('Tuesday', 'Terça')
    dataatual = dataatual.replace('Wednesday', 'Quarta')
    dataatual = dataatual.replace('Thursday', 'Quinta')
    dataatual = dataatual.replace('Friday', 'Sexta')
    dataatual = dataatual.replace('Saturday', 'Sabado')
    dataatual = dataatual.replace('Sunday', 'Domingo')


    # formatar prevdiariasemanal retirar as aspas "" virgulas e colchetes 
    prevdiariasemanal = prevdiariasemanal.replace('"', '')
    prevdiariasemanal = prevdiariasemanal.replace(',', '')
    prevdiariasemanal = prevdiariasemanal.replace('{', '')
    prevdiariasemanal = prevdiariasemanal.replace('}', '')
    
    # formatar prevdiariasemanal deixar os valores com 2 casas decimais ex: Friday: 8.02 Saturday: 8.02 Sunday: 8.02
    prevdiariasemanal = prevdiariasemanal.replace('Monday: ', 'Segunda: ')
    prevdiariasemanal = prevdiariasemanal.replace('Tuesday: ', 'Terça: ')
    prevdiariasemanal = prevdiariasemanal.replace('Wednesday: ', 'Quarta: ')
    prevdiariasemanal = prevdiariasemanal.replace('Thursday: ', 'Quinta: ')
    prevdiariasemanal = prevdiariasemanal.replace('Friday: ', 'Sexta: ')
    prevdiariasemanal = prevdiariasemanal.replace('Saturday: ', 'Sabado: ')
    prevdiariasemanal = prevdiariasemanal.replace('Sunday: ', 'Domingo: ')
    
   


    


    
   

    return [
       
        html.Div(
            id='dataatual',
            children=[
                html.H2(dataatual + ' '+ data), 
                
            ],
            style={'textAlign': 'left',
                   'color': 'green',}
        ),
         html.Div(
            id='ph-atual',
            children=[
                html.H2('pH Atual:  ' +' '+ str(phatual)),
                
            ],
            style={'textAlign': 'right',
                   'color': 'red',
                     'font-size': '20px',
                     #'height': '50px',
                            'width': '900x',
                            #'position': 'absolute',
                            'textAlign': 'center',
                            # ajustar posição para cima
                           # "margin-top": "-50px",
                          
                         
                         
                        

                        
            

                   }
        ),
         html.Div(
            id='prevdiariasemanal',
            children=[
                html.H2('Previsão do pH para os proximos dias:'),
                html.H3(prevdiariasemanal, style={'color': 'blue'})
            ],
            style={'textAlign': 'center'}
        ),
       

    ]




if __name__ == '__main__':
    app.run_server(debug=False)
