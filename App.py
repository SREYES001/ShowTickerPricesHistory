from flask import Flask, render_template, request, redirect, url_for, flash
import os
import datetime
#import pandas as pd
import pandas_datareader as web
#from pandas.util.testing import assert_frame_equal
from yahoo_earnings_calendar import YahooEarningsCalendar
from yahooquery import Ticker


# Start a server
app = Flask(__name__)

# setting
app.secret_key = 'mysecretkey'

def ObtainDate(pDate):
    try:  # strptime throws an exception if the input doesn't match the pattern
        d = datetime.datetime.strptime(pDate, "%Y-%m-%d")
    except:
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
    StockTextarea = request.form['StockTextarea'].upper().replace(" ", "")

    if StockTextarea.strip() == '':
        flash('Please, Enter tickers on ticker Area')
        return redirect(url_for('Index'))

    symbol = StockTextarea.split(',')

    if len(symbol) > 10:
        flash('Please, Enter 10 tickers maximum')
        return redirect(url_for('Index'))

    # Get Start Date
    SD = ObtainDate(request.form['datefrom'])
     
    #Print if there is a error with the date SD
    if SD == '':
        return redirect(url_for('Index'))    
    
    # Get End Date
    ED = ObtainDate(request.form['dateto'])
    
    #Print if there is a error with the date ED
    if ED == '':
        return redirect(url_for('Index'))

   # Get Current Date
    TD = datetime.date.today()

   #Print if there is a error with the date ED
    if SD.strftime("%Y%m%d") > TD.strftime("%Y%m%d"):
        flash('The start date can not higher than today')
        return redirect(url_for('Index'))  

    #Print if there is a error with the date ED
    if ED.strftime("%Y%m%d") > TD.strftime("%Y%m%d"):
        flash('The end date can not higher than today')
        return redirect(url_for('Index'))  

    #Print if there is a error with the date ED
    if ED <  SD:
        flash('The end date can''t be less than the start date')
        return redirect(url_for('Index'))           

    # Get number of days<
    dt = (ED - SD)
    countDays = dt.days

    if countDays > 20:
        flash('The count of the days can not be greater than 20 days')
        return redirect(url_for('Index')) 

    tree_stocks = {}

    #Set earnigs
    yec = YahooEarningsCalendar()

    m = Ticker(symbol)

    for stock in symbol:
        try:
            #get prices info 
            f = web.DataReader(stock, 'yahoo', SD, ED)

            l_count_stock = len(f)
            
            try:
                #get earnig date            
                yec_date = (datetime.date.fromtimestamp(yec.get_next_earnings_date(stock)))
                yec_count = (yec_date - TD).days

                if yec_count > 1:
                    yec_desc = str(yec_count) + ' days to earnings call'
                else:
                    if yec_count >= 0:
                        yec_desc = str(yec_count) + ' day to earnings call'
                    else:
                        yec_desc = ''

            except:
                yec_desc = ''    

            try:
                #get Name and Industry
                l_current_price = m.financial_data[stock]['currentPrice']
                current_price = str(l_current_price)
            except:
                l_current_price = 0
                current_price = ''                

            try:
                #get Name and Industry
                stock_name = m.price[stock]['longName']
                stock_industry = 'Industry: ' + m.asset_profile[stock]['industry']
            except:
                stock_name = ''
                stock_industry = ''

            date_index = l_count_stock

            #count dates
            if date_index > 0:
                date_index = date_index - 1
            
            tree_stock = {}    

            #Build List Dates
            list_dates = []   

            list_dates.append('Date')     
        
            for i in range(l_count_stock):
                list_dates.append(f.index[date_index - i].strftime("%Y-%m-%d"))

            #Build List Prices
            list_prices = []
            
            list_prices.append('Close Price')

            l_date_price = 0

            for i in range(l_count_stock):
                date_price = f.loc[f.index[date_index - i],'Close']
                l_date_price +=  date_price
                list_prices.append("{:.2f}".format(date_price))
                
            #get average stock    
            l_average_stock = (l_date_price/l_count_stock)
            #get difference
            l_difference = (l_average_stock - l_current_price)

            if l_current_price != 0:
                l_average_dif = (l_difference/l_current_price)*100


            #tree_stocks[stock+'0'] = info_stock.info['industry']
            #tree_stocks[stock+'1'] = info_stock.calendar.loc[info_stock.calendar.index[0],'Value'].strftime("%Y-%m-%d")
            #tree_stocks[stock+'1'] = stock
            tree_stock[stock+'0'] = 'DATA_FOUND'
            tree_stock[stock+'1'] = stock_name
            tree_stock[stock+'2'] = stock_industry
            tree_stock[stock+'3'] = yec_desc  
            tree_stock[stock+'4'] = current_price         
            tree_stock[stock+'5'] = 'Average Price: ' + "{:.2f}".format(l_average_stock)
            tree_stock[stock+'6'] = 'Rerturning to Avg: ' + "{:.2f}".format(l_difference) + '   (' + "{:.2f}".format(l_average_dif) + '%)' 
            tree_stock[stock+'7'] = list_dates
            tree_stock[stock+'8'] = list_prices        
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
