#--------------------------------------------------------------------------------------------------#
# QHY294PROM.py                                                                                    #
# Developed by Kiyoaki Okudaira * University of Washington / Kyushu University / IAU CPS SatHub    #
#--------------------------------------------------------------------------------------------------#
# Description                                                                                      #
#--------------------------------------------------------------------------------------------------#
# Satellites list                                                                                  #
# EKRAN series spacecraft                                                                          #
#--------------------------------------------------------------------------------------------------#
# History                                                                                          #
#--------------------------------------------------------------------------------------------------#
# coding 2025.12.08: 1st coding                                                                    #
#--------------------------------------------------------------------------------------------------#
norad_ids = [
    9503,   # EKRAN 1
    10365,  # EKRAN 2
    11273,  # EKRAN 3
    11561,  # EKRAN 4
    11890,  # EKRAN 5
    12120,  # EKRAN 6
    12564,  # EKRAN 7
    13056,  # EKRAN 8
    13554,  # EKRAN 9
    13878,  # EKRAN 10
    14377,  # EKRAN 11
    14821,  # EKRAN 12
    15219,  # EKRAN 13
    15626,  # EKRAN 14
    16729,  # EKRAN 15
    18328,  # EKRAN 16
    18715,  # EKRAN 17
    19090,  # EKRAN 18
    19683,  # EKRAN 19
    22210,  # EKRAN 20
    26736,  # EKRAN 21
]

ftitle = "EKRAN"    # Satellites list title for file name | str
legend_view = "OBJNAME" # "INTLDES" or "OBJNAME", for plot | str
az_min = 90             # Default azimuth min for plot | int
az_max = 270            # Default azimuth max for plot | int
az_interval = 30        # Default azimuth interval for plot | int