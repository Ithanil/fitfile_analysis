import sys
from parse.parse_fitfile import parse_fitfile
from pylab import *

# Import HRV ramp fitfile
entry_dict = {'power' : [10, 120, 90, 30], 'heart_rate' : [1, 30, 1]}
data, mov_avgs = parse_fitfile(sys.argv[1], entry_dict, False)

# Import and sync HR/HRV data
time_offset = float(sys.argv[3])
hr_data = genfromtxt(sys.argv[2] + '_HR.csv', skip_header=2, delimiter=',')
hr_data_sec = [time_offset + data[1]/1000. for data in hr_data]
hr_data_hr = [data[2] for data in hr_data]

hrv_data = genfromtxt(sys.argv[2] + '_Features.csv', skip_header=2, delimiter=',')

hr_data_timestamp0 = hr_data[0][0]
hrv_data_timestamp0 = hrv_data[0][1]
tdiff = hrv_data_timestamp0 - hr_data_timestamp0
time_offset_hrv = time_offset + tdiff/1000.
print('Time Offset HRV: ', time_offset_hrv)

hrv_data_sec = [time_offset_hrv + (data[1] - hrv_data_timestamp0)/1000. for data in hrv_data]
hrv_data_hr = [data[2] for data in hrv_data]
hrv_data_alpha = [data[-2] for data in hrv_data]
print(hrv_data)


# Create Alpha-1 / Power data set
pwr_to_alpha = ([], [])
for hrv_index, time in enumerate(hrv_data_sec):
    time_index = where(mov_avgs['power'][1][0] == int(time))[0][0]
    pwr_to_alpha[0].append(mov_avgs['power'][1][1][time_index])
    pwr_to_alpha[1].append(hrv_data_alpha[hrv_index])

# Create linear fit for pwr:alpha
lin_fit_start = int(sys.argv[4])
lin_fit_end = int(sys.argv[5])
pwr_to_alpha = (pwr_to_alpha[0][0:lin_fit_end], pwr_to_alpha[1][0:lin_fit_end])
x_pwr = array(pwr_to_alpha[0][lin_fit_start:])
y_pwr = array(pwr_to_alpha[1][lin_fit_start:])
A_pwr = vstack([x_pwr, ones(len(x_pwr))]).T
m_pwr, c_pwr = linalg.lstsq(A_pwr, y_pwr, rcond=None)[0]
print('PWR:Alpha m: ', m_pwr, ' PWR:Alpha c: ', c_pwr)
print('AeT Power: ', (0.75 - c_pwr)/m_pwr)
print('AnT Power: ', (0.5 - c_pwr)/m_pwr)
print()


# Create Alpha-1 / HR data set
hr_to_alpha = ([], [])
for hrv_index, time in enumerate(hrv_data_sec):
    time_index = where(mov_avgs['heart_rate'][1][0] == int(time))[0][0]
    hr_to_alpha[0].append(mov_avgs['heart_rate'][1][1][time_index])
    hr_to_alpha[1].append(hrv_data_alpha[hrv_index])

# Create linear fit for hr:alpha
lin_fit_start = int(sys.argv[4])
lin_fit_end = int(sys.argv[5])
hr_to_alpha = (hr_to_alpha[0][0:lin_fit_end], hr_to_alpha[1][0:lin_fit_end])
x_hr = array(hr_to_alpha[0][lin_fit_start:])
y_hr = array(hr_to_alpha[1][lin_fit_start:])
A_hr = vstack([x_hr, ones(len(x_hr))]).T
m_hr, c_hr = linalg.lstsq(A_hr, y_hr, rcond=None)[0]
print('HR:Alpha m: ', m_hr, ' HR:Alpha c: ', c_hr)
print('AeT HR (unreliable): ', (0.75 - c_hr)/m_hr)
print('AnT HR (unreliable): ', (0.5 - c_hr)/m_hr)
print()


# Create HR / Power data set
pwr_to_hr = ([], [])
for index, pwr in enumerate(mov_avgs['power'][3][1]):
    time = mov_avgs['power'][3][0][index]
    if time > hrv_data_sec[lin_fit_start] and time < hrv_data_sec[lin_fit_end - 1]:
        pwr_to_hr[0].append(pwr)
        hr_index = where(mov_avgs['heart_rate'][2][0] == int(time))[0][0]
        pwr_to_hr[1].append(mov_avgs['heart_rate'][2][1][hr_index])


figure()
plot(hr_data_sec, hr_data_hr)
plot(data['seconds'], data['heart_rate'])
#plot(hrv_data_sec, hrv_data_hr, 'x')
#plot(mov_avgs['heart_rate'][1][0], mov_avgs['heart_rate'][1][1], '-')


figure()
plot(pwr_to_alpha[0], pwr_to_alpha[1], 'o')
plot(x_pwr, m_pwr*x_pwr + c_pwr)
plot([pwr_to_alpha[0][0], pwr_to_alpha[0][-1]], [0.75, 0.75], '--', color = 'black')
plot([pwr_to_alpha[0][0], pwr_to_alpha[0][-1]], [0.5, 0.5], '-.', color = 'black')
xlabel('Power (2min-Avg) [W]')
ylabel('HRV Alpha-1')
title('HRV Ramp: Alpha-1 vs. Power')


figure()
plot(hr_to_alpha[0], hr_to_alpha[1], 'o')
plot(x_hr, m_hr*x_hr + c_hr)
plot([hr_to_alpha[0][0], hr_to_alpha[0][-1]], [0.75, 0.75], '--', color = 'black')
plot([hr_to_alpha[0][0], hr_to_alpha[0][-1]], [0.5, 0.5], '-.', color = 'black')
xlabel('HR (2min-Avg) [bpm]')
ylabel('HRV Alpha-1')
title('HRV Ramp: Alpha-1 vs. HR')


figure()
plot(pwr_to_hr[0], pwr_to_hr[1], 'x')

figure()
plot(pwr_to_hr[1], pwr_to_hr[0], 'x')

fig = plt.figure()
host = fig.add_subplot(111)
    
par = host.twinx()
    
host.set_xlim(300, 3100)
host.set_ylim(170, 400)
par.set_ylim(90, 180)
    
host.set_xlabel("Time [s]")
host.set_ylabel("Power [W]")
par.set_ylabel("Heart Rate [bpm]")

color1 = 'purple'
color2 = 'blue'
color3 = 'red'

p1, = host.plot(mov_avgs['power'][0][0], mov_avgs['power'][0][1], '-', color=color1, label="Power (10s Average)")
p2, = host.plot(mov_avgs['power'][2][0], mov_avgs['power'][2][1], '-', color=color2, label="Power (90s Average)")
p3, = par.plot(mov_avgs['heart_rate'][0][0], mov_avgs['heart_rate'][0][1], '-', color=color3, label="Heart Rate")

lns = [p1, p2, p3]
host.legend(handles=lns, loc='best')

host.yaxis.label.set_color(p1.get_color())
par.yaxis.label.set_color(p3.get_color())
host.set_title('HRV ramp: HR and power')


show()
