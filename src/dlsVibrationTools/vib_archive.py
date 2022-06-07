from datetime import datetime
from os import environ

import pandas as pd
from aa.js import JsonFetcher

from dlsVibrationTools.vc_curves import vc_get_level, vc_get_threshold


class vib_archive:
    implemented_variables = ("VC_PEAK", "FFT")  # PVs currently supported
    default_beamline = "i20"

    def __init__(
        self,
        appliance_url="archappl.diamond.ac.uk",
        pv_mask: str = "{beamline}-DI-ACCEL-{id:02}:DATA:CH{chan:02}:{var}",
        beamline: str = None,
    ) -> None:

        self.appliance_url = appliance_url
        self.pv_mask = pv_mask

        if beamline is None:
            self.beamline = self.get_current_beamline_canonical()
        else:
            pass

    def build_pv_names(
        self,
        beamline: str,
        variable: str,
        id: int = 1,
        channels: list = [1],
    ) -> list:
        """builds a PV name based on its component

        Args:
            beamline (str): current beamline (in the "i20..." format)
            variable (str): which PV to retrieve
            id (int, optional): _description_. Defaults to 1.
            channels (list, optional): _description_. Defaults to [1].

        Raises:
            NotImplementedError: _description_

        Returns:
            _type_: _description_
        """

        if variable not in self.implemented_variables:
            raise NotImplementedError()

        PVs = [
            self.pv_mask.format(beamline=beamline, id=id, chan=chan, var=variable)
            for chan in channels
        ]

        return PVs

    def get_current_beamline_canonical(self) -> str:
        """returns the canonical (BL20I / BL20J...) name for the current beamline,
        inferred from the BEAMLINE environment variable. Defaults to
        self.default_beamline if not specified.

        Returns:
            beamline (str): the canonical current beamline
        """
        try:
            beamline = environ["BEAMLINE"]
        except KeyError:
            beamline = self.default_beamline
            # TODO: log this

        # let's make the name "canonical" (from i20 to BL20I)
        if beamline[0] in ("i", "j", "k"):
            beamline = "BL{0}{1}".format(beamline[1:], beamline[0].upper())
        else:
            raise NotImplementedError()
            # TODO: log this
        return beamline

    def fetch_pv_to_dataframe(
        self, pv_name: str, start_date: datetime, end_date: datetime, channels: list
    ) -> pd.DataFrame:
        """retrieves a vibration PV from the Diamond archiver appliance, returns it as
        a dataframe with some useful calculated fields

        Args:
            pv_name (str): EPICS PV full name
            start_date (datetime): datetime, start of data.
            end_date (datetime): datetime, end of data
            channels (list): list of channels

        Returns:
            pd.DataFrame: a Pandas dataframe including the PV augmented with further
                          useful data
        """

        jf = JsonFetcher(self.appliance_url, 80)

        # TODO: support multiple PVs (maybe from the base system PV and automatically
        #       build labels etc?)
        # TODO: check for timezone, if not present throw a warning and assume UTC

        pv_fullnames = self.build_pv_names(
            beamline=self.beamline, variable=pv_name, channels=channels
        )

        df = pd.DataFrame()

        for pv in pv_fullnames:
            this_pv_df = pd.DataFrame()
            data = jf.get_values(pv, start_date, end_date)

            this_pv_df["Time"] = data.utc_datetimes
            this_pv_df["VC_Peak"] = data.values
            this_pv_df["VC_Level"] = this_pv_df.apply(
                lambda x: vc_get_level(x["VC_Peak"]), axis=1
            )

            this_pv_df["dT"] = this_pv_df["Time"].shift(-1) - this_pv_df["Time"]
            this_pv_df["dT_Seconds"] = this_pv_df.apply(
                lambda x: x["dT"].total_seconds(), axis=1
            )  # needed for histplot

            this_pv_df["PV"] = pv
            df = pd.concat([df, this_pv_df], axis=0).reset_index(drop=True)

        df["PV"] = df["PV"].astype("category")
        df["VC_Level"] = df["VC_Level"].astype("category")
        return df


def get_vib_alarms(data: pd.DataFrame, vc_threshold: str = "G"):
    """returns a dataframe of alarms including time and duration

    Args:
        data (pandas.DataFrame): vibration dataframe from fetch_pv_to_dataframe
        vc_threshold (str, optional): threshold for raising an alarm. Defaults to "G".
    """

    # TODO: add an exclusion times PV (list of tuples?)
    vc_alarm_val = vc_get_threshold(vc_threshold)

    # TODO: when supporting multiple PVs, it will need grouping by channel before doing
    # these next bits
    data["VC_Alarm"] = data.apply(
        lambda x: False if x["VC_Peak"] < vc_alarm_val else True, axis=1
    )

    # TODO: can we avoid adding a column altogether and creating alarm_list from the
    # lambda function above?
    alarm_list = data.loc[data["VC_Alarm"]].copy()

    alarm_list["Time_To_Next"] = alarm_list["Time"].shift(-1) - alarm_list["Time"]
