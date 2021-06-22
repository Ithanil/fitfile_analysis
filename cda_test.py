import sys
import fitparse

from pylab import *

# Load the FIT file
fitfile = fitparse.FitFile(sys.argv[1])

data = {}
relevant_keys = ['speed', 'power', 'distance', 'position_lat', 'position_long', 'altitude']

it = 0 # general iteration counter
tot_sec = 0 # count total seconds

# Main loop for data extraction
for record in fitfile.get_messages("record"):

    # pre-extract timestamp, distance and altitude of the record
    for entry in record:
        if entry.name == 'timestamp':
            cur_time = entry.value
        elif entry.name == 'distance':
            cur_dist = entry.value
        elif entry.name == 'altitude':
            cur_alt = entry.value

    # compute time step, distance and height step
    time_diff = 0
    d_diff = 0
    h_diff = 0
    if it > 0:
        time_diff = cur_time - last_time
        time_diff = time_diff.total_seconds()
        d_diff = cur_dist - last_dist
        h_diff = cur_alt - last_alt
    # remember timestamp and altitude
    last_time = cur_time
    last_dist = cur_dist
    last_alt = cur_alt
    # increment total seconds
    tot_sec += time_diff

    # extract all data from record
    for entry in record:
        if entry.name not in relevant_keys and entry.name != 'timestamp':
            continue # skip irrelevant entries

        # --- Pre-Processing of entry values ---

        # convert 'None' values to 0
        if entry.value == None:
            data_value = 0
        else:
            data_value = entry.value

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
        if entry.name in relevant_keys:
            if entry.name not in data.keys():
                data[entry.name] = []
            data[entry.name].append((tot_sec, data_value))

    # add slope data
    if 'slope' not in data.keys():
        data['slope'] = []
    if d_diff > 0:
        slope = h_diff/d_diff
    else:
        slope = 0
    data['slope'].append((tot_sec, slope))

    it += 1 # increase general iteration counter

print(data.keys())
print(data['slope'])

phys_var = {
    'mass' : 73+9,
    'crr'  : 0.0035,
    'cda'  : 0.23,
    'rho'  : 1.225,
    'g'    : 9.81,
    'loss' : 0.03
}

def power_calc(v, slope, phys_var):
    slope_rad = arctan(slope)/180*pi
    F_g = phys_var['mass'] * phys_var['g'] * sin(slope_rad)
    F_r = phys_var['mass'] * phys_var['g'] * cos(slope_rad) * phys_var['crr']
    F_a = 0.5 * phys_var['cda'] * phys_var['rho'] * v*v
    print(F_g, F_r, F_a)

    return (F_g + F_r + F_a) * v / (1 - phys_var['loss'])


comp_pow = []
avg_pow = 0
count = 0
for it in range(len(data['speed'])):
    pow = power_calc(data['speed'][it][1]/3.6, data['slope'][it][1], phys_var)
    comp_pow.append((data['speed'][it][0], pow))
    avg_pow += pow
    count += 1

avg_pow /= count

print(comp_pow)
print(avg_pow)