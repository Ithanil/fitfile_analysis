import sys
from parse.parse_fitfile import parse_fitfile
from pylab import *

# settings
ma_lens = (10, 30, 90)
entry_dict = {'power' : ma_lens, 'heart_rate' : ma_lens}

# load&parse fit files
data_1, mavgs_1 = parse_fitfile(sys.argv[1], entry_dict, False)
data_2, mavgs_2 = parse_fitfile(sys.argv[2], entry_dict, False)

# shift seconds for second file's data
time_shift = float(sys.argv[3])
for it in range(len(data_2['seconds'])):
    data_2['seconds'][it] += time_shift
for entry in entry_dict.keys():
    for it_m in range(len(ma_lens)):
        for it in range(len(mavgs_2[entry][it_m][0])):
            mavgs_2[entry][it_m][0][it] += time_shift

# create scaled power array for second file
scaling_fac = float(sys.argv[4])
pw_2_scaled = scaling_fac*array([data_2['power'], mavgs_2['power'][0][1], mavgs_2['power'][1][1], mavgs_2['power'][2][1]], dtype=object)

# read optional start and end time
if len(sys.argv) >= 6:
    start_time = float(sys.argv[5])
else:
    start_time = data_1['seconds'][0]
if len(sys.argv) >= 7:
    end_time = float(sys.argv[6])
else:
    end_time = data_1['seconds'][-1]

# create coupled data set only with data points from times where there exists an entry in both data series / moving averages
coupled_data = {}
for entry in entry_dict:
    if entry in data_1.keys() and entry in data_2.keys():
        coupled_data[entry] = (([], [], []), ([], [], []), ([], [], []), ([], [], []))  # data, ma0, ma1, ma2
        its = 0
        for series_1, series_2 in [((data_1['seconds'], data_1[entry]), (data_2['seconds'], data_2[entry])), (mavgs_1[entry][0], mavgs_2[entry][0]),
                                   (mavgs_1[entry][1], mavgs_2[entry][1]), (mavgs_1[entry][2], mavgs_2[entry][2])]:
            itd2 = 0
            for itd1, t1 in enumerate(series_1[0]):
                # check start/end time condition
                if t1 < start_time:
                    continue
                if t1 > end_time:
                    break

                # skip to sync times
                while series_2[0][itd2] < t1 and itd2 < (len(series_2[0]) - 1):
                    itd2 += 1

                # couple data
                if series_2[0][itd2] == t1:
                    coupled_data[entry][its][0].append(t1)
                    coupled_data[entry][its][1].append(series_1[1][itd1])
                    if entry == 'power':
                        coupled_data[entry][its][2].append(scaling_fac*series_2[1][itd2])
                    else:
                        coupled_data[entry][its][2].append(series_2[1][itd2])
            its += 1

# compute averages and mean, mean absolute and root mean square differences
labels = ['raw data', 'mov avg ' + str(ma_lens[0]) + 's', 'mov avg '
          + str(ma_lens[1]) + 's', 'mov avg ' + str(ma_lens[2]) + 's']
for name in coupled_data.keys():
    print('')
    print(name + ':')
    for it_label, cdat in enumerate(coupled_data[name]):
        avg1 = 0.
        avg2 = 0.
        md = 0.
        mad = 0.
        rmsd = 0.
        datlen = len(cdat[0])
        for it in range(datlen):
            avg1 += cdat[1][it]
            avg2 += cdat[2][it]
            diff = cdat[1][it] - cdat[2][it]
            md += diff
            mad += abs(diff)
            rmsd += diff**2
        avg1 /= datlen
        avg2 /= datlen
        md /= datlen
        mad /= datlen
        rmsd = sqrt(rmsd/datlen)
        print(labels[it_label], (avg1, avg2), md, mad, rmsd)


for entry in coupled_data.keys():
    figure()
    suptitle(entry)
    for it in range(4):
        subplot(2, 2, it+1)
        plot(coupled_data[entry][it][0], coupled_data[entry][it][1])
        plot(coupled_data[entry][it][0], coupled_data[entry][it][2])
        if it == 1:
            legend([sys.argv[1], sys.argv[2]])

for it_ma, ma_len in enumerate(ma_lens):
    figure()
    suptitle('Powers ' + str(ma_len) + ' Sec MA, with&without scaling')
    subplot(2, 1, 1)
    plot(mavgs_1['power'][it_ma][0], mavgs_1['power'][it_ma][1])
    plot(mavgs_2['power'][it_ma][0], pw_2_scaled[it_ma + 1])
    legend([sys.argv[1], sys.argv[2]])
    subplot(2, 1, 2)
    plot(mavgs_1['power'][it_ma][0], mavgs_1['power'][it_ma][1])
    plot(mavgs_2['power'][it_ma][0], mavgs_2['power'][it_ma][1])

show()
