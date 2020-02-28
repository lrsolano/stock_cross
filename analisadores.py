import pandas as pd
import numpy as np
import tulipy as ti
from datetime import date
from pandas_datareader import data as wb

#Retorna a informações das ações no intervalo definido
def data_stock(tick,inicio='2014-01-01',fim=date.today()):
    df=wb.DataReader(tick,'yahoo',inicio,fim)
    return df

#Cria o DataFrame da media movel exponencial
def return_ema(tick,inicio='2014-01-01',fim=date.today(),window=7,colum='ema'):
    df=wb.DataReader(tick,'yahoo',inicio,fim)
    emas = ti.ema(df['Close'].values,window)
    #Cria o DataFrame com os valores da media movel e usa a data como indice
    emas = pd.DataFrame(data = emas, index = df.index, columns = [colum])
    return emas

#Cria o DataFrame da media movel simples
def return_sma(tick,inicio='2014-01-01',fim=date.today(),window=7,colum='sma'):
    df=wb.DataReader(tick,'yahoo',inicio,fim)
    smas = ti.sma(df['Close'].values,window)
     #Cria o DataFrame com os valores da media movel e usa a data como indice
    smas = pd.DataFrame(data = smas, index = df.index[(window-1):], columns=[colum])
    return smas

#Setup do cruzamento de médias móveis simples
def cross_sma(tick,inicio='2014-01-01',fim=date.today(),window1=7,window2=21):
    #Cria as médias moveis com o periodo informado
    sma1 = return_sma(tick,inicio,fim,window1,colum='sma1')
    sma2 = return_sma(tick,inicio,fim,window2,colum='sma2')
    #Busca as informações da ação
    stocks =  data_stock(tick,inicio,fim)
    #Une os dataframes
    df = pd.concat([stocks,sma1, sma2], axis=1, join='inner')
    #Cria a coluna de diferença das médias moveis
    df['dif'] = (df['sma1'] - df['sma2'] )
    #Cria a coluna co os valores de entrada quando o setup armar
    df['start'] = np.where((df['dif']>=0) & (df.shift(1)['dif']<=0),df['High'],np.NaN)
    df['stop'] =  np.where((df['dif']<=0) & (df.shift(1)['dif']>=0),df['Low'],np.NaN)
    #separa os pontos de entrada
    entry_points = df[df['start']>0]['start']
    exit_points = df[df['stop']>0]['stop']
    #plota o grafico
    import plotly.graph_objects as go
    stock = go.Candlestick(x=df.index,
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'])
    entry = go.Scatter(x=entry_points.index, y=entry_points.values,
                    mode='markers',
                    marker=dict(color='rgb(0,0,0)'),
                    name='Entrys')
    exits = go.Scatter(x=exit_points.index, y=exit_points.values,
                    mode='markers',
                    marker=dict(color='rgb(0,0,255)'),
                    name='Entrys')
    ema_fast = go.Scatter(x=df.index, 
                       y=df['sma1'],
                       mode='lines',
                       line=dict(color='rgb(255,20,147)'),
                       name='sma fast')
    ema_slow = go.Scatter(x=df.index, 
                       y=df['sma2'],
                       mode='lines',
                       line=dict(color='rgb(210,105,30)'),
                       name='sma slow')
    
    fig = go.Figure(data=[stock,entry,ema_fast,ema_slow,exits])
    fig.write_html('fig_cross_sma.html', auto_open=False)
    return df

#Setup do cruzamento de médias móveis exponenciais
def cross_ema(tick,inicio='2014-01-01',fim=date.today(),window1=7,window2=21):
    #Cria as médias moveis com o periodo informado
    ema1 = return_ema(tick,inicio,fim,window1,colum='ema1')
    ema2 = return_ema(tick,inicio,fim,window2,colum='ema2')
    #Busca as informações da ação
    stocks =  data_stock(tick,inicio,fim)
    #Une os dataframes
    df = pd.concat([stocks,ema1, ema2], axis=1, join='inner')
    #Cria a coluna de diferença das médias moveis
    df['dif'] = (df['ema1'] - df['ema2'] )
    #Cria a coluna co os valores de entrada quando o setup armar
    df['start'] = np.where((df['dif']>=0) & (df.shift(1)['dif']<=0),df['High'],np.NaN)
    df['stop'] =  np.where((df['dif']<=0) & (df.shift(1)['dif']>=0),df['Low'],np.NaN)
    #separa os pontos de entrada
    entry_points = df[df['start']>0]['start']
    exit_points = df[df['stop']>0]['stop']
    #plota o grafico
    import plotly.graph_objects as go
    stock = go.Candlestick(x=df.index,
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'])
    entry = go.Scatter(x=entry_points.index, y=entry_points.values,
                    mode='markers',
                    marker=dict(color='rgb(0,0,0)'),
                    name='Entrys')
    ema_fast = go.Scatter(x=df.index, 
                       y=df['ema1'],
                       mode='lines',
                       line=dict(color='rgb(255,20,147)'),
                       name='ema fast')
    ema_slow = go.Scatter(x=df.index, 
                       y=df['ema2'],
                       mode='lines',
                       line=dict(color='rgb(210,105,30)'),
                       name='ema slow')
    exits = go.Scatter(x=exit_points.index, y=exit_points.values,
                    mode='markers',
                    marker=dict(color='rgb(0,0,255)'),
                    name='Entrys')
    
    fig = go.Figure(data=[stock,entry,ema_fast,ema_slow,exits])
    fig.write_html('fig_cross_ema.html', auto_open=False)
    return df

    
      


  
   