import logging
from argparse import ArgumentParser
from datetime import datetime

from dlsVibrationTools.vib_data import fetch_pv_to_dataframe
from dlsVibrationTools.vib_plots import plot_vc_timeseries

from . import __version__

__all__ = ["main"]


def main(args=None):

    # logging set up
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    # input parsing
    parser = ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)

    args = parser.parse_args(args)
    
    # parse args and get data
    # PV names and date range
    pv_name = 'BL20I-DI-ACCEL-01:DATA:CH01:VC_PEAK'
    logger.warning('IOC selection not implemented - defaulting to I20 vibration kit for now')
    #end_date = datetime.now(timezone.utc).astimezone()
    #start_date = end_date - timedelta(hours=24*7)

    start_date = datetime(2022, 5, 3).astimezone()
    end_date = datetime(2022, 5, 5).astimezone()
    logger.warning('Date range not implemented - defaulting to fixed date range for now')

    # Threshold for "alarms" report (will trigger if above the velocity required to meet this level's spec)
    vc_threshold = 'G'
    logger.warning('VC level not implemented - defaulting to VC-G alarms for now!')

    # fetch data & display
    logger.info('Fetching data from EPICS...')
    df = fetch_pv_to_dataframe(pv_name = pv_name, 
        start_date = start_date,
        end_date = end_date)

    print(df.head())
    
    plot_vc_timeseries(df)
    

# test with: pipenv run python -m dlsVibrationTools
if __name__ == "__main__":
    main()
