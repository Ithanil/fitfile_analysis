import sys
from parse.parse_fitfile import parse_fitfile
from calc.calc_cp import calc_cp_data
from pylab import *

# test critical power model calculations

cpow = 364.
wprime = 25000.
pmax = 1170.

entry_dict = {'power' : [], 'distance' : [], 'altitude' : []}
data, mov_avgs = parse_fitfile(sys.argv[1], entry_dict, False)

wp_data, mpa_data, cp_data = calc_cp_data(data, cpow, wprime, pmax, False)
wp_data_alt, mpa_data_alt, cp_data_alt = calc_cp_data(data, cpow, wprime, pmax, True)

for it in range(len(wp_data)): # convert to kJ
    wp_data[it] /= 1000.
    wp_data_alt[it] /= 1000.

figure()
plot(data['seconds'], data['power'])
xlabel("Time [s]")
ylabel("Power [W]")

figure()
plot(data['seconds'], wp_data)
plot(data['seconds'], wp_data_alt)
xlabel("Time [s]")
ylabel("W'bal [kJ]")
legend(["W'bal", "W'bal (alt)"])

figure()
plot(data['seconds'], mpa_data)
plot(data['seconds'], mpa_data_alt)
plot(data['seconds'], data['power'])
xlabel("Time [s]")
ylabel("Power [W]")
legend(["MPA", "MPA (alt)", "Power"])

figure()
plot(data['seconds'], cp_data_alt)
xlabel("Time [s]")
ylabel("CP [W]")

show()
