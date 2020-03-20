import analisadores as ana
import pandas as pd
import numpy as np
from datetime import date

def backtesting_cross(tick,mode='sma',window1=7,window2=21,inicio='2014-01-01',fim=date.today(),max_loss = 0.95,min_gain=1.05,graphic=True,window_ifr=14,sup=70,inf=30,op_loss=0,window_ema9=9):
    '''Tick = código ação
        mode = sma/ema/ifr
        window1 = periodo rapido
        window2 = periodo lento
        inicio = inicio do periodo
        fim = final do periodo
        max_loss = perda máxima
        min_gain = ganho minimo para parcial
        graphic = ver grafico após o modelo rodar True/False
        window_ifr = janela para o indice de força relativa
        sup = intervalo superior ifr
        inf = intervalo inferior ifr'''
    #verifica o tipo de setup
    if mode == 'sma':
        df = ana.cross_sma(tick,inicio,fim,window1,window2)
    elif mode == 'ema':
        df = ana.cross_ema(tick,inicio,fim,window1,window2)
    elif mode == 'ifr':
        df = ana.sinal_ifr(tick,inicio,fim,window_ifr,sup,inf)
    elif mode == 'ema9':
        df = ana.ema9_1(tick,inicio,fim,window_ema9)
    else:
        df = ana.cross_ema(tick,inicio,fim,window1,window2)
    #define os valores de compra e venda do modelo
    df['buy'] = np.where((df['High']>=df.shift(1)['start']),df.shift(1)['start'],0)
    df['sell'] = np.where((df['Low']<=df.shift(1)['stop']),df.shift(1)['stop'],0)
    #inicia as variaveis
    purchased = 0
    price_buy = 0
    amount = 0
    min_first = 0
    yesterday = 0
    #cria os dataframes dos graficos
    buys = pd.DataFrame(columns=['date','price'])
    sells = pd.DataFrame(columns=['date','price'])
    #Inicio do loop
    for x in df.index:
        day = df.loc[x]
        #verifica se não tem nada comprado e se tem sinal de compra
        if purchased == 0 and day['buy']>0:
            price_buy = round(day['buy'],2)
            if op_loss == 0:
                stop_loss = round(price_buy * max_loss,2)
            else:
                stop_loss = round(yesterday['Low'] - 0.05,2)
            amount -= price_buy
            purchased = 1
            min_first = 0
            print("*Compra no valor de: {}*".format(price_buy))            
            new_row = {'date':x, 'price':price_buy}
            buys = buys.append(new_row,ignore_index=True)
        #verifica se está comprado e tem sinal de venda   
        if purchased == 1 and day['sell']>0:
            price_buy = 0
            purchased = 0
            amount += round(day['sell'],2)
            print("Venda no valor de: {}".format(round(day['sell'],2)))
            new_row = {'date':x, 'price':round(day['sell'],2)}
            sells = sells.append(new_row,ignore_index=True)
            parc = round(amount+price_buy,2)   
            print('Lucro atual: R${}'.format(parc))
        #verifica se está comprado e foi stopado
        if purchased == 1 and day['Low'] <= stop_loss:
            #verifica se stop é maior que o valor do dia, caso tenha aberto em gap
            if stop_loss >= day['High']:
                price_sell = round(day['Low'],2)
            else:
                price_sell = round(stop_loss, 2)
            price_buy = 0
            purchased = 0
            amount += price_sell
            new_row = {'date':x, 'price':round(price_sell,2)}
            sells = sells.append(new_row,ignore_index=True)
            print("Stopado no valor de: {}".format(price_sell))
            parc = round(amount+price_buy,2)   
            print('Lucro atual: R${}'.format(parc))
            
        #verifica se é a primeira parcial  
        if (purchased == 1) and (day['High']>=price_buy*min_gain) and (min_first==0):
            stop_loss = round(day['High'] * max_loss,2)
            min_first = 1
        #cria outras parciais
        if (purchased == 1) and (day['High']>=stop_loss*min_gain) and (min_first==1):
            stop_loss = round(day['High'] * max_loss,2)
        yesterday = df.loc[x]
    

    
    if graphic:
        graphics(df,buys,sells)
    
#gera o gráfico   
def graphics(df,buys,sells):
    import plotly.graph_objects as go
    stock = go.Candlestick(x=df.index,
                        open=df['Open'],
                        high=df['High'],
                        low=df['Low'],
                        close=df['Close'])
    entry = go.Scatter(x=buys['date'], y=buys['price'],
                    mode='markers',
                    marker=dict(color='rgb(0,0,0)'),
                    name='Entrys')
    exits = go.Scatter(x=sells['date'], y=sells['price'],
                    mode='markers',
                    marker=dict(color='rgb(0,0,255)'),
                    name='Exits')
    
    fig = go.Figure(data=[stock,entry,exits])
    fig.write_html('fig_backtest.html', auto_open=True)
    
        
            
            
        