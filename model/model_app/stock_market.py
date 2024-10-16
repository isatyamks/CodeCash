# Import Libraries
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt
from scipy import stats
from pandas.core import datetools
from plotly import tools
import plotly.plotly as py
import plotly.figure_factory as ff
import plotly.tools as tls
import plotly.graph_objs as go
import warnings
warnings.filterwarnings("ignore")



df = pd.read_csv('model\model_data\stock_market_data\stocks\A.csv')
df.head()
df.describe()

df = df.rename(columns={'Name': 'Ticks'})

amzn = df.loc[df['Ticks'] == 'AMZN']
amzn.head()