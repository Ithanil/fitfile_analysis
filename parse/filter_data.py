from numpy import array, double
from scipy.signal import savgol_filter

def filter_data(data, entry_dict):
# Function to apply Savitzky-Golay filter to certain entries in data dictionary
# entry_dict contains entry names as keys anda filter parameters as value tuple
# returns new data dictionary with desired entries filtered, others untouched
    data_filt = {}
    for key in data.keys():
        if key in entry_dict.keys():
            data_filt[key] = savgol_filter(data[key], entry_dict[key][0], entry_dict[key][1])
        else:
            data_filt[key] = data[key].copy()

    return data_filt