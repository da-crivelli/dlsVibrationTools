import logging
import logging.config
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from datetime import datetime
from multiprocessing import Process

import yaml

from dlsVibrationTools import __version__
from dlsVibrationTools.vib_archive import vib_archive
from dlsVibrationTools.vib_plots import (
    plot_spectrogram,
    plot_vc_histograms,
    plot_vc_timeseries,
)

__all__ = ["main"]


def logging_setup():

    with open("logging.conf.yml", "r") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)

    # logging = logging.getLogging(__name__)
    # handler = logging.StreamHandler()
    # log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    # )
    # handler.setFormatter(formatter)
    # logging.addHandler(handler)
    # logging.setLevel(logging.DEBUG)

    # return logging

    # logging.basicConfig(format=log_format, level=logging.INFO)


def main(args=None):

    # logging set up
    logging_setup()

    # TODO: this should really live outside of this
    # FIXME: return carriages aren't really workin
    epilog_text = """
    Example:

    pipenv run vibration-report
    pipenv run vibration-report --help
    pipenv run vibration-report --start="2022-06-08 12:00" --end="2022-06-08 13:00"
    """

    # input parsing
    parser = ArgumentParser(
        description="Vibration data analysis script",
        epilog=epilog_text,
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument("--version", action="version", version=__version__)

    # date/time parsing
    # TODO: actually use these values...
    parser.add_argument(
        "--start", nargs=1, help='start datetime: "YYYY-MM-DD HH:MM:SS"'
    )
    parser.add_argument("--end", nargs=1, help='end datetime:  "YYYY-MM-DD HH:MM:SS"')

    args = parser.parse_args(args)

    # TODO: allow multiple plot types
    plot_type = "spectrogram"
    logging.warning("""Plot selection not implemented, this is hardcoded for now""")

    # parse args and get data
    arch = vib_archive()
    logging.warning(
        (
            "IOC selection not implemented - defaulting to "
            "I20 vibration kit for now, or local machine if on a beamline"
        )
    )
    # create a vibration archive object

    # TODO: this is for testing only
    if plot_type == "vc":
        start_date = datetime(2022, 5, 4).astimezone()
        end_date = datetime(2022, 5, 5).astimezone()
    elif plot_type == "spectrogram":
        start_date = datetime(2022, 5, 4, 12, 0, 0).astimezone()
        end_date = datetime(2022, 5, 4, 12, 10, 0).astimezone()
    else:
        raise NotImplementedError

    logging.warning("""Date selection currently hardcoded for testing purposes""")

    # end_date = datetime.now(timezone.utc).astimezone()
    # start_date = end_date - timedelta(hours=24*7)

    # TODO: turn this into a dictionary type match, throwing notImplemented otherwise
    if plot_type == "vc":
        pv_name = "VC_PEAK"
    elif plot_type == "spectrogram":
        pv_name = "FFT"
    else:
        raise NotImplementedError

    logging.warning(
        "Channel selection ont implemented - defaulting to channel 1 for now"
    )

    # Threshold for "alarms" report (will trigger if above the velocity
    # required to meet this level's spec)
    vc_threshold = "G"
    logging.warning("VC level not implemented - defaulting to VC-G alarms for now!")

    # fetch data & display
    logging.info("Fetching data from EPICS...")

    df = arch.fetch_pv_to_dataframe(
        pv_name=pv_name, start_date=start_date, end_date=end_date, channels=[1]
    )

    # print(df.head())
    # print(df.info())

    # TODO: this needs to be done in a loop... or dictionary match. please
    if plot_type == "vc":
        p1 = Process(target=plot_vc_timeseries, args=(df,))
        p1.start()

        p2 = Process(target=plot_vc_histograms, args=(df,))
        p2.start()
    elif plot_type == "spectrogram":
        p1 = Process(target=plot_spectrogram, args=(df,))
        p1.start()
    else:
        raise NotImplementedError

    p1.join()

    if plot_type == "vc":
        p2.join()


# test with: pipenv run python -m dlsVibrationTools
if __name__ == "__main__":
    main()
