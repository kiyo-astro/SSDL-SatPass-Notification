#--------------------------------------------------------------------------------------------------#
# QHY294PROM.py                                                                                    #
# Developed by Kiyoaki Okudaira * University of Washington / Kyushu University / IAU CPS SatHub    #
#--------------------------------------------------------------------------------------------------#
# Description                                                                                      #
#--------------------------------------------------------------------------------------------------#
# Satellites list                                                                                  #
# Bright LEO satellites                                                                            #
#--------------------------------------------------------------------------------------------------#
# History                                                                                          #
#--------------------------------------------------------------------------------------------------#
# coding 2025.12.08: 1st coding                                                                    #
#--------------------------------------------------------------------------------------------------#
norad_ids = [
    20580,  # HST
    25544,  # ISS
    27386,  # ENVISAT
    48274,  # CSS
    53807,  # BLUEWALKER 3
    59588,  # ACS 3 SOLAR SAIL
    60235,  # OBJECT A
    67073,  # RAISE-4
    61047,  # SPACEMOBILE-001
    61048,  # SPACEMOBILE-002
    61045,  # SPACEMOBILE-003
    61049,  # SPACEMOBILE-004
    61046,  # SPACEMOBILE-005
    67232   # SPACEMOBILE-006
]

ftitle = "BRIGHT_LEO"   # Satellites list title for file name | str
legend_view = "OBJNAME" # "INTLDES" or "OBJNAME", for plot | str
az_min = 0              # Default azimuth min for plot | int
az_max = 360            # Default azimuth max for plot | int
az_interval = 30        # Default azimuth interval for plot | int