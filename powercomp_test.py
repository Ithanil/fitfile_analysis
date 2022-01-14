import sys
import fitparse

from pylab import *

# settings
ma_len_0 = 10
ma_len_1 = 30
ma_len_2 = 90
ma_names = ['speed', 'power', 'heart_rate', 'cadence', 'left_right_balance']
verbose = False

# Load the FIT files
fitfiles = [fitparse.FitFile(sys.argv[1]), fitparse.FitFile(sys.argv[2])]

data = [{}, {}]
mavgs_0 = [{}, {}]
mavgs_1 = [{}, {}]
mavgs_2 = [{}, {}]
for itf in [0,1]:
    for name in ma_names:
        mavgs_0[itf][name] = ([], [])
        mavgs_1[itf][name] = ([], [])
        mavgs_2[itf][name] = ([], [])

# Main loop for data extraction
for itf, fitfile in enumerate(fitfiles):

    it = 0  # general iteration counter
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
            if verbose:
                if entry.units:
                    print(" * {}: {} ({})".format(entry.name, data_value, entry.units))
                else:
                    print(" * {}: {}".format(entry.name, data_value))
                print("---")

            # ----------

            # put desired entry data into dictionaries
            if entry.name not in data[itf].keys():
                data[itf][entry.name] = ([], [])
            data[itf][entry.name][0].append(cur_time)
            data[itf][entry.name][1].append(data_value)

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
                            mavgs_0[itf][entry.name][0].append(cur_time)
                            mavgs_0[itf][entry.name][1].append(sum(cur_hist_0[entry.name])/ma_len_0)
                        if cont_it >= ma_len_1:
                            mavgs_1[itf][entry.name][0].append(cur_time)
                            mavgs_1[itf][entry.name][1].append(sum(cur_hist_1[entry.name])/ma_len_1)
                        if cont_it >= ma_len_2:
                            mavgs_2[itf][entry.name][0].append(cur_time)
                            mavgs_2[itf][entry.name][1].append(sum(cur_hist_2[entry.name])/ma_len_2)
                    except:
                        print('Error when processing entry: ', entry)
                        exit()

        # update indices for moving average history
        ma_it_0 = (ma_it_0 + 1)%ma_len_0
        ma_it_1 = (ma_it_1 + 1)%ma_len_1
        ma_it_2 = (ma_it_2 + 1)%ma_len_2
        cont_it += 1 # increase continuous iteration counter
        it += 1 # increase general iteration counter

print(data[0].keys())

# convert all ma data to numpy array
for itf in [0,1]:
    for name in ma_names:
        if name in data[itf].keys():
            data[itf][name] = (array(data[itf][name][0]), array(data[itf][name][1]))
        mavgs_0[itf][name] = (mavgs_0[itf][name][0], array(mavgs_0[itf][name][1]))
        mavgs_1[itf][name] = (mavgs_1[itf][name][0], array(mavgs_1[itf][name][1]))
        mavgs_2[itf][name] = (mavgs_2[itf][name][0], array(mavgs_2[itf][name][1]))

# create scaled power array for second file
if len(sys.argv) >= 4:
    scaling_fac = float(sys.argv[3])
else:
    scaling_fac = 1.0
pw_0_scaled = scaling_fac*array(mavgs_0[1]['power'][1])
pw_1_scaled = scaling_fac*array(mavgs_1[1]['power'][1])
pw_2_scaled = scaling_fac*array(mavgs_2[1]['power'][1])

# create coupled data set only with data points from times where there exists an entry in both data series / moving averages
coupled_data = {}
for name in ma_names:
    if name in data[0].keys() and name in data[1].keys():
        coupled_data[name] = (([], [], []), ([], [], []), ([], [], []), ([], [], [])) # data, ma0, ma1, ma2
        its = 0
        for series0, series1 in [(data[0][name], data[1][name]), (mavgs_0[0][name], mavgs_0[1][name]),
                                 (mavgs_1[0][name], mavgs_1[1][name]), (mavgs_2[0][name], mavgs_2[1][name])]:
            itd1 = 0
            for itd0, t0 in enumerate(series0[0]):
                while series1[0][itd1] < t0 and itd1 < (len(series1[0]) - 1) :
                    itd1 += 1
                if series1[0][itd1] == t0:
                    coupled_data[name][its][0].append(t0)
                    coupled_data[name][its][1].append(series0[1][itd0])
                    coupled_data[name][its][2].append(series1[1][itd1])
            its += 1

# compute averages and mean, mean absolute and root mean square differences
labels = ['raw data', 'mov avg ' + str(ma_len_0) + 's', 'mov avg '
          + str(ma_len_1) + 's', 'mov avg ' + str(ma_len_2) + 's']
for name in coupled_data.keys():
    print('')
    print(name + ':')
    for it_label, cdat in enumerate(coupled_data[name]):
        avg0 = 0.
        avg1 = 0.
        md = 0.
        mad = 0.
        rmsd = 0.
        datlen = len(cdat[0])
        for it in range(datlen):
            avg0 += cdat[1][it]
            avg1 += cdat[2][it]
            diff = cdat[1][it] - cdat[2][it]
            md += diff
            mad += abs(diff)
            rmsd += diff**2
        avg0 /= datlen
        avg1 /= datlen
        md /= datlen
        mad /= datlen
        rmsd = sqrt(rmsd/datlen)
        print(labels[it_label], (avg0, avg1), md, mad, rmsd)


for name in coupled_data.keys():
    figure()
    title(name)
    plot(coupled_data[name][0][0], coupled_data[name][0][1])
    plot(coupled_data[name][0][0], coupled_data[name][0][2])
    legend([sys.argv[1], sys.argv[2]])

figure()
title('Powers ' + str(ma_len_1) + ' Sec MA')
plot(mavgs_1[0]['power'][0], mavgs_1[0]['power'][1])
plot(mavgs_1[1]['power'][0], mavgs_1[1]['power'][1])
legend([sys.argv[1], sys.argv[2]])

figure()
title('Powers '  + str(ma_len_2) + ' Sec MA')
plot(mavgs_2[0]['power'][0], mavgs_2[0]['power'][1])
plot(mavgs_2[1]['power'][0], mavgs_2[1]['power'][1])
legend([sys.argv[1], sys.argv[2]])

figure()
title('Powers with Scaling, ' + str(ma_len_1) + ' Sec MA')
plot(mavgs_1[0]['power'][0], mavgs_1[0]['power'][1])
plot(mavgs_1[1]['power'][0], pw_1_scaled)
legend([sys.argv[1], sys.argv[2]])

figure()
title('Powers with Scaling, '  + str(ma_len_2) + ' Sec MA')
plot(mavgs_2[0]['power'][0], mavgs_2[0]['power'][1])
plot(mavgs_2[1]['power'][0], pw_2_scaled)
legend([sys.argv[1], sys.argv[2]])

show()
