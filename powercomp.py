import sys
from parse.parse_fitfile import parse_fitfile
from pylab import *

# settings
ma_lens = [10, 30, 90]
entry_dict = {'speed' : ma_lens, 'power' : ma_lens, 'heart_rate' : ma_lens, 'cadence' : ma_lens, 'left_right_balance' : ma_lens}

# Load the FIT files
fitfiles = [fitparse.FitFile(sys.argv[1]), fitparse.FitFile(sys.argv[2])]

# Parse the FIT files
data_1, mov_avgs_1 = parse_fitfile(sys.argv[1], entry_dict, False)
data_2, mov_avgs_2 = parse_fitfile(sys.argv[2], entry_dict, False)

# create scaled power array for second file
if len(sys.argv) >= 4:
    scaling_fac = float(sys.argv[3])
else:
    scaling_fac = 1.0
pw_1_scaled = scaling_fac*array(mov_avgs_2['power'][0][1], mov_avgs_2['power'][1][1], mov_avgs_2['power'][2][1])

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
