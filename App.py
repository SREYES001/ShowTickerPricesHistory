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
    StockTextarea = request.form['StockTextarea']

    if StockTextarea.strip() == '':
        flash('Please, Input Stocks on Stock Area')
        return redirect(url_for('Index'))

    symbol = StockTextarea.split(',')

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

    #Print if there is a error with the date ED
    if ED <  SD:
        flash('The end date can''t be less than the start date')
        return redirect(url_for('Index'))        


    # Get number of days<
    dt = (ED - SD)
    countDays = dt.days

    # Get Current Date
    TD = datetime.date.today()

    lSymbols = {}
    # Generate Files Stocks
    #location = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Downloads') + '\\'
    location = 'C:\\Users\\Public\\Downloads'

    for stock in symbol:
        lStock = stock.strip().upper()
        try:
            f = web.DataReader(lStock, 'yahoo', SD, ED)
            print('')
            print('')
            print(lStock)
            print('')
            f.loc[ED:ED, ['Close']].to_csv(location+lStock+'_'+TD.strftime("%d")+'-'+TD.strftime("%b")+'-'+TD.strftime("%Y")+'.csv', mode='w')
            for i in range(1, countDays+1):
                day = (ED - datetime.timedelta(days=i))
                f.loc[day:day, ['Close']].to_csv(location+lStock+'_'+TD.strftime("%d")+'-'+TD.strftime("%b")+'-'+TD.strftime("%Y")+'.csv', mode='a', header=False)

            lSymbols[lStock] = "File Created"    
        except:
            print("No information for symbol: " + lStock)
            lSymbols[lStock] = "No information for symbol" 
            continue

    return render_template('create_stocks.html', pStocks=lSymbols,pLocation = location)

if __name__ == '__main__':
    # debug--> Use when we had changes into the server so restart the server
    app.run()
    print('Successful')
else:
    print('Error')
