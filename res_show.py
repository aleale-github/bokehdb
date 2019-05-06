#!/usr/bin/env python
# coding: utf-8

# In[3]:


import pandas as pd
import numpy as np
from datetime import date
from bokeh.plotting import figure
from bokeh.layouts import layout, widgetbox
from bokeh.models import ColumnDataSource, Div,HoverTool
from bokeh.models.widgets import Slider, Select, TextInput, DateRangeSlider,DateSlider,DatePicker
from bokeh.io import curdoc
from bokeh.palettes import Category10_4 as cols
# from bokeh.io import show,output_notebook
# output_notebook()


# In[7]:


df_pred = pd.read_hdf('/data/tests/vwap.hdf5',key='/historical_data/results')
df_pred = df_pred.sort_values(by=["ISIN","MKT","DATETIME","REF_DATE"]).drop_duplicates(subset=["ISIN","MKT","DATETIME"],keep='last').drop(columns=["REF_DATE"])
df_real = pd.read_hdf('/data/tests/vwap.hdf5',key='/historical_data/volumes')
df = df_real.merge(df_pred,on=["ISIN","MKT","DATETIME"],suffixes=["_REAL","_PRED"],how="right")
df["DATE"] = df.DATETIME.dt.date
df["TIME"] = df.DATETIME.dt.time
df = df[["ISIN","MKT","DATE","TIME","NCUMSUM_REAL","NCUMSUM_PRED"]].sort_values(by=["ISIN","MKT","DATE","TIME"])

isin_l = df.ISIN.unique().tolist()
dates_l = df.DATE.sort_values().unique().tolist()
isin_s = Select(title="ISIN", options=isin_l,value=isin_l[0])
date_s = DatePicker(title="Date",min_date=dates_l[0],max_date=dates_l[-1],value=df.DATE.min())

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(TIME=[],NCUMSUM_REAL=[],NCUMSUM_PRED=[]))
tools = 'save,pan,box_zoom,reset,wheel_zoom,hover'

p = figure(plot_height=480, plot_width=800,x_axis_type="datetime",y_range=(0,1.1),background_fill_color="#efefef",tools = tools, output_backend="webgl")
p.toolbar.logo = None
p.xaxis.axis_label = "Trade Time"
p.yaxis.axis_label = "Volume"
line_pred = p.line(x="TIME", y="NCUMSUM_PRED", source=source,legend="Prediction",color=cols[1], line_width=2,muted_color=cols[1], muted_alpha=0.1)
line_real = p.line(x="TIME", y="NCUMSUM_REAL", source=source,legend="Real",color=cols[0], line_width=2,muted_color=cols[0], muted_alpha=0.1)

p.legend.location = "top_left"
p.legend.click_policy = "mute"
p.select_one(HoverTool).tooltips = [('Time', '@TIME{%T}'),('Predicted', '@NCUMSUM_PRED'),('Real', '@NCUMSUM_REAL')]
p.select_one(HoverTool).formatters = {'TIME': 'datetime'}
p.select_one(HoverTool).mode='vline'

def update():
    isin = isin_s.value
    date = date_s.value
    tmp = df[(df.DATE == date) & (df.ISIN == isin)]
    if tmp.empty:
        p.title.text = "No data available for {} on {}".format(isin,date)
    else:
        p.title.text = "VWAP for {} on {}".format(isin,date)
    source.data = dict(TIME=tmp.TIME.values,NCUMSUM_PRED=tmp.NCUMSUM_PRED.values,NCUMSUM_REAL=tmp.NCUMSUM_REAL.values)
    
controls = [isin_s,date_s]
for control in controls:
    control.on_change('value', lambda attr, old, new: update())

inputs = widgetbox(*controls, sizing_mode='fixed')
l = layout([[inputs, p]], sizing_mode='fixed')

update()
curdoc().add_root(l)
curdoc().title = "VWAP"


# In[ ]:




