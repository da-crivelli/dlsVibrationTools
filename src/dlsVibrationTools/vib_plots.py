import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter

from dlsVibrationTools.vc_curves import VC_LABELS, VC_UPPER_LIMIT

# if this line isn't here, seaborn explodes. Not sure why. Worked it out from:
# https://medium.com/@darektidwell1980/typeerror-float-argument-must-be-a-string-or-a-number-not-period-facebook-prophet-and-pandas-6b74a23fc47b
pd.plotting.register_matplotlib_converters()


def plot_vc_timeseries(data: pd.DataFrame, vc_gridlines: list = [3, 10]) -> None:
    """generates a timeseries plot of the VC level with appropriate labels.
    Mostly a shortcut for a seaborn plot with some decoration.

    Args:
        data (pandas.DataFrame): vibration dataframe from fetch_pv_to_dataframe
        vc_gridlines (list, optional): reference VC grid lines to show. Defaults to [3,10].
    """

    # TODO: maybe do all the preliminary stuff as a decorator

    # sns.set_theme(style="ticks")

    fg = plt.figure()

    ax = sns.lineplot(data=data, x="Time", y="VC_Peak", hue="PV")

    # VC reference lines
    end_date = data["Time"].max()

    for (limit, label) in zip(
        VC_UPPER_LIMIT[vc_gridlines[0] : vc_gridlines[1]],
        VC_LABELS[vc_gridlines[0] : vc_gridlines[1]],
    ):
        plt.axhline(limit, linestyle="dotted", color=[0.5, 0.5, 0.5])
        plt.text(x=end_date, y=limit, s="VC-" + label)

    ax.set(ylabel="Peak 1/3 octave velocity (m/s)", yscale="log")

    fg.figure.autofmt_xdate()

    plt.show()


def plot_vc_histograms(data: pd.DataFrame) -> None:
    plt.figure()

    ax = sns.displot(data=data, x="VC_Peak", hue="PV", kde=True, fill=True)
    ax.set(xlabel="Peak 1/3 octave velocity (m/s)", xscale="log")

    plt.show()
