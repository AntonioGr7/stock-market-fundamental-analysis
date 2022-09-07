import math


def discount(cf, discount_rate, begin_year, actual_year):
    dcf = cf * ((1 + discount_rate) ** (begin_year - actual_year - 1))
    return dcf

def data_growth(data):
    base = data[0]
    growths = []
    for i,d in enumerate(data):
        if math.isnan(base):
            growths.append(math.nan)
            base=d
        else:
            delta = d-base
            if base!=0:
                if base < d:
                    growth_rate = (abs(delta)/abs(base))*100
                else:
                    growth_rate = -(abs(delta) / abs(base)) * 100
            else:
                growth_rate = 0
            growths.append(growth_rate)
            base = d
    return growths

def to_float(in_data):
    if isinstance(in_data, str):
        if "," in in_data:
            in_data = in_data.replace(",", ".")
        elif "." in in_data:
            in_data = float(in_data)
            in_data = float_convertion(in_data)
        else:
            in_data = float(in_data)
            in_data = float_convertion(in_data)
    elif (isinstance(in_data, float)):
        in_data = float_convertion(in_data)
    return float(in_data)

def float_convertion(in_data):
    if math.isnan(in_data):
        return in_data
    in_data = math.ceil(in_data)
    if in_data > 0:
        digits = int(math.log10(in_data)) + 1
        negative = False
    elif in_data == 0:
        digits = 1
        negative = False
    else:
        digits = int(math.log10(-in_data)) + 1
        negative = True
    if digits <= 3:
        if not negative:
            in_data = in_data / 1000
            # in_data = str("0."+str(in_data))
        else:
            in_data = abs(in_data)
            in_data = - in_data / 1000
    return in_data