from flask import Flask, render_template, request, redirect, url_for, flash
import os
import datetime
#import pandas as pd
import pandas_datareader as web
#from pandas.util.testing import assert_frame_equal


# Start a server
app = Flask(__name__)

# setting
app.secret_key = 'mysecretkey'

def ObtainDate(pDate):
    try:  # strptime throws an exception if the input doesn't match the pattern
        d = datetime.datetime.strptime(pDate, "%m/%d/%Y")
    except:
        print('Incorrect date format\n')
        flash('Invalid date format. Please, input a valid date.')
        d = ''

    return d

# app.route(/) use for decorate, always someone visit our page we display "Hello World!"
@app.route('/')
def Index():
    return render_template('index.html')


@app.route('/create_stocks', methods=['POST'])
def create_stocks():

    # read ticker symbols from the text area
    StockTextarea = request.form['StockTextarea'].upper()

    if StockTextarea.strip() == '':
        flash('Please, Input Stocks on Stock Area')
        return redirect(url_for('Index'))

    symbol = StockTextarea.split(',')
    
    # Get End Date
    ED = ObtainDate(request.form['lastdate'])
    
    #Print if there is a error with the date ED
    if ED == '':
        return redirect(url_for('Index'))

   # Get Current Date
    TD = datetime.date.today()

    #Print if there is a error with the date ED
    if ED.strftime("%Y%m%d") > TD.strftime("%Y%m%d"):
        flash('The date can not higher than today')
        return redirect(url_for('Index'))        

    # Get number of days<
    SD = (ED - datetime.timedelta(days=18))


    tree_stocks = {}

    for stock in symbol:
        try:
            #get prices info 
            f = web.DataReader(stock, 'yahoo', SD, ED)        
       
            date_index = len(f)

            if date_index > 0:
                date_index = date_index - 1
            
            tree_stock = {}    

            #Build List Dates
            list_dates = []   

            list_dates.append('Date')     
        
            for i in range(len(f)):
                if i == 0:
                    list_dates.append(f.index[date_index - i].strftime("%Y-%m-%d"))
                else:
                    list_dates.append(f.index[date_index - i].strftime("%Y-%m-%d"))

            #Build List Prices
            list_prices = []
            
            list_prices.append('Close Price')

            for i in range(len(f)):
                if i == 0:
                    list_prices.append("{:.2f}".format(f.loc[f.index[date_index - i],'Close']))
                else:
                    list_prices.append("{:.2f}".format(f.loc[f.index[date_index - i],'Close']))        

            #tree_stocks[stock+'0'] = info_stock.info['industry']
            #tree_stocks[stock+'1'] = info_stock.calendar.loc[info_stock.calendar.index[0],'Value'].strftime("%Y-%m-%d")
            #tree_stocks[stock+'1'] = stock
            tree_stock[stock+'0'] = 'DATA_FOUND'
            tree_stock[stock+'1'] = list_dates
            tree_stock[stock+'2'] = list_prices        

            print("Symbol: " + stock)
   
        except:
            tree_stock = {}
            tree_stock[stock+'0'] = 'NO_DATA_FOUND'
            tree_stock[stock+'1'] = 'There is no information for the symbol'
            tree_stocks[stock] = tree_stock
            continue 

        tree_stocks[stock] = tree_stock 

    return render_template('create_stocks.html', pTreeStocks=tree_stocks)

if __name__ == '__main__':
    # debug--> Use when we had changes into the server so restart the server
    app.run()
    print('Successful')
else:
    print('Error')
