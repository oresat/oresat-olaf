#!/usr/bin/env python3

from oresat_od_db.oresat0_5 import C3_OD, OD_DB
from olaf import olaf_setup, olaf_run

if __name__ == '__main__':
    # olaf_setup(GPS_OD)
    olaf_setup(C3_OD, OD_DB)
    olaf_run()
