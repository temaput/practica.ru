#set encoding=utf-8

from decimal import Decimal
from collections import namedtuple
D = lambda _float: Decimal(str(_float))
ZonesTuple = namedtuple("ZonesTuple", "zone1, zone2, zone3, zone4, zone5")
class ZonesTupleWrapper(object):
    def __init__(self, ztuple):
        self.data = ZonesTuple(*(D(price) for price in ztuple))
    def __getitem__(self, index):
        return self.data[index - 1]
    def __getattr__(self, attr):
        return getattr(self.data, attr)
    def __repr__(self):
        return self.data.__repr__()

zonestuple = lambda *ztuple: ZonesTupleWrapper(ztuple)


TARIFCALC_TARIF = dict(
    # бандероль
    letterpacket = dict(
        name = u'Бандероль',
        main_charge = zonestuple(82.60, 88.50, 94.40, 100.3, 118.00),
        extra_charge = zonestuple(82.60, 88.50, 94.40, 100.3, 118.00),
        extrastep_threshold = D(500),
        maximum_threshold = D(2000),
        airmail_charge = D(100.30),
        airmail_reloading_charge = D(26.79),
        # плата за ценность (4 коп за рубль)
        insurance_rate = D(0.04)


    ),
    # посылка
    parcel = dict(
        name = u'Посылка',
        main_charge = zonestuple(150.00, 185.00, 193.00, 233.00, 261.00),
        extra_charge = zonestuple(16.0, 19.0, 26.0, 39.0, 44.0),
        heavyweight_rate = D(1.3),
        oversized_rate = D(1.3),
        airmail_charge = D(275.1),
        airmail_heavyweight_charge = D(82.6),
        airmail_oversized_charge = D(82.6),
        insurance_rate = D(0.04),
        extrastep_threshold = D(500),
        heavy_threshold = D(10000),
        maximum_threshold = D(20000)
        )
    )
