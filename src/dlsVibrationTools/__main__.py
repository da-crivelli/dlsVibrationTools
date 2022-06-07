import logging
from argparse import ArgumentParser
from datetime import datetime
from multiprocessing import Process

from dlsVibrationTools.vib_archive import vib_archive
from dlsVibrationTools.vib_plots import plot_vc_histograms, plot_vc_timeseries

from . import __version__

__all__ = ["main"]


def main(args=None):

    # logging set up
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    # input parsing
    parser = ArgumentParser()
    parser.add_argument("--version", action="version", version=__version__)

    args = parser.parse_args(args)

    # parse args and get data
    arch = vib_archive()
    logger.warning(
        """IOC selection not implemented - defaulting to
        I20 vibration kit for now, or local machine if on a beamline"""
    )
    # create a vibration archive object

    start_date = datetime(2022, 5, 4).astimezone()
    end_date = datetime(2022, 5, 5).astimezone()
    df = arch.fetch_pv_to_dataframe(
        pv_name="VC_PEAK", start_date=start_date, end_date=end_date, channels=[1, 2]
    )

    logger.warning(
        "Channel selection ont implemented - defaulting to channel 1 for now"
    )

    # end_date = datetime.now(timezone.utc).astimezone()
    # start_date = end_date - timedelta(hours=24*7)

    logger.warning(
        "Date range not implemented - defaulting to fixed date range for now"
    )

    # Threshold for "alarms" report (will trigger if above the velocity
    # required to meet this level's spec)
    vc_threshold = "G"
    logger.warning("VC level not implemented - defaulting to VC-G alarms for now!")

    # fetch data & display
    logger.info("Fetching data from EPICS...")

    print(df.head())
    print(df.info())

    p1 = Process(target=plot_vc_timeseries, args=(df,))
    p1.start()

    p2 = Process(target=plot_vc_histograms, args=(df,))
    # TODO: add histograms
    p2.start()
    # TODO: add spectrogram

    p1.join()
    p2.join()


# test with: pipenv run python -m dlsVibrationTools
if __name__ == "__main__":
    main()
