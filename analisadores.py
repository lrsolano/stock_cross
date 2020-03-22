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
#Cria o DataFrame do indice de força relativa
def return_ifr(tick,inicio='2014-01-01',fim=date.today(),window=7,colum='ifr'):
    df=wb.DataReader(tick,'yahoo',inicio,fim)
    #retorna o indice de força relativa 
    ifrs = ti.rsi(df['Close'].values,window)
     #Cria o DataFrame com os valores da media movel e usa a data como indice
    ifrs = pd.DataFrame(data = ifrs, index = df.index[(window):], columns=[colum])
    return ifrs

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
    #Cria a coluna com os valores de entrada quando o setup armar
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
    #Cria a coluna com os valores de entrada quando o setup armar
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

def sinal_ifr(tick,inicio='2014-01-01',fim=date.today(),window=14,sup=70,inf=30):
    #cria o dataframe com o indice de força relativa
    ifrs = return_ifr(tick,inicio,fim,window)
    #Busca as informações da ação
    stocks =  data_stock(tick,inicio,fim)
    #Une os dataframes
    df = pd.concat([stocks,ifrs], axis=1, join='inner')
    #Cria a coluna com os valores de entrada quando o setup armar
    df['start'] = np.where((df['ifr']<=inf) & (df.shift(1)['ifr']>=df['ifr']),df['High'],np.NaN)
    df['stop'] =  np.where((df['ifr']>=sup) & (df.shift(1)['ifr']<=df['ifr']),df['Low'],np.NaN)
    #separa os pontos de entrada
    entry_points = df[df['start']>0]['start']
    exit_points = df[df['stop']>0]['stop']
    #plota o grafico
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    fig = make_subplots(rows=2, cols=1)
    
    fig.add_trace(go.Candlestick(x=df.index,
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close']), row=1,col=1)
    fig.add_trace(go.Scatter(x=entry_points.index, y=entry_points.values,
                    mode='markers',
                    marker=dict(color='rgb(0,0,0)'),
                    name='Entrys'),row=1,col=1)
    fig.add_trace(go.Scatter(x=exit_points.index, y=exit_points.values,
                    mode='markers',
                    marker=dict(color='rgb(0,0,255)'),
                    name='Exits'),row=1,col=1)
    fig.add_trace(go.Scatter(x=df.index, 
                       y=df['ifr'],
                       mode='lines',
                       line=dict(color='rgb(255,20,147)'),
                       name='ifr'),row=2,col=1)
    fig.write_html('fig_ifr.html', auto_open=False)
    return df
#Setup 9.1
def ema9_1(tick,inicio='2014-01-01',fim=date.today(),window=9):
    emas = return_ema(tick,inicio,fim,window)
    #Busca as informações da ação
    stocks =  data_stock(tick,inicio,fim)
    #Une os dataframes
    df = pd.concat([stocks,emas], axis=1, join='inner')
    #Retorna inclinação da média
    df['dif'] = df['ema'] - df.shift(1)['ema']
    #Setup aberto
    df['start'] = np.where((df['dif']>0)  & (df.shift(1)['dif']<0) & (df['ema']>df['Low']) & (df['ema']<df['High']),df['High'],np.NaN)
    df['stop'] = np.where((df['dif']<0) & (df.shift(1)['dif']>0) & (df['ema']>df['Low']) & (df['ema']<df['High']),df['Low'],np.NaN)

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
    ema = go.Scatter(x=df.index, 
                       y=df['ema'],
                       mode='lines',
                       line=dict(color='rgb(255,20,147)'),
                       name='ema')
    exits = go.Scatter(x=exit_points.index, y=exit_points.values,
                    mode='markers',
                    marker=dict(color='rgb(0,0,255)'),
                    name='exits')
    
    fig = go.Figure(data=[stock,entry,ema,exits])
    fig.write_html('fig_ema9_1.html', auto_open=False)
    return df
    
      


  
   