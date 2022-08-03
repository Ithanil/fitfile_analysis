import sys
from parse.parse_fitfile import parse_fitfile
from parse.filter_data import filter_data
from pylab import *

# test

entry_dict = {'speed' : [3, 30], 'temperature' : [6], 'distance' : [], 'altitude' : [5], 'power' : [3]}

data, mov_avgs = parse_fitfile(sys.argv[1], entry_dict, False)
data_filt = filter_data(data, {'altitude' : (5, 1), 'speed' : (10, 1), 'power' : (3, 1)})

figure()
plot(data['seconds'], data['speed'])
plot(data['seconds'], data_filt['speed'])

figure()
plot(data['seconds'], data['power'])
plot(mov_avgs['power'][0][0], mov_avgs['power'][0][1])
plot(data['seconds'], data_filt['power'])
legend(['raw', 'mavg', 'filt'])

figure()
plot(data['seconds'], data['altitude'])
plot(mov_avgs['altitude'][0][0], mov_avgs['altitude'][0][1])
plot(data['seconds'], data_filt['altitude'])
legend(['raw', 'mavg', 'filt'])

show()
