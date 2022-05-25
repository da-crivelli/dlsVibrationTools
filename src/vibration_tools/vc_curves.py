from string import ascii_uppercase
import numpy as np

# VC levels 
VC_UPPER_LIMIT = np.array([0.012, 0.024, 0.048, 0.097, 0.195, 0.39, 0.78, 1.56, 3.12, 6.25, 12.5, 25, 50])*1e-6
VC_LABELS = list(ascii_uppercase)[0:len(VC_UPPER_LIMIT)][::-1]

def vc_get_level(val: float) -> str:
    """Return the VC level key (letter) from a 1/3 octave velocity in m/s

    This function maps VC_UPPER_LIMIT velocities to VC level labels, according to IEST-RP-CC012 (paywalled). The original paper (with out of date values) is available as:
    
    Colin G. Gordon, "Generic vibration criteria for vibration-sensitive equipment," Proc. SPIE 3786, Optomechanical Engineering and Vibration Control, (28 September 1999); https://doi.org/10.1117/12.363802

    Note that this does not meet IEST on VC-B and above, as we are not relaxing <8Hz on VC-A and VC-B for brevity. This is a conservative approach for us.

    Args:
        val (float): value of the 1/3 velocity peak

    Returns:
        str: uppercase VC level ([A-M]) or "ISO" if above 50 um/s
    """
    try:
        return VC_LABELS[np.searchsorted(VC_UPPER_LIMIT, val)]
    except IndexError:
        return 'ISO'
    
def vc_get_threshold(vc_label: str) -> float:
    """Returns the 1/3 velocity threshold in m/s corresponding to the VC-level specified as an input

    Args:
        vc_label (str): VC level [A-M] 

    Returns:
        float: 1/3 velocity threshold limit for specified VC level.
    """
    return VC_UPPER_LIMIT[VC_LABELS.index(vc_label)]

