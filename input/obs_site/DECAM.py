#--------------------------------------------------------------------------------------------------#
# DECAM.py                                                                                         #
# Developed by Kiyoaki Okudaira * University of Washington / Kyushu University / IAU CPS SatHub    #
#--------------------------------------------------------------------------------------------------#
# Description                                                                                      #
#--------------------------------------------------------------------------------------------------#
# Observatory config file for obs_satorbit                                                         #
# DECam                                                                                            #
#--------------------------------------------------------------------------------------------------#
# History                                                                                          #
#--------------------------------------------------------------------------------------------------#
# coding 2025.12.10: 1st coding                                                                    #
#--------------------------------------------------------------------------------------------------#
obs_name = "DECam" # Observatory name | str
obs_id   = "DECAM"                                # Pbservatory ID   | str
telescope_name = ""                    # Telescope name   | str
telescope_id   = ""                              # Telescope ID     | str

obs_timezone = "Chile/Continental"

obs_gd_lon_deg = -70.814890 # Geodetic longitude [deg] | float
obs_gd_lat_deg = -30.165278  # Geodetic latitude  [deg] | float
obs_gd_height  = 2.215  # Geodetic height [km] | float

obs_el_min   = 0        # Observation elevation min [deg] | int or float
wavelength_m = 0.5e-6   # Wavelength [m] | float
aperture_m   = 508.0e-3 # Aperture   [m] | float

fits_primary_hdu = 0
fits_ccd_hdu = 1

obs_params = [obs_gd_lon_deg,obs_gd_lat_deg,obs_gd_height,wavelength_m,aperture_m,obs_el_min]