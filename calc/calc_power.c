#include <math.h>
#include <stdio.h>

struct PhysVar {
    const double mass;
    const double rot_mass;
    const double crr;
    const double cda;
    const double rho;
    const double g;
    const double loss;
    const double wind_v;
    const double wind_dir;
};

double calc_direction(const double Alat, const double Along, const double Blat, const double Blong) {
    const double Alat_rad = Alat/180.*M_PI;
    const double Along_rad = Along/180.*M_PI;
    const double Blat_rad = Blat/180.*M_PI;
    const double Blong_rad = Blong/180.*M_PI;

    const double deltaL = Blong_rad - Along_rad;
    const double X = cos(Blat_rad)*sin(deltaL);
    const double Y = cos(Alat_rad)*sin(Blat_rad) - sin(Alat_rad)*cos(Blat_rad)*cos(deltaL);

    return atan2(X, Y)/M_PI*180. + 180.;
}

double calc_power(const double v_new, const double v_old, const double tdiff, const double dir, const double slope, const struct PhysVar * const phys_var) {
    const double slope_rad = atan(slope);
    const double v = 0.5*(v_new + v_old);
    const double v_wind = v - phys_var->wind_v * cos((dir - phys_var->wind_dir)/180.*M_PI);

    const double F_g = phys_var->mass * phys_var->g * sin(slope_rad);
    const double F_r = phys_var->mass * phys_var->g * fabs(cos(slope_rad)) * phys_var->crr;
    const double F_w = 0.5 * phys_var->cda * phys_var->rho * v_wind*v_wind;
    const double pow_base = (F_g + F_r + F_w) * v;

    const double diff_ekin = 0.5*phys_var->mass*(v_new*v_new - v_old*v_old);
    const double diff_erot = 0.5*phys_var->rot_mass*(v_new*v_new - v_old*v_old);
    const double pow_acc = (diff_ekin + diff_erot) / tdiff;

    return (pow_base + pow_acc) / (1. - phys_var->loss);
}

void calc_power_data(const int ndata, double * const comp_pow,
                    const double * const speed, const double * const posLat, const double * const posLong,
                    const double * const slope, const double * const tsecs,
                    const struct PhysVar phys_var, const int calc_neg_watts) {
    double v_old = 0.;
    for (int it = 0; it < ndata; it+=1) {
        const double v_new = speed[it]/3.6;
        double dir;
        double tdiff;
        //printf("Speed: %f, PosLat: %f, PosLong: %f, Slope: %f, Secs: %f", speed[it], posLat[it], posLong[it], slope[it], tsecs[it]);
        //printf("\n");

        // compute time difference
        if (it > 0) {
            tdiff = tsecs[it] - tsecs[it-1];
        }
        else {
            tdiff = 1.;
        }

        // compute smoothed direction
        if (ndata > 1 && it == ndata - 1) { // last step
            dir = calc_direction(posLat[it-1], posLong[it-1], posLat[it], posLong[it]);
        }
        else if (ndata > 1 && it > 0) { // regular step
            dir = calc_direction(posLat[it-1], posLong[it-1], posLat[it+1], posLong[it+1]);
        }
        else { // first step: just assume perfect cross wind
            dir = phys_var.wind_dir + 90.;
        }

        // compute power
        const double pow = calc_power(v_new, v_old, tdiff, dir, slope[it], &phys_var);
        if (pow > 0 || calc_neg_watts > 0) { // option to clamp power to positive values
            comp_pow[it] = pow;
        }
        else {
            comp_pow[it] = 0.;
        }
        v_old = v_new;
    }

    return;
}
