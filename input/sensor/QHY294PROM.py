#--------------------------------------------------------------------------------------------------#
# QHY294PROM.py                                                                                    #
# Developed by Kiyoaki Okudaira * University of Washington / Kyushu University / IAU CPS SatHub    #
#--------------------------------------------------------------------------------------------------#
# Description                                                                                      #
#--------------------------------------------------------------------------------------------------#
# CCD config file for QHY294PROM                                                                   #
# Kyushu University Pegasus Telescope                                                              #
#--------------------------------------------------------------------------------------------------#
# History                                                                                          #
#--------------------------------------------------------------------------------------------------#
# coding 2025.12.08: 1st coding                                                                    #
#--------------------------------------------------------------------------------------------------#
ccd_name = "QHY294PROM" # CCD Name for telescope control app | str
ccd_resolution_1 = 4164 # CCD Resolution of axis 1 | int
ccd_resolution_2 = 2822 # CCD Resolution of axis 2 | int
ccd_cooler = -10        # CCD temperature setting  | int or None

ccd_ps_exp = 2          # CCD exposure at plate solve | int or float
ccd_ps_binning = 1      # CCD binning at plate solve  | int
ccd_ps_gain = 1860      # CCD gain at plate solve     | int