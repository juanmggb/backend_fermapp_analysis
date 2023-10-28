def monod_model(t, y, mu, Y, Yp, Ks):
    X, S, P = y

    dXdt = mu * X * S / (Ks + S)
    dSdt = -1 / Y * dXdt
    dPdt = Yp * dXdt
    return [dXdt, dSdt, dPdt]


def inhibition_model(t, y, mu, Y, Yp, Ks, Ki):
    X, S, P = y

    dXdt = mu * X * S / (Ks + S + Ki * S**2)
    dSdt = -1 / Y * dXdt
    dPdt = Yp * dXdt
    return [dXdt, dSdt, dPdt]
