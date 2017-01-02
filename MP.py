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

MP = Flask(__name__) #create application instance
MP.vars = {
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
	url += 'ticker=' + MP.vars['Symbol']
	url += '&qopts.columns=date,' + columns
	url += '&api_key=' + key
	return url

def get_data():
	"""processes API request and returns data as list."""
	r = requests.get(MP.vars['URL'])
	raw = pd.DataFrame(r.json())
	z = zip(*raw.ix[1,0]) #strip non-data elements from json, flip
	def convert_date(x):
		y, m, d =x.split('-')
		return datetime(int(y),int(m),int(d))
	MP.vars['Dates'] = map(convert_date, z[0])
	MP.vars['Prices'] = z[1:]
	return 
	
@MP.route('/')
def toMP():
    return redirect(url_for('Mini_Project'))

	
#Main Form
@MP.route('/Mini-Project/', methods=['GET','POST'])
def Mini_Project():
    if request.method == 'GET':
        return render_template('BaseForm.html')
    else:
		MP.vars['Symbol'] = request.form['symbol'].upper()
		if MP.vars['Symbol']=='':
			return redirect(url_for('Oops'))
		cols = []
		for key in MP.vars['CheckBoxes']:
			try:
				if request.form[key]:
					MP.vars['CheckBoxes'][key][2]=True
					cols.append(MP.vars['CheckBoxes'][key][0])
			except:
				MP.vars['CheckBoxes'][key][2]=False
		if cols:
			MP.vars['URL'] = gen_url(columns=','.join(cols))
			return redirect(url_for('Graph'))
		else:
			return redirect(url_for('Oops'))


#Generate Graph
@MP.route('/Graph/')
def Graph():
	col = ['red', 'blue', 'green', 'yellow']
	p = figure(tools='pan,box_zoom,reset,save', x_axis_label='Date', y_axis_label='Price ($)')
	get_data()

	#generate chart 
	i=0
	for key in MP.vars['CheckBoxes']:
		if MP.vars['CheckBoxes'][key][2]:
			p.line(MP.vars['Dates'], MP.vars['Prices'].pop(0), legend=MP.vars['CheckBoxes'][key][1], line_color=col.pop(0))			
	p.legend.location = 'top_left'
	p.xaxis.formatter=DatetimeTickFormatter(formats=dict(hours=['%B %Y'], days=['%B %Y'], months=['%B %Y'], years=['%B %Y']))
	p.xaxis.major_label_orientation = pi/4

	#return as webpage
	js_resources = INLINE.render_js()
	css_resources = INLINE.render_css()
	script, div = components(p)
	html = render_template(
		'embed.html',
		symbol=MP.vars['Symbol'],
		plot_script=script,
		plot_div=div,
		js_resources=js_resources,
		css_resources=css_resources,
	)
	return encode_utf8(html)			
	
			
#ERROR
@MP.route('/Insufficient-Params/')
def Oops():
	return "Insufficient Parameters! Go back and try again!"
	
	
		
if __name__ == '__main__':
    MP.run(port=33507)


# MP.vars['symbol'] = request.form['symbol']
# MP.vars['features'] = request.form['features']
# s = "Lets go!"
# for ss in request.form['features']:
# s+=ss
