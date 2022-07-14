import fitparse
from numpy import array, double

def parse_laps(filename, verbose = False):
    fitfile = fitparse.FitFile(filename)

    # setup data list and iteration counter
    data = []
    it = 0

    # Main loop for data extraction
    for lap in fitfile.get_messages("lap"):
        data.append({}) # create empty dict for lap

        # extract all data from lap
        for entry in lap:
            # --- Pre-Processing of entry values ---

            # convert 'None' values to 0
            if entry.value == None:
                data_value = 0
            else:
                data_value = entry.value

            # L/R balance processing
            if entry.name == 'left_right_balance':
               # exception for weird l/r-balance values ('left'/'right') occurring at 0 power with Assiomas
                if data_value == 'left' or data_value == 'right':
                    data_value = 50 # i.e. directly set to 50%
                else: # convert to proper % value
                    data_value -= 128

            # convert speed from m/s to km/h
            if entry.name == 'speed':
                data_value *= 3.6

            # convert longitude/latitude to decimal degrees
            if entry.name == 'position_lat' or entry.name == 'position_long':
                data_value /= 11930465.

            # Print the name and value of the data (and the units if it has any)
            if verbose:
                if entry.units:
                    print(" * {}: {} ({})".format(entry.name, data_value, entry.units))
                else:
                    print(" * {}: {}".format(entry.name, data_value))
                print("---")

            # ----------

            # put desired entry data into dictionary
            data[it][entry.name] = data_value

        it += 1  # increase iteration counter

    # create list of start/end timestamps
    timestamps = []
    for lap in data:
        timestamps.append([lap['start_time'], lap['timestamp']])

    return data, timestamps
