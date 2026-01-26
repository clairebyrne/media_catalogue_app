import streamlit as st
import pandas as pd
import numpy as np
import os 
from dotenv import load_dotenv

st.title('Uber pickups in NYC')
st.logo('resources/tmdb_logo.png', size='small')

def get_variable(variable_name):
    """ 
    Retrieves the value of a variable from a .env file, given variable name
    Returns: variable value
    """
    # get env variables from .env file
    load_dotenv()
    # extract variable
    value = os.environ.get(variable_name)
    return value

tmdb_cred = get_variable('tmbd_credit')

st.text(tmdb_cred)
st.text('(or at least it will when its not the streamlit placeholder)')

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
            'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache_data
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

data_load_state = st.text('Loading data...')
data = load_data(10000)
data_load_state.text("Done! (using st.cache_data)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

st.subheader('Number of pickups by hour')
hist_values = np.histogram(data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
st.bar_chart(hist_values)

# Some number in the range 0-23
hour_to_filter = st.slider('hour', 0, 23, 17)
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]

st.subheader('Map of all pickups at %s:00' % hour_to_filter)
st.map(filtered_data)