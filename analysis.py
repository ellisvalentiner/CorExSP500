#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function
import psycopg2
import os
import pandas as pd
import corex as ce
from corex.vis_corex import vis_hierarchy

conn = psycopg2.connect(dsn=os.environ["DATABASE_DSN"])
query = """
SELECT date, tbl.ticker, (close - prev_close)/prev_close AS return, gics.sector
FROM (
    SELECT date, ticker, close, LAG(close) OVER (PARTITION BY ticker ORDER BY date) AS prev_close
    FROM (
        SELECT MIN(date) OVER (PARTITION BY DATE_TRUNC('month', date)) AS min_date, date, ticker, close
        FROM daily
        ) AS tbl
    WHERE date=min_date
    ) AS tbl
LEFT JOIN gics ON tbl.ticker = LOWER(gics.ticker)
WHERE prev_close IS NOT NULL
ORDER BY date;
"""
data = pd.read_sql(query, con=conn)
conn.close()

# Colors from corex.vis_rep
colors = 'indigo,gold,hotpink,firebrick,indianred,yellow,mistyrose,darkolivegreen,darkseagreen,pink,tomato,' \
         'lightcoral,orangered,navajowhite,palegreen,darkslategrey,greenyellow,burlywood,seashell,mediumspringgreen,' \
         'papayawhip,blanchedalmond,chartreuse,dimgray,black,peachpuff,springgreen,aquamarine,white,orange,' \
         'lightsalmon,darkslategray,brown,ivory,dodgerblue,peru,lawngreen,chocolate,crimson,forestgreen,slateblue,' \
         'lightseagreen,cyan,mintcream,antiquewhite,mediumorchid,skyblue,gray,darkturquoise,goldenrod,darkgreen,' \
         'floralwhite,darkviolet,moccasin,saddlebrown,grey,darkslateblue,lightskyblue,lightpink,mediumvioletred,' \
         'slategrey,red,deeppink,limegreen,palegoldenrod,plum,turquoise,lightgrey,lightgoldenrodyellow,darkgoldenrod,' \
         'lavender,maroon,yellowgreen,sandybrown,thistle,violet,navy,magenta,dimgrey,tan,rosybrown,blue,lightblue,' \
         'ghostwhite,honeydew,cornflowerblue,linen,powderblue,seagreen,darkkhaki,snow,sienna,mediumblue,royalblue,' \
         'lightcyan,green,mediumpurple,midnightblue,cornsilk,paleturquoise,bisque,slategray,khaki,wheat,darkorchid,' \
         'deepskyblue,salmon,steelblue,palevioletred,lightslategray,aliceblue,lightslategrey,orchid,gainsboro,' \
         'mediumseagreen,lightgray,mediumturquoise,lemonchiffon,cadetblue,lightyellow,lavenderblush,coral,purple,' \
         'whitesmoke,mediumslateblue,darkorange,mediumaquamarine,darksalmon,beige,blueviolet,azure,lightsteelblue,' \
         'oldlace'.split(',')
data['color'] = [colors[i] for i in pd.Categorical(data.sector).codes]
data['label'] = data.color + '_' + data.ticker
data = data.pivot_table(values='return', index='date', columns='label', fill_value=-1)

# "We included only the 388 companies which were on the S&P 500 for the entire period."
X = data.loc[:, ~(data == -1).any(0)].as_matrix()
labels = data.loc[:, ~(data == -1).any(0)].columns

# "We use a representation with m1 = 20, m2 = 3, m3 = 1 and Yj were discrete trinary variables."
layers = []
for n in (20, 3, 1):
    layer = ce.Corex(n_hidden=n, dim_hidden=3,
                     max_iter=1000, n_repeat=1, ram=16., max_samples=10000, n_cpu=4,
                     eps=1e-5, marginal_description='gaussian', smooth_marginals=True,
                     missing_values=-1, seed=1, verbose=True)
    layers.append(layer)

# Fit the model
Y1 = layers[0].fit_transform(X)
Y2 = layers[1].fit_transform(Y1)
Y3 = layers[2].fit_transform(Y2)

# Produce visualization
vis_hierarchy(corexes=layers, column_label=labels, max_edges=400, prefix='corex_output')
