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

    """# read ticker symbols from the text area
    volume = request.form['volume']"""

    #print('Volume flag: ' + volume)

    is_error = False

    if StockTextarea.strip() == '':
        flash('Please, Enter tickers on ticker Area')
        is_error = True        

    
    symbol = StockTextarea.split(',')

    symbol_index = StockTextarea.split(',')

    symbol_index.append('NDAQ')
    symbol_index.append('^DJI')
    symbol_index.append('^GSPC')
   

    if len(symbol) > 10:
        flash('Please, Enter 10 tickers maximum')
        is_error = True


    # Get Start Date
    SD = ObtainDate(request.form['datefrom'])
     
    #Print if there is a error with the date SD
    if SD == '':
        is_error = True   
    
    # Get End Date
    ED = ObtainDate(request.form['dateto'])
    
    #Print if there is a error with the date ED
    if ED == '':
        is_error = True

   # Get Current Date
    TD = datetime.date.today()

   #Print if there is a error with the date ED
    if SD.strftime("%Y%m%d") > TD.strftime("%Y%m%d"):
        flash('The start date can not higher than today')
        is_error = True

    #Print if there is a error with the date ED
    if ED.strftime("%Y%m%d") > TD.strftime("%Y%m%d"):
        flash('The end date can not higher than today')
        is_error = True  

    #Print if there is a error with the date ED
    if ED <  SD:
        flash('The end date can''t be less than the start date')
        is_error = True           

    # Get number of days<
    dt = (ED - SD)
    countDays = dt.days

    if countDays > 30:
        flash('The count of the days can not be greater than 30 days')
        is_error = True 
    
    if is_error:
        return redirect(url_for('Index'))
        #return redirect(url_for('Index',PstockTextarea =request.form['StockTextarea'],P_StartDate=request.form['datefrom'],P_EndDate=request.form['dateto']))

    list_yec = []

    tree_stocks = {}

    #Set tickers
    m = Ticker(symbol_index)

    #Get index prices
    list_NDAQ = []
    
    list_NDAQ.append(m.price['NDAQ']['shortName'])
    list_NDAQ.append("{:.2f}".format(m.price['NDAQ']['regularMarketPrice']))  
    list_NDAQ.append("{:.2f}".format(m.price['NDAQ']['regularMarketChange']))    
    list_NDAQ.append("{:.2f}".format(m.price['NDAQ']['regularMarketChangePercent'] * 100))   

    list_DJI = []

    list_DJI.append(m.price['^DJI']['shortName'])
    list_DJI.append("{:.2f}".format(m.price['^DJI']['regularMarketPrice'])) 
    list_DJI.append("{:.2f}".format(m.price['^DJI']['regularMarketChange']))    
    list_DJI.append("{:.2f}".format(m.price['^DJI']['regularMarketChangePercent'] * 100))   

    list_GSPC = []
    
    list_GSPC.append(m.price['^GSPC']['shortName'])
    list_GSPC.append("{:.2f}".format(m.price['^GSPC']['regularMarketPrice']))  
    list_GSPC.append("{:.2f}".format(m.price['^GSPC']['regularMarketChange']))    
    list_GSPC.append("{:.2f}".format(m.price['^GSPC']['regularMarketChangePercent'] * 100))     

    tree_stocks['NDAQ'] = list_NDAQ
    tree_stocks['DJI'] = list_DJI 
    tree_stocks['GSPC'] = list_GSPC 
    #End Index  

    list_dates = []

    for stock in symbol:
        try:
            #get prices info 
            f = web.DataReader(stock, 'yahoo', SD, ED)

            l_count_stock = len(f)
            
            list_yec = []

            try:
                #get earnig date            
                yec_date = (datetime.date.fromtimestamp(m.get_modules('calendarEvents')[stock]['earnings']['earningsDate'][0]))
                yec_count = (yec_date - TD).days

                if yec_count > 1:
                    yec_desc = str(yec_count) + ' days to earnings call'
                else:
                    if yec_count >= 0:
                        yec_desc = str(yec_count) + ' day to earnings call'
                    else:
                        yec_desc = ''
                        yec_count = ''

                list_yec.append(yec_count)
                list_yec.append(yec_desc)
            except:
                list_yec = []

            try:
                #get Name and Industry
                l_current_price = m.financial_data[stock]['currentPrice']
                current_price = "{:.2f}".format(l_current_price)
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

            #reset values
            ChangeStock = ''
            ChangeStock_percent = ''
            ChangeStock_pre = ''
            ChangeStock_percent_pre = ''
            ChangeStock_post = ''
            ChangeStock_percent_post = ''                

            try:
                #get Change
                l_change = m.price[stock]['regularMarketChange']
                ChangeStock = "{:.2f}".format(l_change)
                l_change_percent = m.price[stock]['regularMarketChangePercent']*100
                ChangeStock_percent  = "{:.2f}".format(l_change_percent)               
            except:
                ChangeStock = ''
                ChangeStock_percent = ''

            try:
                #get Change pre
                l_change_pre = m.price[stock]['preMarketChange']
                ChangeStock_pre = "{:.2f}".format(l_change_pre)
                l_change_percent_pre = m.price[stock]['preMarketChangePercent']*100
                ChangeStock_percent_pre  = "{:.2f}".format(l_change_percent_pre)              
            except:
                ChangeStock_pre = ''
                ChangeStock_percent_pre = ''

            try:
                #get Change post
                l_change_post = m.price[stock]['postMarketChange']
                ChangeStock_post = "{:.2f}".format(l_change_post)
                l_change_percent_post = m.price[stock]['postMarketChangePercent']*100
                ChangeStock_percent_post  = "{:.2f}".format(l_change_percent_post)               
            except:
                ChangeStock_post = ''
                ChangeStock_percent_post = ''                                

                     

            date_index = l_count_stock

            #count dates
            if date_index > 0:
                date_index = date_index - 1
            
            tree_stock = {}    

            #Build List Dates
            if len(list_dates) == 0:
                list_dates = []    
                
                #get dates
                for i in range(l_count_stock):
                    list_dates.append(f.index[date_index - i].strftime("%Y-%m-%d"))

            #Build List Prices
            list_prices = []

            l_date_price = 0
            
            #get prices
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
            average_list = []
            average_list.append("{:.2f}".format(l_average_stock))
            average_list.append('Average Price: ' + "{:.2f}".format(l_average_stock))
            average_list.append("{:.2f}".format(l_difference))
            average_list.append("{:.2f}".format(l_average_dif) + '%')
            average_list.append('Returning to Avg: ' + "{:.2f}".format(l_difference) + '   (' + "{:.2f}".format(l_average_dif) + '%)')
            average_list.append(ChangeStock)
            average_list.append(ChangeStock_percent)  
            average_list.append(ChangeStock_post)
            average_list.append(ChangeStock_percent_post)  
            average_list.append(ChangeStock_pre)
            average_list.append(ChangeStock_percent_pre)                          

            ChangeStock_percent_pre


            tree_stock[stock+'0'] = 'DATA_FOUND'
            tree_stock[stock+'1'] = stock_name
            tree_stock[stock+'2'] = stock_industry
            tree_stock[stock+'3'] = list_yec  
            tree_stock[stock+'4'] = current_price         
            tree_stock[stock+'5'] = average_list
            #tree_stock[stock+'7'] = list_dates
            tree_stock[stock+'6'] = list_prices   
        except:
            tree_stock = {}
            tree_stock[stock+'0'] = 'NO_DATA_FOUND'
            tree_stock[stock+'1'] = 'There is no information for the symbol'
            tree_stocks[stock] = tree_stock
            continue 

        tree_stocks[stock] = tree_stock

    
    tree_stocks['DATES'] = list_dates 
  

    return render_template('create_stocks.html', pTreeStocks=tree_stocks)    

if __name__ == '__main__':
    # debug--> Use when we had changes into the server so restart the server
    app.run()
    print('Successful')
else:
    print('Error')
