from datetime import datetime
from aa.js import JsonFetcher
import pandas as pd
from vc_curves import vc_get_threshold, vc_get_level


APPLIANCE_URL = 'archappl.diamond.ac.uk'

def fetch_pv_to_dataframe(pv_name:str, start_date:datetime, end_date:datetime) -> pd.DataFrame:
    """retrieves a vibration PV from the Diamond archiver appliance, returns it as a dataframe with some useful calculated fields

    Args:
        pv_name (str): EPICS PV full name 
        start_date (datetime): datetime, start of data. 
        end_date (datetime): _datetime, end of data

    Returns:
        pd.DataFrame: a Pandas dataframe including the PV augmented with further useful data
    """

    jf = JsonFetcher(APPLIANCE_URL, 80)

    #TODO: support multiple PVs (maybe from the base system PV and automatically build labels etc?)
    #TODO: check for timezone, if not present throw a warning and assume UTC

    data = jf.get_values(pv_name, start_date, end_date)

    # if this line isn't here, seaborn explodes. Not sure why. Worked it out from here: 
    # https://medium.com/@darektidwell1980/typeerror-float-argument-must-be-a-string-or-a-number-not-period-facebook-prophet-and-pandas-6b74a23fc47b
    pd.plotting.register_matplotlib_converters()

    df = pd.DataFrame()
    df['Time'] = data.utc_datetimes
    df['VC_Peak'] = data.values
    df['VC_Level'] = df.apply(lambda x: vc_get_level(x['VC_Peak']), axis=1).astype('category') # assign a categorical VC level

    df['dT'] = df['Time'].shift(-1) - df['Time']
    df['dT_Seconds'] = df.apply(lambda x: x['dT'].total_seconds(), axis=1) #needed for histplot

    return df

def get_vib_alarms(data:pd.DataFrame, vc_threshold:str = "G"):
    """returns a dataframe of alarms including time and duration

    Args:
        data (pd.DataFrame): _description_
        vc_threshold (str, optional): _description_. Defaults to "G".
    """

    #TODO: add an exclusion times PV (list of tuples?)
    vc_alarm_val = vc_get_threshold(vc_threshold)
    # TODO: needs sorting by channel before doing this
    data['VC_Alarm'] = data.apply(lambda x: False if x['VC_Peak'] < vc_alarm_val else True, axis=1)