import sys
from parse.parse_fitfile import parse_fitfile
from calc.calc_cp import calc_cp_data
from pylab import *

# test critical power model calculations

cpow = 370.
wprime = 25000.
pmax = 1170.

entry_dict = {'power' : [], 'distance' : [], 'altitude' : []}
data, mov_avgs = parse_fitfile(sys.argv[1], entry_dict, False)

wp_data, mpa_data, cp_data = calc_cp_data(data, cpow, wprime, pmax, True)

figure()
plot(data['seconds'], data['power'])

figure()
plot(data['seconds'], wp_data)

figure()
plot(data['seconds'], mpa_data)
plot(data['seconds'], data['power'])
legend(["MPA", "Power"])

figure()
plot(data['seconds'], cp_data)

show()
