# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline
from plotly import __version__
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot

import pylab 
import scipy.stats as stats
import statsmodels.api as sm

from numpy import mean
from numpy import median
from numpy import percentile

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report,confusion_matrix
from sklearn.preprocessing import StandardScaler

from pandas import read_csv
from pandas import datetime
from pandas import DataFrame

from statsmodels.tsa.arima_model import ARIMA
from pandas.plotting import autocorrelation_plot
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error,mean_absolute_error,explained_variance_score

import jupyter_dash
from jupyter_dash import JupyterDash
#import dash_core_components as dcc
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

df = pd.read_csv('https://raw.githubusercontent.com/JoaoYukio/projetoPCO114/main/CCEE_BR_Data.csv', sep=',')#pd.read_csv('CCEE_BR_Data.csv', sep=',')

df['Timestamp'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')
df['Ano'] = df['Timestamp'].dt.year
df['Mês'] = df['Timestamp'].dt.month
df['Dia'] = df['Timestamp'].dt.day
df['DiaSem'] = df['Timestamp'].dt.weekday

# exclude 'Exportador'
df=df[df['Classe']!='Exportador']
# df pré COVID
df0 = df[df['Covid']==0]
# df durante COVID
df1 = df[df['Covid']==1]

ACL_df = df[df['Classe']!='Distribuidor']

#Create a treemap of the consumption by ramo and UF
b = ACL_df.groupby(['Ramo','UF'])['Consumo'].sum()
#b = b.groupby(['UF']).mean()
b=b.reset_index().sort_values(['Consumo'],ascending=False)

treeMap = px.treemap(b, path=['UF', 'Ramo'], values='Consumo')
treeMap.update_layout(title='Consumo por ramo e estado', xaxis_title='UF', yaxis_title='Consumo (MWh)')
treeMap

#Plota o consumo médio por Ramo de forma descendente
rankInd = px.bar(ACL_df.groupby(['Ramo'])['Consumo'].mean().reset_index().sort_values(['Consumo'],ascending=True),
                y='Ramo', x='Consumo', orientation='h') #, title='Consumo médio por ramo'
rankInd.update_layout(xaxis_title='Consumo (MWh)', yaxis_title='Ramo')
rankInd

import json

#Read consumooBrasil
consumoBrasil = pd.read_csv('https://raw.githubusercontent.com/JoaoYukio/projetoPCO114/main/consumoBrasil.csv', sep=',')#pd.read_csv('consumoBrasil.csv', sep=',')

consumoEstado = df.groupby(['UF', 'Timestamp'])['Consumo'].sum()/1000
consumoEstado = consumoEstado.reset_index()
consumoEstado.columns = ['UF', 'Timestamp', 'Consumo']

consumoEstado

#Cria um grafico de linha com o consumo de energia por UF e por dia
lineUf = px.line(consumoEstado, x="Timestamp", y=consumoEstado["Consumo"].rolling(window=4).mean(), color='UF', title='Consumo de energia por UF')
lineUf.update_layout(xaxis_title='Data', yaxis_title='Consumo (MWh)')
lineUf.update_layout(
    xaxis=dict(
        rangeselector=dict(
            
            buttons=list([
                dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)
lineUf

import re, json, requests

url = 'https://raw.githubusercontent.com/JoaoYukio/projetoPCO114/main/brazil_geo.json'

#Ler o arquivo json com os dados geográficos do Brasil do github
resp = requests.get(url)

estados_do_brasil = json.loads(resp.text)#json.load(open('brazil_geo.json', 'r')) <- forma de ler localmente

df["UF"] = df["UF"].str.replace("\xa0", "")

# Cria um mapa com o consumo de energia de cada estado
figMap = px.choropleth_mapbox(
    df, locations="UF", color="Consumo",
    center={"lat":-16.95, "lon": -47.78},
    zoom = 3,
    geojson=estados_do_brasil,
    color_continuous_scale="Redor",
    mapbox_style="carto-positron",
    opacity=0.5,
    labels={'Consumo':'Consumo de Energia (MWh)'}
)
figMap.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

consumoRamo= df.groupby(['Ramo', 'Timestamp'])['Consumo'].sum()/1000

consumoRamo = consumoRamo.reset_index()
consumoRamo.columns = ['Ramo', 'Timestamp', 'Consumo']

consumoRamo.drop(consumoRamo[consumoRamo['Ramo'] == 'ACR'].index, inplace = True)

#Cria um grafico de linha com o consumo de energia por ramo e por dia
figRamo = px.line(consumoRamo, x="Timestamp", y=consumoRamo["Consumo"].rolling(4).mean(), color='Ramo', title='Consumo de energia por ramo')
figRamo.update_layout(xaxis_title='Data', yaxis_title='Consumo (MWh)')
figRamo.update_layout(
    xaxis=dict(
        rangeselector=dict(
            
            buttons=list([
                dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)
figRamo

#Create a scatter with the avarage consumption by day of the week
figScatter = px.scatter(df.groupby(['DiaSem'])['Consumo'].mean().reset_index().sort_values(['Consumo'],ascending=True),
                x='DiaSem', y='Consumo') #, title='O consumo é afetado pelo final de semana?',
#mapeia o dia da semana para o nome do dia
                
figScatter.update_xaxes(ticktext=['Segunda','Terça','Quarta','Quinta','Sexta','Sábado','Domingo'],
                    tickvals=[0,1,2,3,4,5,6])

figScatter.update_layout(xaxis_title='Dia da semana', yaxis_title='Consumo (MWh)')

figScatter

consumoBrasil

#Adiciona a estação do ano ao dataframe
df['Estacao'] = df['Timestamp'].dt.month%12 // 3 + 1
df['Estacao'] = df['Estacao'].replace(1, 'Inverno')
df['Estacao'] = df['Estacao'].replace(2, 'Primavera')
df['Estacao'] = df['Estacao'].replace(3, 'Verão')
df['Estacao'] = df['Estacao'].replace(4, 'Outono')

consumoData = ACL_df.groupby(['Timestamp'])['Consumo'].sum()/1000

consumoData

consumoData = consumoData.reset_index()
consumoData.columns = ['Timestamp', 'Consumo']

consumoData['Estacao'] = consumoData['Timestamp'].dt.month%12 // 3 + 1
consumoData['Estacao'] = consumoData['Estacao'].replace(1, 'Inverno')
consumoData['Estacao'] = consumoData['Estacao'].replace(2, 'Primavera')
consumoData['Estacao'] = consumoData['Estacao'].replace(3, 'Verão')
consumoData['Estacao'] = consumoData['Estacao'].replace(4, 'Outono')

import holidays

#Adiciona os feriados no dataframe
df['Feriado'] = df['Timestamp'].dt.date.astype('datetime64').isin(holidays.Brazil(years=[2018,2019,2020]).keys())

dataWeather = pd.read_csv('https://raw.githubusercontent.com/JoaoYukio/projetoPCO114/main/dadosComClima.csv', sep=',')#pd.read_csv('dadosComClima.csv', sep=',')

#Convert the date string to datetime
dataWeather['Timestamp'] = pd.to_datetime(dataWeather['Timestamp'])

#Remove the data before july 2018 and after july 2020
dataWeather = dataWeather[dataWeather['Timestamp'] >= '2018-07-01']
dataWeather = dataWeather[dataWeather['Timestamp'] <= '2020-06-19']

dataWeather['Estacao'] = dataWeather['Timestamp'].dt.month%12 // 3 + 1
dataWeather['Estacao'] = dataWeather['Estacao'].replace(1, 'Inverno')
dataWeather['Estacao'] = dataWeather['Estacao'].replace(2, 'Primavera')
dataWeather['Estacao'] = dataWeather['Estacao'].replace(3, 'Verão')
dataWeather['Estacao'] = dataWeather['Estacao'].replace(4, 'Outono')

#plota a media movel de 7 dias do consumo de energia do dataset dataWeather
fig7 = px.line(dataWeather, x = dataWeather["Timestamp"], y = dataWeather["Consumo"].rolling(window=4).mean(),title='Consumo de energia média móvel de 4 dias')
fig7.update_layout(xaxis_title='Data', yaxis_title='Consumo (MWh)')
#Add a candlestick chart
meanData=dataWeather["Consumo"].rolling(window=4).mean()
fig7.add_trace(go.Candlestick(x=dataWeather["Timestamp"],
                open=meanData,
                high=meanData*1.02,
                low=meanData*0.98,
                close=meanData,
                name = 'Candlestick'))
fig7.update_layout(
    xaxis=dict(
        rangeselector=dict(
            
            buttons=list([
                dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)
fig7

figEstacao = px.line(dataWeather, x = dataWeather['Timestamp'], y = dataWeather['Consumo'].rolling(window=4).mean(),title='Consumo de energia média móvel de 4 dias')#, color = 'Estacao'
figEstacao.add_scatter(x=dataWeather[dataWeather['Estacao'] == 'Verão']['Timestamp'], y=dataWeather[dataWeather['Estacao'] == 'Verão']['Consumo'].rolling(window=4).mean(), mode='markers', name='Verão')
figEstacao.add_scatter(x=dataWeather[dataWeather['Estacao'] == 'Outono']['Timestamp'], y=dataWeather[dataWeather['Estacao'] == 'Outono']['Consumo'].rolling(window=4).mean(), mode='markers', name='Outono')
figEstacao.add_scatter(x=dataWeather[dataWeather['Estacao'] == 'Inverno']['Timestamp'], y=dataWeather[dataWeather['Estacao'] == 'Inverno']['Consumo'].rolling(window=4).mean(), mode='markers', name='Inverno')
figEstacao.add_scatter(x=dataWeather[dataWeather['Estacao'] == 'Primavera']['Timestamp'], y=dataWeather[dataWeather['Estacao'] == 'Primavera']['Consumo'].rolling(window=4).mean(), mode='markers', name='Primavera')
figEstacao.update_layout(xaxis_title='Data', yaxis_title='Consumo (MWh)')
#Add a data range slider
figEstacao.update_layout(
    xaxis=dict(
        rangeselector=dict(
            
            buttons=list([
                dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)
figEstacao

#Remove the estacao from dataWeather
dataWeather = dataWeather.drop(['Estacao'], axis=1)

consumoBrasil = consumoBrasil[consumoBrasil['Timestamp'] >= '2018-07-01']
consumoBrasil = consumoBrasil[consumoBrasil['Timestamp'] <= '2020-06-19']

#Plota os dados de radiacao solar
figSolar = px.line(dataWeather, x = dataWeather['Timestamp'], y = dataWeather['Radiacao'].rolling(5).mean(), title='Radiacao Solar')
figSolar.update_layout(xaxis_title='Data', yaxis_title='Radiacao (W/m²)')
figSolar.update_layout(
    xaxis=dict(
        rangeselector=dict(
            
            buttons=list([
                dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

#Plota os dados de temperatura
figTemp = px.line(dataWeather, x = dataWeather['Timestamp'], y = dataWeather['Temperatura'], title='Temperatura')
figTemp.update_layout(xaxis_title='Data', yaxis_title='Temperatura (°C)')
figTemp.update_layout(
    xaxis=dict(
        rangeselector=dict(
            
            buttons=list([
                dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

#Plota os dados de umidade
figUmidade = px.line(dataWeather, x = dataWeather['Timestamp'], y = dataWeather['Umidade'], title='Umidade' )
figUmidade.update_layout(xaxis_title='Data', yaxis_title='Umidade (%)')
figUmidade.update_layout(
    xaxis=dict(
        rangeselector=dict(
            
            buttons=list([
                dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

#Verificando se tem correlacao entre o clima e o consumo de energia
figCorrTemp = px.scatter(dataWeather, x='Temperatura', y='Consumo', title='Existe correlacao? (Consumo x Temperatura)', trendline="ols")
figCorrTemp.update_layout(xaxis_title='Temperatura (°C)', yaxis_title='Consumo (MWh)')

dataWeather['Consumo'].corr(dataWeather['Temperatura'])

figCorrRad = px.scatter(dataWeather, x='Radiacao', y='Consumo', title='Existe correlacao? (Consumo x Radiacao)', trendline="ols")
figCorrRad.update_layout(xaxis_title='Radiacao (W/m²)', yaxis_title='Consumo (MWh)')

dataWeather['Consumo'].corr(dataWeather['Radiacao'])

figCorrRadTemp = px.scatter(dataWeather, x='Radiacao', y='Temperatura', title='Existe correlacao? (Temperatura x Radiacao)', trendline="ols")
figCorrRadTemp.update_layout(xaxis_title='Radiacao (W/m²)', yaxis_title='Temperatura (°C)')

dataWeather['Temperatura'].corr(dataWeather['Radiacao'])

figCorrUmid = px.scatter(dataWeather, x='Umidade', y='Consumo', title='Existe correlacao? (Consumo x Umidade)', trendline="ols")
figCorrUmid.update_layout(xaxis_title='Umidade (%)', yaxis_title='Consumo (MWh)')

dataWeather['Consumo'].corr(dataWeather['Umidade'])

#Adiciona se o dia é feriado ou não
dataWeather['Feriado'] = dataWeather['Timestamp'].dt.date.astype('datetime64').isin(holidays.Brazil(years=[2018,2019,2020]).keys())

#dataWeather.to_csv('dadosComClima.csv', sep=',', index=False)

"""Parte de IA"""

#TODO: Dar uma olhada entre consumoData e dataWeather, ver se tem diferencas

# Usa 90% dos dados para treino e 10% para teste
train_size = int(len(dataWeather) * 0.9)
test_size = len(dataWeather) - train_size
train, test = dataWeather[0:train_size], dataWeather[train_size:len(dataWeather)]

test

#Cria um dataset de treino contendo dia da semana, mes, ano e dia do ano a partir da coluna Timestamp
train['dayofweek'] = train['Timestamp'].dt.dayofweek
train['quarter'] = train['Timestamp'].dt.quarter
train['month'] = train['Timestamp'].dt.month
train['year'] = train['Timestamp'].dt.year
train['dayofyear'] = train['Timestamp'].dt.dayofyear
train['dayofmonth'] = train['Timestamp'].dt.day
train['weekofyear'] = train['Timestamp'].dt.weekofyear

#Add estações do ano
train['Estacao'] = train['Timestamp'].dt.month%12 // 3 + 1

#Cria um dataset de teste contendo dia da semana, mes, ano e dia do ano a partir da coluna Timestamp
test['dayofweek'] = test['Timestamp'].dt.dayofweek
test['quarter'] = test['Timestamp'].dt.quarter
test['month'] = test['Timestamp'].dt.month
test['year'] = test['Timestamp'].dt.year
test['dayofyear'] = test['Timestamp'].dt.dayofyear
test['dayofmonth'] = test['Timestamp'].dt.day
test['weekofyear'] = test['Timestamp'].dt.weekofyear

#Add estações do ano
test['Estacao'] = test['Timestamp'].dt.month%12 // 3 + 1

XTrain = train.drop(['Timestamp', 'Consumo', 'Umidade','Radiacao'], axis = 1)

XTrain

consumoData["Consumo"][0:train_size]

YTrain = train['Consumo']

XTest = test.drop(['Timestamp', 'Consumo', 'Umidade','Radiacao'], axis = 1)

YTest = test['Consumo']

import xgboost as xgb
from xgboost import plot_importance, plot_tree
from sklearn.metrics import mean_squared_error, mean_absolute_error

reg = xgb.XGBRegressor(n_estimators=1000)
reg.fit(XTrain, YTrain,
        eval_set=[(XTrain, YTrain), (XTest, YTest)],
        early_stopping_rounds=50,
       verbose=False) # Change verbose to True if you want to see it train

sorted_idx = reg.feature_importances_.argsort()

feature_important = reg.get_booster().get_score(importance_type='weight')

keys = list(feature_important.keys())
values = list(feature_important.values())

modelData = pd.DataFrame(data=values, index=keys, columns=["score"]).sort_values(by = "score", ascending=True)

modelData = modelData.reset_index()
modelData.columns = ['Feature', 'Importance']

figImp = px.bar(y=modelData['Feature'], x=modelData['Importance'], title='Feature Importance', orientation='h')
figImp.update_layout(xaxis_title='Importancia', yaxis_title='Feature')
figImp

#Create a bar plot using px with the feature importance of the model <- NAO FUNCIONOU BEM NO COLAB
#figImp = px.bar(y=reg.feature_names_in_[sorted_idx], x=reg.feature_importances_[sorted_idx], title='Feature Importance', orientation='h')
#figImp.update_layout(xaxis_title='Feature', yaxis_title='Importance')
#figImp

XTest

resTest = reg.predict(XTest)

#Create a line plot using px line with the train data, test data and the prediction
forecast = px.line(train, x = 'Timestamp', y = 'Consumo', title = 'Consumo de Energia')
forecast.add_scatter(x = test['Timestamp'], y = test['Consumo'], mode = 'lines', name = 'Test')
forecast.add_scatter(x = test['Timestamp'], y = resTest, mode = 'lines', name = 'Prediction')
forecast.update_layout(
    xaxis=dict(
        rangeselector=dict(
            
            buttons=list([
                dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

forecast.show()

#Calcula o erro absoluto medio
mae = mean_absolute_error(YTest, resTest)
print('MAE: %.3f' % mae)

app = jupyter_dash.JupyterDash(__name__)

consumoEstado

#Create a dict for the dropdown with the states
optionsUF = [{'label': i, 'value': i} for i in ACL_df['UF'].unique()]
for i in optionsUF:
    i['label'] = i['label'].replace("\xa0", "")
    i['value'] = i['value'].replace("\xa0", "")

ACL_df["UF"] = ACL_df["UF"].str.replace("\xa0", "")

#Calcula a media de consumo quando e feriado ou nao
consumoFeriado = dataWeather.groupby(['Feriado'])['Consumo'].mean().reset_index()

print(consumoFeriado)

#Plota o consumo de um grafico de linha e indica se o dia é feriado ou nao
figConsumoFeriado = px.line(dataWeather, x = 'Timestamp', y = 'Consumo', title = 'Consumo de Energia')
figConsumoFeriado.add_scatter(x = dataWeather[dataWeather['Feriado']]['Timestamp'], y = dataWeather[dataWeather['Feriado']]['Consumo'],mode = 'markers', name = 'Feriado')
figConsumoFeriado.update_layout(xaxis_title='Feriado', yaxis_title='Consumo (MWh)')
figConsumoFeriado.update_layout(
    xaxis=dict(
        rangeselector=dict(
            
            buttons=list([
                dict(count=1,
                        label="1m",
                        step="month",
                        stepmode="backward"),
                dict(count=6,
                        label="6m",
                        step="month",
                        stepmode="backward"),
                dict(count=1,
                        label="1y",
                        step="year",
                        stepmode="backward"),
                dict(step="all")
            ])
        ),
        rangeslider=dict(
            visible=True
        ),
        type="date"
    )
)

#Calcula a correlacao entre as variaveis
correlacao = dataWeather.corr()
correlacao

app.layout = html.Div([
    html.H1("Visão Geral do Consumo de Energia no Brasil", style={'text-align': 'center'}),
    
    html.H2("Como é o consumo de energia no Brasil?", style={'text-align': 'center'}),
    dcc.Graph(figure=figMap),
    html.H2("Como está composto o consumo de energia em cada estado?", style={'text-align': 'center'}),
    #Add fig5
    dcc.Graph(figure=treeMap),
    dbc.Row(
        [
            dbc.Col([
                html.H3("Selecione os estados que deseja visualizar de forma mais detalhada:", style={'text-align': 'center'}),
                dcc.Dropdown(id='dropEstado',options=optionsUF, value= ['SP'], multi=True),
            ]),
        ]
    ),
    dcc.Graph(id = 'rankInd',figure=rankInd),
    html.H1("Consumo de Energia ao longo do tempo", style={'text-align': 'center'}),
    html.H2("Como o consumo varia por UF? (Selecione os estados no lado direito)", style={'text-align': 'center'}),
    dcc.Graph(figure=lineUf),
    html.H2("Como o consumo varia por Ramo? (Selecione os ramos no lado direito)", style={'text-align': 'center'}),
    dcc.Graph(figure = figRamo),
    html.H2("Como o consumo varia de acordo com a estação do ano? (Selecione a estação no lado direito)", style={'text-align': 'center'}),
    dcc.Graph(figure=figEstacao),
    html.H2("Como o consumo varia com o dia da semana?", style={'text-align': 'center'}),
    dcc.Graph(figure=figScatter),
    html.H2("Qual a tendencia de queda e aumento do consumo?", style={'text-align': 'center'}),
    dcc.Graph(figure=fig7),
    html.H2("Feriados afetam o consumo?", style={'text-align': 'center'}),
    dcc.Graph(figure=figConsumoFeriado),
    html.H1("Fatores climaticos influenciam no consumo?", style={'text-align': 'center'}),
    html.H2("Como os fatores climaticos variam com o ano?", style={'text-align': 'center'}),
    dcc.Graph(figure=figTemp),
    dcc.Graph(figure=figSolar),
    dcc.Graph(figure=figUmidade),
    html.H2("Qual a correlação entre o consumo e a temperatura?", style={'text-align': 'center'}),
    dcc.Graph(figure=figCorrTemp),
    html.H2("Qual a correlação entre o consumo e a umidade?", style={'text-align': 'center'}),
    dcc.Graph(figure=figCorrUmid),
    html.H2("Qual a correlação entre o consumo e a radiação solar?", style={'text-align': 'center'}),
    dcc.Graph(figure=figCorrRad),
    html.H2("Qual a correlação entre a temperatura e a radiação solar?", style={'text-align': 'center'}),
    dcc.Graph(figure=figCorrRadTemp),
    html.P("Percebemos que a umidade não tem uma correlação muito forte com o consumo, mas a temperatura e a radiação solar tem uma correlação forte com o consumo, além disso, a temperatura e a radiação solar tem uma correlação forte entre si."),
    html.P("A correlação entre a temperatura e a consumo é de: " + str(correlacao['Consumo']['Temperatura'])),
    html.P("A correlação entre a umidade e a consumo é de: " + str(correlacao['Consumo']['Umidade'])),
    html.P("A correlação entre a radiação solar e a consumo é de: " + str(correlacao['Consumo']['Radiacao'])),
    html.P("A correlação entre a temperatura e a radiação solar é de: " + str(correlacao['Temperatura']['Radiacao'])),

    html.H1("Forecasting do consumo", style={'text-align': 'center'}),
    html.H3("Com base nas perguntas anteriores foi feito um modelo usando XGBoost"),
    html.H3("Os dados de treinamento foram: Temperatura, Feriados, Estação do ano e Dados provenientes da data"),
    html.H3("Foi feito forecasting do dia 09/04/2020 a 19/06/2020"),
    html.H3("As features mais importantes de acordo com o modelo foram: "),
    dcc.Graph(figure= figImp),
    html.H2("Temos a seguinte serie com a predição: "),
    dcc.Graph(figure= forecast),
    html.H3("O erro absoluto medio do modelo foi de: "),
    html.P(str(mae) + " MWh")
])

#Callback for the dropdown
@app.callback(
    Output('rankInd', 'figure'),
    Input('dropEstado', 'value')
)
def update_graph(dropEstado):
    dataFilt = ACL_df[ACL_df['UF'].isin(dropEstado)]
    b = dataFilt.groupby(['Ramo','UF'])['Consumo'].sum()
    b=b.reset_index().sort_values(['Consumo'],ascending=False)
    rankInd = px.bar(b.groupby(['Ramo'])['Consumo'].mean().reset_index().sort_values(['Consumo'],ascending=True),
                y='Ramo', x='Consumo', orientation='h') #color='Ramo',
    rankInd.update_layout(xaxis_title='Consumo (MWh)', yaxis_title='Ramo')
    return rankInd

app.run_server() #<- roda no navegador
#app.run_server(mode='inline',host="0.0.0.0",port=1005) # <- roda direto no colab