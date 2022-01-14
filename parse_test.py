import sys
from parse.parse_fitfile import parse_fitfile
from pylab import *

# test

entry_dict = {'speed' : [3, 30], 'temperature' : [6], 'distance' : [], 'altitude' : [5]}

data, mov_avgs = parse_fitfile(sys.argv[1], entry_dict, True)

print(sum(data['speed'])/len(data['speed']))
print(sum(mov_avgs['speed'][0][1]/len(mov_avgs['speed'][0][1])))
print(sum(mov_avgs['speed'][1][1]/len(mov_avgs['speed'][1][1])))

print(len(data['speed']), len(mov_avgs['speed'][0][1]), len(mov_avgs['speed'][1][1]))

figure()
plot(data['timestamp'], data['speed'])

figure()
plot(data['seconds'], data['temperature'])

figure()
plot(data['seconds'], data['speed'])
plot(mov_avgs['speed'][0][0], mov_avgs['speed'][0][1], 'x')
plot(mov_avgs['speed'][1][0], mov_avgs['speed'][1][1], 'x')
legend(['1s', '3s', '30s'])

show()
