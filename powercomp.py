import sys
from parse.parse_fitfile import parse_fitfile
from pylab import *

# settings
ma_lens = (5, 30, 180)
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
if len(sys.argv) >= 5:
    scaling_fac = float(sys.argv[4])
else:
    scaling_fac = 1.0
pw_2_scaled = scaling_fac*array([data_2['power'], mavgs_2['power'][0][1], mavgs_2['power'][1][1], mavgs_2['power'][2][1]], dtype=object)

# create coupled data set only with data points from times where there exists an entry in both data series / moving averages
coupled_data = {}
for entry in entry_dict:
    if entry in data_1.keys() and entry in data_2.keys():
        coupled_data[entry] = (([], [], []), ([], [], []), ([], [], []), ([], [], []))  # data, ma0, ma1, ma2
        its = 0
        for series_1, series_2 in [((data_1['seconds'], data_1[entry]), (data_2['seconds'], data_2[entry])), (mavgs_1[entry][0], mavgs_2[entry][0]),
                                   (mavgs_1[entry][1], mavgs_2[entry][1]), (mavgs_1[entry][2], mavgs_2[entry][2])]:
            itd1 = 0
            for itd0, t0 in enumerate(series_1[0]):
                while series_2[0][itd1] < t0 and itd1 < (len(series_2[0]) - 1):
                    itd1 += 1
                if series_2[0][itd1] == t0:
                    coupled_data[entry][its][0].append(t0)
                    coupled_data[entry][its][1].append(series_1[1][itd0])
                    coupled_data[entry][its][2].append(series_2[1][itd1])
            its += 1

# compute averages and mean, mean absolute and root mean square differences
#labels = ['raw data', 'mov avg ' + str(ma_len_0) + 's', 'mov avg '
#          + str(ma_len_1) + 's', 'mov avg ' + str(ma_len_2) + 's']
#for name in coupled_data.keys():
#    print('')
#    print(name + ':')
#    for it_label, cdat in enumerate(coupled_data[name]):
#        avg0 = 0.
#        avg1 = 0.
#        md = 0.
#        mad = 0.
#        rmsd = 0.
#        datlen = len(cdat[0])
#        for it in range(datlen):
#            avg0 += cdat[1][it]
#            avg1 += cdat[2][it]
#            diff = cdat[1][it] - cdat[2][it]
#            md += diff
#            mad += abs(diff)
#            rmsd += diff**2
#        avg0 /= datlen
#        avg1 /= datlen
#        md /= datlen
#        mad /= datlen
#        rmsd = sqrt(rmsd/datlen)
#        print(labels[it_label], (avg0, avg1), md, mad, rmsd)


for entry in coupled_data.keys():
    figure()
    title(entry)
    plot(coupled_data[entry][0][0], coupled_data[entry][0][1])
    plot(coupled_data[entry][0][0], coupled_data[entry][0][2])
    legend([sys.argv[1], sys.argv[2]])

figure()
title('Powers ' + str(ma_lens[0]) + ' Sec MA')
plot(mavgs_1['power'][0][0], mavgs_1['power'][0][1])
plot(mavgs_2['power'][0][0], mavgs_2['power'][0][1])
legend([sys.argv[1], sys.argv[2]])

figure()
title('Powers '  + str(ma_lens[1]) + ' Sec MA')
plot(mavgs_1['power'][1][0], mavgs_1['power'][1][1])
plot(mavgs_2['power'][1][0], mavgs_2['power'][1][1])
legend([sys.argv[1], sys.argv[2]])

figure()
title('Powers with Scaling, ' + str(ma_lens[1]) + ' Sec MA')
plot(mavgs_1['power'][1][0], mavgs_1['power'][1][1])
plot(mavgs_2['power'][1][0], pw_2_scaled[2])
legend([sys.argv[1], sys.argv[2]])

figure()
title('Powers with Scaling, ' + str(ma_lens[2]) + ' Sec MA')
plot(mavgs_1['power'][2][0], mavgs_1['power'][2][1])
plot(mavgs_2['power'][2][0], pw_2_scaled[3])
legend([sys.argv[1], sys.argv[2]])

show()
