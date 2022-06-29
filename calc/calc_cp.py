from numpy import array

# differential wprime balance changes
def calc_wp_diff(wp_bal, po, tdiff, cp, wp):
    if po >= cp:
        return (cp - po)*tdiff
    else:
        return (cp - po)*(wp - wp_bal)/wp*tdiff

# return new wprime balance according to differential algorithm
def update_wp_bal(wp_bal, po, tdiff, cp, wp):
    wp_bal_new = wp_bal + calc_wp_diff(wp_bal, po, tdiff, cp, wp)
    if wp_bal_new > wp:
        return wp
    if wp_bal_new < 0:
        return 0.
    return wp_bal_new

# MPA at a given WPrime balance
def calc_mpa(wp_bal, cp, wp, pm):
    mpa = pm - (pm - cp)*((wp - wp_bal)/wp)**2
    if mpa > pm: # shouldn't happen for proper wp_bal input
        return pm
    if mpa < cp: # can happen if wp isn't accurate / too low
        return cp
    return mpa

# Critical Power at altitude
# doi.org/10.3389/fphys.2017.00180
def calc_cp_alt(cp, alt):
    alt_km = alt/1000.
    return cp * (0.0016*alt_km**3 - 0.0157*alt_km**2 - 0.027*alt_km + 1.0025)


def calc_cp_data(data, cp, wp, pm, use_altitude):
    wp_data = []
    mpa_data = []
    cp_data = [] # only relevant if use_altitude

    wp_bal = wp
    ndata = len(data['power'])
    for it in range(ndata):
        po = data['power'][it]

        # compute time difference
        if it > 0:
            tdiff = data['seconds'][it] - data['seconds'][it-1]
        else:
            tdiff = 1.

        if use_altitude:
            cp_alt = calc_cp_alt(cp, data['altitude'][it])
        else:
            cp_alt = cp

        wp_bal = update_wp_bal(wp_bal, po, tdiff, cp_alt, wp)
        wp_data.append(wp_bal)
        mpa_data.append(calc_mpa(wp_bal, cp_alt, wp, pm))
        cp_data.append(cp_alt)

    return array(wp_data), array(mpa_data), array(cp_data)
