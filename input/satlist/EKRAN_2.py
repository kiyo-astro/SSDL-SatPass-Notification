#--------------------------------------------------------------------------------------------------#
# QHY294PROM.py                                                                                    #
# Developed by Kiyoaki Okudaira * University of Washington / Kyushu University / IAU CPS SatHub    #
#--------------------------------------------------------------------------------------------------#
# Description                                                                                      #
#--------------------------------------------------------------------------------------------------#
# Satellites list                                                                                  #
# EKRAN 2 spacecraft and debris                                                                    #
#--------------------------------------------------------------------------------------------------#
# History                                                                                          #
#--------------------------------------------------------------------------------------------------#
# coding 2025.12.08: 1st coding                                                                    #
#--------------------------------------------------------------------------------------------------#
norad_ids = [
    10365,  # EKRAN 2
    11581,  # EKRAN 2 DEB 1977-092H
    12996,  # EKRAN 2 DEB 1977-092J
    29014,  # EKRAN 2 DEB 1977-092K
    33519,  # EKRAN 2 DEB 1977-092L
    59986,  # EKRAN 2 DEB 1977-092M
    59987,  # EKRAN 2 DEB 1977-092N
    59988   # EKRAN 2 DEB 1977-092P
]

ftitle = "EKRAN_2"    # Satellites list title for file name | str
legend_view = "INTLDES" # "INTLDES" or "OBJNAME", for plot | str
az_min = 90             # Default azimuth min for plot | int
az_max = 270            # Default azimuth max for plot | int
az_interval = 30        # Default azimuth interval for plot | int