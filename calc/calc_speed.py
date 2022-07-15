from pylab import *
from calc.calc_power import calc_direction

def calc_speed(pow, v_old, tdiff, dir, slope, phys_var, verbosity = 0):
    slope_rad = arctan(slope)
    v_wind = v_old - phys_var['wind_v'] * cos((dir - phys_var['wind_dir']) / 180. * pi)

    F_g = phys_var['mass'] * phys_var['g'] * sin(slope_rad)
    F_r = phys_var['mass'] * phys_var['g'] * cos(slope_rad) * phys_var['crr']
    F_w = 0.5 * phys_var['cda'] * phys_var['rho'] * v_wind*v_wind
    pow_base = (F_g + F_r + F_w) * v_old

    pow_diff = pow*(1 - phys_var['loss']) - pow_base
    vnew_sq = 2.*pow_diff*tdiff/(phys_var['mass'] + phys_var['rot_mass']) + v_old**2
    if (vnew_sq > 0):
        v_new = sqrt(vnew_sq)
    else:
        v_new = 0.
    ekin_new = 0.5*phys_var['mass']*v_new**2
    erot_new = 0.5*phys_var['rot_mass']*v_new**2

    if verbosity > 1:
        print('Forces g/r/w: ', F_g, F_r, F_w)
        print('Powers g/r/w/a (lossless): ', F_g*v, F_r*v, F_w*v, (ekin_new + erot_new - 0.5*(phys_var['mass'] + phys_var['rot_mass'])*v_old**2)/tdiff)
        print('V_old, V_new: ', v_old, v_new)
        print('Ekin_new: ', ekin_new, ' Erot_new: ', erot_new)

    return v_new

def calc_speed_static(pow, dir, slope, phys_var, verbosity = 0):
    slope_rad = arctan(slope)

    F_g = phys_var['mass'] * phys_var['g'] * sin(slope_rad)
    F_r = phys_var['mass'] * phys_var['g'] * cos(slope_rad) * phys_var['crr']

    # Equation: pow*(1. - phys_var['loss']) = (F_g + F_r + F_w) * v
    # with F_w = 0.5 * phys_var['cda'] * phys_var['rho'] * v_wind*v_wind
    # and v_wind = v - phys_var['wind_v'] * cos((dir - phys_var['wind_dir']) / 180. * pi)
    # translates to:
    # 0 == (F_g + F_r)*v + v * 0.5 * phys_var['cda'] * phys_var['rho'] * (v - phys_var['wind_v'] * cos((dir - phys_var['wind_dir']) / 180. * pi))**2 - pow*(1 - phys_var['loss'])
    # which is equation of form 0 == A*v + v*B*(v-C)^2 - D
    #
    # Solution according to WolframAlpha:
    A = F_g + F_r
    B = 0.5 * phys_var['cda'] * phys_var['rho']
    C = phys_var['wind_v'] * cos((dir - phys_var['wind_dir']) / 180. * pi)
    D = pow*(1. - phys_var['loss'])

    v = -(18 * A * B**2 * C + sqrt(4. * (3. * A * B - B**2 * C**2)**3 + (18. * A * B**2 * C + 2. * B**3 * C**3 - 27. * B**2 * D)**2) + 2. * B**3 * C**3 - 27. * B**2 * D)**(1./3.)/(3. * 2.**(1./3.) * B) +\
        (2.**(1./3.) * (3. * A  * B - B**2 * C**2))/(3. * B * (18. * A * B**2 * C + sqrt(4. * (3. * A * B - B**2 * C**2)**3 + (18. * A * B**2 * C + 2. * B**3 * C**3 - 27. * B**2 * D)**2) + 2. * B**3 * C**3 - 27. * B**2 * D)**(1./3.)) + (2. * C)/3.


    return v

# WIP, no gpx parsing for course data yet
#def calc_speed_data(data, initial_speed, phys_var, verbosity = 0):
# Data needs to contain the GPS points of the course, associated altitude and power values
#
#Physical parameter dictionary example:
#phys_var = {
#    'mass'     : 73+9,
#    'crr'      : 0.004,
#    'cda'      : 0.215,
#    'rho'      : 1.225,
#    'g'        : 9.81,
#    'loss'     : 0.025,
#    'wind_v'   : 1.,
#    'wind_dir' : -70.
#}
#
#        # compute smoothed direction
#        if it == ndata - 1: # last step
#            dir = calc_direction(data['position_lat'][it-1], data['position_long'][it-1], data['position_lat'][it], data['position_long'][it])
#        elif it > 0: # regular step
#            dir = calc_direction(data['position_lat'][it-1], data['position_long'][it-1], data['position_lat'][it+1], data['position_long'][it+1])
#        else: # first step: assume perfect cross wind
#            dir = phys_var['wind_dir'] + 90.
#
#        # compute smoothed slope
#        smooth_slope = 0.
#        if not use_zero_slope:
#            if it == ndata - 1: # last step
#                smooth_slope = 0.5*(data['slope'][it-1] + data['slope'][it])
#            elif it > 0: # regular step
#                smooth_slope = 0.333333333*(data['slope'][it-1] + data['slope'][it] + data['slope'][it+1])
#            else: # first step
#                smooth_slope = 0.5*(data['slope'][it] + data['slope'][it+1])
#
#        # compute speed
#
#
#    return array(speed)

