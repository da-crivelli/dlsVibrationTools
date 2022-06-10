import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from dlsVibrationTools.vc_curves import VC_LABELS, VC_UPPER_LIMIT

# if this line isn't here, seaborn explodes. Not sure why. Worked it out from:
# https://medium.com/@darektidwell1980/typeerror-float-argument-must-be-a-string-
# or-a-number-not-period-facebook-prophet-and-pandas-6b74a23fc47b
pd.plotting.register_matplotlib_converters()


# TODO: turn this into a library so it can store the dataframes etc


def plot_vc_timeseries(data: pd.DataFrame, vc_gridlines: list = [3, 10]) -> None:
    """generates a timeseries plot of the VC level with appropriate labels.
    Mostly a shortcut for a seaborn plot with some decoration.

    Args:
        data (pandas.DataFrame): vibration dataframe from fetch_pv_to_dataframe
        vc_gridlines (list, optional): reference VC lines to show. Defaults to [3,10].
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

    # FIXME: these seem to open an extra plot window for some reason

    # TODO: add VC reference gridlines


def plot_spectrogram(data: pd.DataFrame, freq_range: list = [2, 400]) -> None:

    # TODO: this is assuming a single channel
    fig, (ax_spec, ax_fft) = plt.subplots(1, 2)
    v = np.stack(data["FFT"].to_numpy())
    v = v[:, freq_range[0] : freq_range[1]]

    vmax = np.max(v, 0)
    vmean = np.mean(v, 0)

    time = data["Time"]
    freq = np.arange(freq_range[0], freq_range[1], 1)

    # FIXME: RuntimeWarning: divide by zero encountered in log10
    # 10.0 * np.log10(np.transpose(v)),
    ax_spec.pcolormesh(
        time,
        freq,
        10.0 * np.log10(np.transpose(v)),
        rasterized=True,
    )

    ax_spec.set_xlabel("Time")
    ax_spec.set_ylabel("Frequency (Hz)")

    # TODO: remove hardcoded frequency limits

    # TODO: add average FFT and VC time series

    ax_spec.figure.autofmt_xdate()

    # average and maxhold FFT
    # TODO: add labels and sharey
    ax_fft.plot(vmean, freq)
    ax_fft.plot(vmax, freq)
    ax_fft.set_xscale("log")

    plt.show()

    #
