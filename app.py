from flask import Flask, render_template, request, redirect

import numpy as np
import requests
import json
import pandas as pd
import os

# bokeh / flask imports
import flask
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.templates import RESOURCES
from bokeh.util.string import encode_utf8

app = Flask(__name__)

@app.route('/')
def main():
  return redirect('/index')

app.vars = {}  

@app.route('/index', methods = ['GET','POST'])
def index():
  if request.method == 'GET':
    return render_template('index.html')
  else:
        #request was a POST
        app.vars['ticker'] = request.form['ticker']
        app.vars['features'] = request.form.getlist('features')
        
        #### my code from ipython notebook ####
        # set variables closing, adj_closing, volume
        ticker = app.vars['ticker']
        closing = 'Close' in app.vars['features']
        adj_closing = 'Adj. Close' in app.vars['features']
        volume = 'Volume' in app.vars['features']
        """
        f = open('%s.txt'%(app.vars['ticker']),'w')
        f.write('Ticker: %s\n'%(app.vars['ticker']))
        f.write('Features: %s\n'%(app.vars['features']))
        f.write('Include Closing: %s\n'%(closing))
        f.write('Include Adjusted Closing: %s\n'%(adj_closing))
        f.write('Include Volume: %s\n'%(volume))
        f.close()
        """        
        # import data from Quandle WIKI 
        r = requests.get('https://www.quandl.com/api/v3/datasets/WIKI/'+ticker+'.json?order=asc')

        parsed_json = json.loads(r.text)
        
        # import to dataframe
        df = pd.DataFrame(parsed_json['dataset']['data'])

        # rename columns, set date to datetime type
        df.columns = parsed_json['dataset']['column_names']
        df['Date'] = pd.to_datetime(df['Date'])

        company = parsed_json['dataset']['name'].split('.')
        company = company[0]

        def generate_close(ticker, closing):
            if closing:
                return p1.line(df['Date'], df['Close'], color='#0000FF', legend=ticker+": Close")

        def generate_adjclose(ticker,adj_closing):
            if adj_closing:
                return p1.line(df['Date'], df['Adj. Close'], color='#009933', legend=ticker+": Adj. Close")
            
        def generate_volume(ticker, volume):
            if volume:
                return p1.line(df['Date'], df['Volume'], color='#CC3300', legend=ticker+": Volume")


        from bokeh.plotting import figure, show, output_file, vplot

        output_file("stockstest.html", title=company)

        p1 = figure(x_axis_type = "datetime")

        # generate lines for the selected options
        generate_close(ticker, closing)
        generate_adjclose(ticker, adj_closing)
        generate_volume(ticker, volume)

        if not (closing or adj_closing or volume):
            generate_close(ticker, True)

        p1.title = ticker + " (Data from Quandle WIKI set)"
        p1.grid.grid_line_alpha=1.0
        p1.xaxis.axis_label = 'Date'

        plot_resources = RESOURCES.render(
        js_raw=INLINE.js_raw,
        css_raw=INLINE.css_raw,
        js_files=INLINE.js_files,
        css_files=INLINE.css_files,
        )

        script, div = components(p1, INLINE)
        html = flask.render_template(
        'index_post.html',
        plot_script=script, plot_div=div, plot_resources=plot_resources, ticker=ticker, company=company
        )
        return encode_utf8(html)

        # return render_template('index_post.html',ticker=app.vars['ticker'])


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
    #app.run(port=33507, debug=True)