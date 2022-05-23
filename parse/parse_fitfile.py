import fitparse
from pylab import *

def parse_fitfile(filename, entry_dict, verbose = False):
    fitfile = fitparse.FitFile(filename)

    data_entry_list = [entry_name for entry_name in entry_dict.keys()] # build list of entries for which data will be collected
    if 'timestamp' in entry_dict.keys():
        print('Error: Special quantity "timestamp" was present in entry_dict.')
        exit()
    data_entry_list.append('timestamp')
    if 'seconds' in entry_dict.keys():
        print('Error: Special derived quantity "seconds" was present in entry_dict.')
        exit()
    data_entry_list.append('seconds')
    if 'slope' in entry_dict.keys():
        print('Error: Special derived quantity "slope" was present in entry_dict.')
        exit()

    calcSlope = True
    if 'distance' not in entry_dict.keys():
        cur_dist = 0. # at least initialize this variable
        calcSlope = False
    if 'altitude' not in entry_dict.keys():
        cur_alt = 0. # at least initialize this variable
        calcSlope = False
    if calcSlope:
        data_entry_list.append('slope')

    # build list of entries for which moving averages will be computed
    ma_entry_list = [entry_name for entry_name in entry_dict.keys() if len(entry_dict[entry_name]) > 0]

    # setup dictionaries
    data = {}
    mov_avgs = {}
    cur_hist = {}
    for entry_name in data_entry_list:
        data[entry_name] = [] # raw data
    for entry_name in ma_entry_list: # moving averages are desired
        mov_avgs[entry_name] = [([], []) for ma_len in entry_dict[entry_name]] # moving average data
        cur_hist[entry_name] = [zeros(ma_len) for ma_len in entry_dict[entry_name]] # current history helper arrays

    it = 0 # general iteration counter
    cont_it = 0 # continuous iteration counter of iterations with 1 sec delta
    tot_sec = 0  # count total seconds

    # Main loop for data extraction
    for record in fitfile.get_messages("record"):

        # pre-extract timestamp, distance and altitude of the record
        for entry in record:
            if entry.name == 'timestamp':
                cur_time = entry.value
            elif entry.name == 'distance' and entry.value != None: # quick fix, need to look into this
                cur_dist = entry.value
            elif entry.name == 'altitude':
                cur_alt = entry.value

        # check for discontinuity, compute time step, distance and height step
        time_diff = 0
        d_diff = 0
        h_diff = 0
        if it > 0:
            time_diff = cur_time - last_time
            time_diff = time_diff.total_seconds()
            d_diff = cur_dist - last_dist
            h_diff = cur_alt - last_alt
        if time_diff != 1:
            # reset moving average computation
            for ma_entry in ma_entry_list:
                for ch in cur_hist[ma_entry]:
                    ch.fill(0.)
            cont_it = 0
        # remember timestamp and altitude
        last_time = cur_time
        last_dist = cur_dist
        last_alt = cur_alt
        # increment total seconds
        tot_sec += time_diff


        # extract all data from record
        for entry in record:
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

            # put desired entry data into dictionaries
            data[entry.name].append(data_value)

            # if entry is desired, deal with moving averages
            if entry.name in ma_entry_list:
                # add to current history for moving averages
                for it_ma, ma_len in enumerate(entry_dict[entry.name]):
                    cur_hist[entry.name][it_ma][cont_it % ma_len] = data_value

                    # compute moving average value if possible
                    if cont_it >= ma_len:
                        mov_avgs[entry.name][it_ma][0].append(tot_sec)
                        mov_avgs[entry.name][it_ma][1].append(sum(cur_hist[entry.name][it_ma])/ma_len)

        # check if all desired entries were present
        present_entries = [entry.name for entry in record]
        for entry in entry_dict.keys():
            if entry not in present_entries:
                print('Error: Desired entry "', entry, '" was not present.')
                exit()
        if 'timestamp' not in present_entries:
            print('Error: Timestamp entry was not present.')
            exit()

        # add seconds data
        data['seconds'].append(tot_sec)

        # add slope data
        if calcSlope:
            if d_diff > 0:
                slope = h_diff / d_diff
            else:
                slope = 0
            data['slope'].append(slope)

        cont_it += 1  # increase continuous iteration counter
        it += 1  # increase general iteration counter

    # convert to numpy arrays
    for data_entry in data_entry_list:
        if data_entry != 'timestamp':
            data[data_entry] = array(data[data_entry])
    for ma_entry in ma_entry_list:
        for it_ma, ma_len in enumerate(entry_dict[ma_entry]):
            mov_avgs[ma_entry][it_ma] = (array(mov_avgs[ma_entry][it_ma][0]), array(mov_avgs[ma_entry][it_ma][1]))

    return data, mov_avgs
