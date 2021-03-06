#include <math.h>
#include <stdio.h>

int calc_pdiff(const int ndata, double * const cost,
               const double * const data_pow, const double * const data_v,
               const double * const comp_pow, const int no_filter) {
    *cost = 0.;
    int np = 0;
    for (int it = 1; it < ndata; it+=1) {
        //printf("Dat_P %f, Dat_V %f, Comp_P %f", data_pow[it], data_v[it], comp_pow[it]);
        //printf("\n");
        if ((data_pow[it] > 0. && data_v[it] > 20. && fabs(data_v[it] - data_v[it-1]) < 2.0) || no_filter > 0) {
            const double pd = comp_pow[it] - data_pow[it];
            *cost += pd + pd*pd;
            np += 1;
        }
    }

    *cost = fabs(*cost);
    return np;
}
