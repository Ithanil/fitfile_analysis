import sys
import fitparse

from pylab import *

# settings
ma_len = 30
ma_names = ['speed', 'power', 'heart_rate', 'cadence', 'left_right_balance']

# Load the FIT file
fitfile = fitparse.FitFile(sys.argv[1])

data = {}
mavgs = {}
cur_hist = {}
for name in ma_names:
    mavgs[name] = ([], [])
    cur_hist[name] = np.zeros(ma_len)
ma_it = 0
it = 0

# Iterate over all messages of type "record"
for record in fitfile.get_messages("record"):
    # pre-extract timestamp of the record
    for entry in record:
        if entry.name == 'timestamp':
            cur_time = entry.value

    # Records can contain multiple pieces of data (ex: timestamp, latitude, longitude, etc)
    for entry in record:
        # Print the name and value of the data (and the units if it has any)
    #    if entry.units:
    #        print(" * {}: {} ({})".format(entry.name, entry.value, entry.units))
    #    else:
    #        print(" * {}: {}".format(entry.name, entry.value))
#    print("---")

        # put desired entry data into dictionaries
        if entry.name not in data.keys():
            data[entry.name] = []
        data[entry.name].append(entry.value)

        # if entry is not timestamp, deal with moving averages
        if entry.name != 'timestamp':
            if entry.name in ma_names:
                # add to current history for moving averages
                cur_hist[entry.name][ma_it] = entry.value

                # compute moving average value if possible
                if it >= ma_len:
                    mavgs[entry.name][0].append(cur_time)
                    mavgs[entry.name][1].append(sum(cur_hist[entry.name])/ma_len)

    ma_it = (ma_it + 1)%ma_len # update index for moving average history
    it += 1 # increase general iteration counter

print(data.keys())

# convert all ma data to numpy array
for name in ma_names:
    mavgs[name] = (mavgs[name][0], array(mavgs[name][1]))

# convert LR-balance values to proper %
for data_it in range(len(mavgs['left_right_balance'][1])):
    mavgs['left_right_balance'][1][data_it] -= 128
print(mavgs['left_right_balance'][1])
#except:
#    pass

for name in ma_names:
    print(name, len(mavgs[name][0]), len(mavgs[name][1]))
    figure()
    title(name)
    #plot(data['timestamp'], data[name])
    plot(mavgs[name][0], mavgs[name][1])

show()
