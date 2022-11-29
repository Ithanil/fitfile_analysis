from pylab import *

def mpa_test(wprime_bal, cp, wprime, pmax):
    return cp + (pmax - cp)*(-exp(wprime))

def mpa_test_2(wprime_bal, cp, pmax, tref):
    return 1./(tref/wprime_bal - 1./(cp-pmax)) + cp

def mpa_test_3(wprime_bal, cp, wprime, pmax):
    return cp + (pmax - cp)/wprime*wprime_bal

def mpa_test_4(wprime_bal, cp, wprime, pmax):
    return pmax - (pmax - cp)*((wprime - wprime_bal)/wprime)**2

cp = 362.
wprime = 25000.
pmax = 1170.

pdata_x = arange(0.1, wprime, 100.)
pdata_y_1 = array([mpa_test(wp_x, cp, wprime, pmax) for wp_x in pdata_x])
pdata_y_2 = array([mpa_test_2(wp_x, cp, pmax, 1.) for wp_x in pdata_x])
pdata_y_3 = array([mpa_test_2(wp_x, cp, pmax, 5.) for wp_x in pdata_x])
pdata_y_4 = array([mpa_test_3(wp_x, cp, wprime, pmax) for wp_x in pdata_x])
pdata_y_5 = array([mpa_test_4(wp_x, cp, wprime, pmax) for wp_x in pdata_x])

xdata_x = [25000. - (402.515-362.)*t for t in [0., 60., 120., 180., 240., 300., 360., 420., 480., 540., 600.]]
xdata_y = [1170., 1163., 1140., 1102., 1048., 980., 895., 796., 681., 551., 406.]

figure()
plot(pdata_x, pdata_y_1)
plot(pdata_x, pdata_y_2)
plot(pdata_x, pdata_y_3)
plot(pdata_x, pdata_y_4)
plot(pdata_x, pdata_y_5)
plot(xdata_x, xdata_y, '+')

ylim(0., pmax)
legend(["V1", "V2, tref = 1", "V2, tref = 5", "V3", "Xert Model", "Xert Data"])
gca().invert_xaxis()


ydata = [1170]
for ydata_old in xdata_y:
    ydata.append(ydata_old)
ydata = array(ydata)
mpadata = [(ydata[it + 1] - ydata[it])  for it in range(11)]
print(mpadata)
figure()
plot(mpadata)

alts = [0., 0.250, 0.500, 0.750, 1., 1.250, 1.500, 2.000, 2.250, 2.500]
cp_alt = [cp*(0.0016*alt**3 - 0.0157*alt**2 - 0.027*alt + 1.0025) for alt in alts]

figure()
plot(alts, cp_alt)

figure()
plot(alts, [(0.0016*alt**3 - 0.0157*alt**2 - 0.027*alt + 1.0025) for alt in alts])

show()
