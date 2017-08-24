# CorEx S&P500

Correlation Explanation applied to S&P 500 data.

This repository is a replication of the CorEx finance data example in [Ver Steeg & Galstyan (2015)](#references).

## Background

Correlation Explanation (CorEx) is an unsupervised method for producing probabilistic hierarchical informative representations. The idea is the representations should be based on maximizing information, the multivariate mutual information or total correlation.

Total correlation, or multivariate mutual information, is a measure of dependence. If _X_ is a set of one or more variables, and _Y_ is another, then the decrease in total correlation between _X_ and _X_|_Y_ approximates how much _Y_ explains _X_. Total correlation is zero if and only if the set of variables are independent and is maximized when a single variable explains all others in the set. CorEx uses latent factors, _Y_, to minimize the correlation in the data, _X_, when conditioned on those factors (_X_ | _Y_). 

For more information about CorEx, see [Ver Steeg & Galstyan (2014)](#references).

## Data

The dataset consists of daily stock quotes for S&P 500 companies from January 1988 through July 2013. The data is transformed from a long to wide format where each column represents a company and rows represents the return (as a percent) from the previous month. 

The data was obtained from [QuantQuote](https://quantquote.com), a provider of historical stock market data, and loaded into a Postgres database (see [ellisvalentiner/QuantQuoteHistoricalIngest](https://github.com/ellisvalentiner/QuantQuoteHistoricalIngest)).

Although the S&P 500 index is made up of approximately 500 companies at a given time, companies enter and exit the index so only 388 companies have complete data for this time period. As in [Ver Steeg & Galstyan (2015)](#references), this analysis excluded companies without complete data for the study period. While CorEx can handle missingness, the authors noted that missing not at random (MNAR) hasn't been extensively investigated.

It's important to note that this may introduce a survivorship bias effect: companies that remained in the index during this time may be more correlated than those that left/entered the index. This is difficult to assess because companies may exit the index for several reasons (market cap changes, taken private, acquisitions, etc.) creating room for new companies to enter. Further changes to the index occur at defined times, so several companies may enter and exit simultaneously.

## Model

The CorEx model here consists of three layers with 20, 3, and 1 units respectively. The hidden factor at each layer takes 3 discrete values.

## Result

![](tree_sfdp_w_splines.png)

The figure is a replication of Fig. 4 in [Ver Steeg & Galstyan (2015)](#references), showing the overall structure.

The edge thickness is proportional to mutual information. The node size represents multivariate mutual information among child nodes.

## References

Ver Steeg, G., & Galstyan, A. (2014). Discovering structure in high-dimensional data through correlation explanation. In _Advances in Neural Information Processing Systems_ (pp. 577-585). ([arXiv](https://arxiv.org/abs/1406.1222))

Ver Steeg, G., & Galstyan, A. (2015). Maximally informative hierarchical representations of high-dimensional data. In _Artificial Intelligence and Statistics_ (pp. 1004-1012). ([arXiv](https://arxiv.org/abs/1410.7404v2))
