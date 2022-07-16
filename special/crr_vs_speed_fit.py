from pylab import *
from scipy.optimize import curve_fit

# BRR tested CRR increase with speed (when assuming linear rolling resistance formula):
# https://www.bicyclerollingresistance.com/specials/crr-speed-test
# Here I try to find a model fit which could be implemented into my speed/power formulae.

# Data

speeds = array([4., 6., 8., 10.]) # m/s
crr_corsa_speed = array([0.0021, 0.0022, 0.00233, 0.00234])
crr_gp5kstr = array([0.00287, 0.00288, 0.00299, 0.00306])
crr_power_road_tlr = array([0.00326, 0.00345, 0.0036, 0.00368])
crr_corsa = array([0.00392, 0.00415, 0.00437, 0.00444])
crr_pro_one_vg = array([0.00405, 0.00425, 0.00438, 0.00444])
crr_gp_urban = array([0.00456, 0.00478, 0.00502, 0.00522])

data = [crr_corsa_speed, crr_gp5kstr, crr_power_road_tlr, crr_corsa, crr_pro_one_vg, crr_gp_urban]
data_normalized = []
for set in data:
    set_normalized = []
    for crr in set:
        set_normalized.append(crr/set[2])
    data_normalized.append(array(set_normalized))

fit_data_x = []
fit_data_y = []
for set in data_normalized:
    for it, v in enumerate(speeds):
        fit_data_x.append(v)
        fit_data_y.append(set[it])

def crr_model(v, a, b, s):
    return s*(1. + a*(1. - exp(-b * v)))

popt, pcov = curve_fit(crr_model, fit_data_x, fit_data_y, [0.4, 0.15, 0.75])
print(popt)

a, b, s = popt
#b = 0.2
#s = 0.9
model_pdata_x = array([0., 2., 4., 6., 8., 10., 12., 14.])
model_pdata_y = []
for v in model_pdata_x:
    model_pdata_y.append(crr_model(v, a, b, s))
model_pdata_y = array(model_pdata_y)

figure()
plot(model_pdata_x, model_pdata_y)
for set in data_normalized:
    plot(speeds, set)

show()
