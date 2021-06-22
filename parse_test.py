import sys
import fitparse

from pylab import *

# settings
ma_len_0 = 3
ma_len_1 = 30
ma_len_2 = 300
ma_names = ['speed', 'power', 'heart_rate', 'cadence', 'left_right_balance']

# Load the FIT file
fitfile = fitparse.FitFile(sys.argv[1])

data = {}
mavgs_0 = {}
mavgs_1 = {}
mavgs_2 = {}
for name in ma_names:
    mavgs_0[name] = ([], [])
    mavgs_1[name] = ([], [])
    mavgs_2[name] = ([], [])
it = 0 # general iteration counter

# Main loop for data extraction
for record in fitfile.get_messages("record"):

    # pre-extract timestamp of the record
    for entry in record:
        if entry.name == 'timestamp':
            cur_time = entry.value

    # check for discontinuity
    time_diff = 0
    if it > 0:
        time_diff = cur_time - last_time
        time_diff = time_diff.total_seconds()
    if time_diff != 1:
        # initialize or reset moving average computation
        cur_hist_0 = {}
        cur_hist_1 = {}
        cur_hist_2 = {}
        for name in ma_names:
            cur_hist_0[name] = np.zeros(ma_len_0)
            cur_hist_1[name] = np.zeros(ma_len_1)
            cur_hist_2[name] = np.zeros(ma_len_2)
        ma_it_0 = 0
        ma_it_1 = 0
        ma_it_2 = 0
        cont_it = 0 # counter of continuous data points with 1 sec delta
    # remember timestamp
    last_time = cur_time

    # extract all data from record
    for entry in record:

        # --- Pre-Processing of entry values ---

        # convert 'None' values to 0
        if entry.value == None:
            data_value = 0
        else:
            data_value = entry.value

        # L/R balance processing
        if entry.name == 'left_right_balance':
           # exception for weird l/r-balance values ('left'/'right') occuring at 0 power with Assiomas
            if data_value == 'left' or data_value == 'right':
                data_value = 50 # i.e. directly set to 50% 
            else: # convert to proper % value
                data_value -= 128

        # convert speed from m/s to km/h
        if entry.name == 'speed':
            data_value *= 3.6

        # Print the name and value of the data (and the units if it has any)
        #if entry.units:
        #    print(" * {}: {} ({})".format(entry.name, data_value, entry.units))
        #else:
        #    print(" * {}: {}".format(entry.name, data_value))
        #print("---")

        # ----------

        # put desired entry data into dictionaries
        if entry.name not in data.keys():
            data[entry.name] = []
        data[entry.name].append(data_value)

        # if entry is not timestamp, deal with moving averages
        if entry.name != 'timestamp':
            if entry.name in ma_names:
                try:
                    # add to current history for moving averages
                    cur_hist_0[entry.name][ma_it_0] = data_value
                    cur_hist_1[entry.name][ma_it_1] = data_value
                    cur_hist_2[entry.name][ma_it_2] = data_value

                    # compute moving average value if possible
                    if cont_it >= ma_len_0:
                        mavgs_0[entry.name][0].append(cur_time)
                        mavgs_0[entry.name][1].append(sum(cur_hist_0[entry.name])/ma_len_0)
                    if cont_it >= ma_len_1:
                        mavgs_1[entry.name][0].append(cur_time)
                        mavgs_1[entry.name][1].append(sum(cur_hist_1[entry.name])/ma_len_1)
                    if cont_it >= ma_len_2:
                        mavgs_2[entry.name][0].append(cur_time)
                        mavgs_2[entry.name][1].append(sum(cur_hist_2[entry.name])/ma_len_2)
                except:
                    print('Error when processing entry: ', entry)
                    exit()

    # update indices for moving average history
    ma_it_0 = (ma_it_0 + 1)%ma_len_0
    ma_it_1 = (ma_it_1 + 1)%ma_len_1
    ma_it_2 = (ma_it_2 + 1)%ma_len_2
    cont_it += 1 # increase continuous iteration counter
    it += 1 # increase general iteration counter

print(data.keys())

# convert all ma data to numpy array
for name in ma_names:
    mavgs_0[name] = (mavgs_0[name][0], array(mavgs_0[name][1]))
    mavgs_1[name] = (mavgs_1[name][0], array(mavgs_1[name][1]))
    mavgs_2[name] = (mavgs_2[name][0], array(mavgs_2[name][1]))

for name in ma_names:
    print(name, len(mavgs_1[name][0]), len(mavgs_1[name][1]), len(mavgs_2[name][0]), len(mavgs_2[name][1]))
    figure()
    title(name)
#    plot(data['timestamp'], data[name])
    plot(mavgs_0[name][0], mavgs_0[name][1], '*', markersize = 4)
    plot(mavgs_1[name][0], mavgs_1[name][1], '*', markersize = 4)
    plot(mavgs_2[name][0], mavgs_2[name][1], '*', markersize = 4)

show()
