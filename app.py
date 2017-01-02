import requests
import pandas as pd
from datetime import datetime
from math import pi
from flask import Flask, redirect, url_for, render_template, request
from bokeh.plotting import figure, show
from bokeh.models import DatetimeTickFormatter
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8

app = Flask(__name__) #create application instance
app.vars = {
	'Symbol': '', 'URL': '', 'Dates': [], 'Prices': [],
	'CheckBoxes': {
	'Close': ['close','Closing Price',False],
	'Open': ['open','Opening Price',False],
	'CloseA': ['adj_close','Adjusted Closing Price',False],
	'OpenA': ['adj_open','Adjusted Opening Price',False]}
	}
	#CheckBoxes nested dict is: column, title, display?

def gen_url(columns='', key='ooAjSowGyRDhfqU-XSvZ'):
	"""Returns appropriate request url."""
	url = r'https://www.quandl.com/api/v3/datatables/WIKI/PRICES.json?'
	url += 'ticker=' + app.vars['Symbol']
	url += '&qopts.columns=date,' + columns
	url += '&api_key=' + key
	return url

def get_data():
	"""processes API request sets global list variables (dates and prices)."""
	r = requests.get(app.vars['URL'])
	raw = pd.DataFrame(r.json())
	z = zip(*raw.ix[1,0]) #strip non-data elements from json, flip
	if not z: #verify data exists
		return False
	def convert_date(x):
		y, m, d =x.split('-')
		return datetime(int(y),int(m),int(d))
	app.vars['Dates'] = map(convert_date, z[0])
	app.vars['Prices'] = z[1:]
	return True
	
@app.route('/')
def toMP():
	return redirect(url_for('Mini_Project'))
	
#Main Form
@app.route('/Mini-Project/', methods=['GET','POST'])
def Mini_Project():
	if request.method == 'GET':
        	return render_template('BaseForm.html')
    	else:
		app.vars['Symbol'] = request.form['symbol'].upper()
		if app.vars['Symbol']=='':
			return redirect(url_for('Oops'))
		cols = []
		for key in app.vars['CheckBoxes']:
			try:
				if request.form[key]:
					app.vars['CheckBoxes'][key][2]=True
					cols.append(app.vars['CheckBoxes'][key][0])
			except:
				app.vars['CheckBoxes'][key][2]=False
		if cols:
			app.vars['URL'] = gen_url(columns=','.join(cols))
			return redirect(url_for('Graph'))
		else:
			return redirect(url_for('Oops'))


#Generate Graph
@app.route('/Graph/')
def Graph():
	if not get_data():
		return redirect(url_for('Oops'))
	col = ['red', 'blue', 'green', 'yellow']
	p = figure(tools='pan,box_zoom,reset,save', x_axis_label='Date', y_axis_label='Price ($)')
	
	#generate chart 
	i=0
	for key in app.vars['CheckBoxes']:
		if app.vars['CheckBoxes'][key][2]:
			p.line(app.vars['Dates'], app.vars['Prices'].pop(0), legend=app.vars['CheckBoxes'][key][1], line_color=col.pop(0))			
	p.legend.location = 'top_left'
	p.xaxis.formatter=DatetimeTickFormatter(formats=dict(hours=['%B %Y'], days=['%B %Y'], months=['%B %Y'], years=['%B %Y']))
	p.xaxis.major_label_orientation = pi/4

	#return as webpage
	js_resources = INLINE.render_js()
	css_resources = INLINE.render_css()
	script, div = components(p)
	html = render_template(
		'embed.html',
		symbol=app.vars['Symbol'],
		plot_script=script,
		plot_div=div,
		js_resources=js_resources,
		css_resources=css_resources,
	)
	return encode_utf8(html)			
	
			
#ERROR
@app.route('/Insufficient-Params/')
def Oops():
	return r'Insufficient Parameters! Go <a href="Mini-Project">back</a> and try again!'
	
		
if __name__ == '__main__':
    app.run(port=33507)
