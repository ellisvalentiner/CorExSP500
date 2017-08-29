#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function
import psycopg2
import os
import pandas as pd
import corex as ce
from corex.vis_corex import vis_hierarchy
from timeit import default_timer

conn = psycopg2.connect(dsn=os.environ["DATABASE_DSN"])
query = """
SELECT
  date,
  tbl.ticker,
  (close - prev_close)/prev_close AS return,
  gics.sector
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

sector_colors = {
    None: 'black',
    'Telecommunication Services': 'purple',
    'Information Technology': 'magenta',
    'Industrials': 'blue',
    'Materials': 'cornflowerblue',
    'Energy': 'red',
    'Utilities': 'limegreen',
    'Consumer Staples': 'green',
    'Consumer Discretionary': 'lightblue',
    'Financials': 'sandybrown',
    'Health Care': 'lightslategrey',
    'Real Estate': 'darkorange'
}
data['color'] = [sector_colors[i] for i in data.sector.values]
data['label'] = data.color + '_' + data.ticker
data = data.pivot_table(values='return', index='date', columns='label', fill_value=-1)

# "We included only the 388 companies which were on the S&P 500 for the entire period."
X = data.loc[:, ~(data == -1).any(axis=0)].as_matrix()
labels = data.loc[:, ~(data == -1).any(axis=0)].columns

# "We use a representation with m1 = 20, m2 = 3, m3 = 1 and Yj were discrete trinary variables."
layers = []
for n in (20, 3, 1):
    layer = ce.Corex(n_hidden=n, dim_hidden=3,
                     max_iter=int(1e4), n_repeat=1, ram=16., max_samples=500, n_cpu=4,
                     eps=1e-5, marginal_description='gaussian', smooth_marginals=False,
                     missing_values=-1, seed=1, verbose=True)
    layers.append(layer)

# Fit the model
start = default_timer()
Y1 = layers[0].fit_transform(X)
Y2 = layers[1].fit_transform(Y1)
Y3 = layers[2].fit_transform(Y2)
end = default_timer()
print("Start: {0}\tEnd: {1}\tElapsed: {2}".format(start, end, end - start))

# Produce visualization
vis_hierarchy(corexes=layers, column_label=labels, max_edges=400, prefix='output')
