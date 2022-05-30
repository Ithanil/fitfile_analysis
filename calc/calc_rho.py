from numpy import exp

def calc_rho_dry(temp, pres):
# Units: temp in °C, pres in hPa
    T_K = temp + 273.15
    p_Pa = pres * 100.

    return p_Pa / (287.0500676*T_K)

def calc_rho_humid(temp, pres, rhum):
# Units: temp in °C, pres in hPa, rhum in %
    T_K = temp + 273.15
    p_Pa = pres * 100.
    h_rel = rhum / 100.

    psat = 610.78 * exp(17.27*temp / (temp + 237.3))
    pv = h_rel * psat
    pd = p_Pa - pv

    return pd/(287.058*T_K) + pv/(461.495*T_K)