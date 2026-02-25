#--------------------------------------------------------------------------------------------------#
# KUPT.py                                                                                          #
# Developed by Kiyoaki Okudaira * University of Washington / Kyushu University / IAU CPS SatHub    #
#--------------------------------------------------------------------------------------------------#
# Description                                                                                      #
#--------------------------------------------------------------------------------------------------#
# Observatory config file for obs_satorbit                                                         #
# Kyushu University Pegasus Telescope                                                              #
#--------------------------------------------------------------------------------------------------#
# History                                                                                          #
#--------------------------------------------------------------------------------------------------#
# coding 2025.12.07: 1st coding                                                                    #
#--------------------------------------------------------------------------------------------------#
obs_name = "Kyushu University Pegasus Telescope" # Observatory name | str
obs_id   = "KUPT"                                # Pbservatory ID   | str
telescope_name = "MEADE LX200-40ACF"             # Telescope name   | str
telescope_id   = ""                              # Telescope ID     | str

obs_timezone = "Asia/Tokyo"

obs_gd_lon_deg = 130.0 + (12.0 + 42.0 / 60.0) / 60.0 # Geodetic longitude [deg] | float
obs_gd_lat_deg = 33.0 + (35.0 + 56.0 / 60.0) / 60.0  # Geodetic latitude  [deg] | float
obs_gd_height  = 0.073  # Geodetic height [km] | float

obs_el_min   = 10       # Observation elevation min [deg] | int or float
wavelength_m = 0.5e-6   # Wavelength [m] | float
aperture_m   = 508.0e-3 # Aperture   [m] | float

fits_primary_hdu = None
fits_ccd_hdu = 0

obs_params = [obs_gd_lon_deg,obs_gd_lat_deg,obs_gd_height,wavelength_m,aperture_m,obs_el_min]