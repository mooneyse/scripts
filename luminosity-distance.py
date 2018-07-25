def integral(z): # http://www.astro.ucla.edu/~wright/CosmoCalc.html
    Omega_m = 0.74
    Omega_Lambda = 1 - Omega_m
    return 1 / np.sqrt(Omega_Lambda + Omega_m * (1 + z) ** 3)

if __name__ == "__main__":

    d = []
    z1s = get_data(0, 'luminosity.txt')

    h = 0.71
    H0 = 100 * h

    for z in z1s:
        d_M = ((constant.c / 1000) / H0) * integrate.quad(integral, 0, z) # https://en.wikipedia.org/wiki/Luminosity#Radio_luminosity
        d_L = (1 + z) * d_M[0]                                            # https://en.wikipedia.org/wiki/Luminosity_distance
        d_m = 1e6 * 3.0857e16 * d_L                                       # convert to metres
        d.append(d_m)
