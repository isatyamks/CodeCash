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



df = pd.read_csv('../input/all_stocks_5yr.csv')
df.head()
# Brief Description of our dataset
df.describe()

# Replace the column name from name to ticks
df = df.rename(columns={'Name': 'Ticks'})

# Let's analyze some of the stocks.
amzn = df.loc[df['Ticks'] == 'AMZN']
amzn.head()