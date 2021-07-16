from pos_calc import posCalc

def set_current_loc(lat, long, altitude):
    pos_dict = {
        "latitude": lat,
        "longitude": long,
        "altitude":altitude
    }
    return pos_dict

current_loc = set_current_loc(39.20707440192549, -76.6895809536484, 6371e3)
print(f"Current location: {current_loc}")

def posCalc_impl(dis_cm, azimuth):
    lat = current_loc.get("latitude")
    long = current_loc.get("longitude")
    dict_r = posCalc(
        current_loc.get("altitude"), 
        lat,
        long,
        dis_cm, 
        azimuth
    )
    return {
        "latitude":dict_r.get("latitude"),
        "longitude": dict_r.get("longitude")
    }

def posCalc_test_example():
    dict = posCalc(6371e3, 80, -90, 100000, 200)
    lat = dict.get("latitude")
    long = dict.get("longitude")
    print("example answer should be: (79.99, 90.02)")
    print(f"returned ({lat}, {long})")

def posCalc_test_accuracy(angle, test):
    cm = posCalc_impl(1, angle)
    if (cm.get(test)!=current_loc.get(test)):
        return "can detect cm"

    cm5 = posCalc_impl(5, angle)
    if (cm.get(test)!=current_loc.get(test)):
        return "can detect 5 cm"

    cm10 = posCalc_impl(10, angle)
    if (cm10.get(test)!=current_loc.get(test)):
        return "can detect 10 cm"

    m = posCalc_impl(100, angle)
    if (m.get(test)!=current_loc.get(test)):
        return "can detect 1 m"

    m10 = posCalc_impl(1000, angle)
    if (m10.get(test)!=current_loc.get(test)):
        return "can detect 10 m"

    m100 = posCalc_impl(10000, angle)
    if (m100.get(test)!=current_loc.get(test)):
        return "can detect 100 m"

    


def test_all():
    print("test example to check for function implementation")
    posCalc_test_example()
    print(f"test longitude accuracy")
    print(posCalc_test_accuracy(180, "longitude"))
    print("test latitude accuracy")
    print(posCalc_test_accuracy(90, "latitude"))
    print(current_loc)
    print(posCalc(6371e3, 39.20707440192549, -76.6895809536484, 1000000, 90))

test_all()