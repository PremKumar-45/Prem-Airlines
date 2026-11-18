"""Airports served by Prem Airlines: city -> (IATA code, latitude, longitude, is_hub)."""

CITIES = {
    'Delhi':           ('DEL', 28.5562, 77.1000, True),
    'Mumbai':          ('BOM', 19.0896, 72.8656, True),
    'Bengaluru':       ('BLR', 13.1986, 77.7066, True),
    'Chennai':         ('MAA', 12.9941, 80.1709, True),
    'Kolkata':         ('CCU', 22.6547, 88.4467, True),
    'Hyderabad':       ('HYD', 17.2403, 78.4294, True),
    'Pune':            ('PNQ', 18.5822, 73.9197, False),
    'Ahmedabad':       ('AMD', 23.0772, 72.6347, False),
    'Goa':             ('GOI', 15.3808, 73.8314, False),
    'Jaipur':          ('JAI', 26.8242, 75.8122, False),
    'Lucknow':         ('LKO', 26.7606, 80.8893, False),
    'Kochi':           ('COK', 10.1520, 76.4019, False),
    'Thiruvananthapuram': ('TRV', 8.4821, 76.9201, False),
    'Guwahati':        ('GAU', 26.1061, 91.5859, False),
    'Bhubaneswar':     ('BBI', 20.2444, 85.8178, False),
    'Patna':           ('PAT', 25.5913, 85.0880, False),
    'Ranchi':          ('IXR', 23.3143, 85.3217, False),
    'Srinagar':        ('SXR', 33.9871, 74.7742, False),
    'Chandigarh':      ('IXC', 30.6735, 76.7885, False),
    'Indore':          ('IDR', 22.7218, 75.8011, False),
    'Nagpur':          ('NAG', 21.0922, 79.0472, False),
    'Varanasi':        ('VNS', 25.4524, 82.8593, False),
    'Visakhapatnam':   ('VTZ', 17.7212, 83.2245, False),
    'Coimbatore':      ('CJB', 11.0300, 77.0434, False),
    'Port Blair':      ('IXZ', 11.6412, 92.7297, False),
    'Leh':             ('IXL', 34.1359, 77.5465, False),
    'Jamshedpur':      ('IXW', 22.8132, 86.1688, False),
}

CITY_NAMES = sorted(CITIES)
