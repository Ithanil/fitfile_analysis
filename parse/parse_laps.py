import fitparse
from numpy import array, double

def parse_laps(filename, entry_dict, verbose = False):
    fitfile = fitparse.FitFile(filename)

    data_entry_list = [entry_name for entry_name in entry_dict.keys()] # build list of entries for which data will be collected
    if 'timestamp' in entry_dict.keys():
        print('Error: Special quantity "timestamp" was present in entry_dict.')
        exit()
    data_entry_list.append('timestamp')

    # setup data list and iteration counter
    data = []
    it = 0

    # Main loop for data extraction
    for lap in fitfile.get_messages("laps"):
        data.append({}) # create empty dict for lap

        # extract all data from lap
        for entry in lap:
            if entry.name not in data_entry_list:
                continue  # skip irrelevant entries

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

        # check if all desired entries were present
        present_entries = [entry.name for entry in lap]
        for entry in entry_dict.keys():
            if entry not in present_entries:
                print('Warning: Desired entry "', entry, '" was not present.')
                data[it][entry] = None
        if 'timestamp' not in present_entries:
            print('Error: Timestamp entry was not present.')
            exit()

        it += 1  # increase iteration counter

    return data
