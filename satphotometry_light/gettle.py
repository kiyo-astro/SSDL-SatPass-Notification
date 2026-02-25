#--------------------------------------------------------------------------------------------------#
# gettle.py                                                                                        #
# Developed by Kiyoaki Okudaira * University of Washington / Kyushu University / IAU CPS SatHub    #
#--------------------------------------------------------------------------------------------------#
# Description                                                                                      #
#--------------------------------------------------------------------------------------------------#
# Retrieve Two-Line Element set from space-track.org or celestrak.org                              #
#--------------------------------------------------------------------------------------------------#
# History                                                                                          #
#--------------------------------------------------------------------------------------------------#
# copied 2025.12.07: from astroKUBO_lib                                                            #
# update 2026.01.27: get_past_TLE function added                                                   #
#--------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------#
# Libraries                                                                                        #
#--------------------------------------------------------------------------------------------------#
import requests
from datetime import datetime, timedelta
from urllib.parse import quote

#--------------------------------------------------------------------------------------------------#
# Main                                                                                             #
#--------------------------------------------------------------------------------------------------#
class space_track:
    def get_latest_TLE(
            norad_id: int | str,
            user_id: str,
            password: str
            ):
        """
        Get latest Two-Line Element set from space-track.org

        Parameters
        ----------
        norad_id: `int` or `str`
            NORAD catalog number
        user_id: `str`
            space-track.org user id
        password: `str`
            space-track.org password

        Returns
        -------
        response.status_code: `int`
            status code of query
        tle_result: `str`
            Two-Line Element set

        Notes
        -----
            (c) 2025 Kiyoaki Okudaira - Kyushu University Hanada Lab (SSDL) / IAU CPS SatHub
        """
        # Start Session
        session = requests.Session()

        # Log in
        login_url = 'https://www.space-track.org/ajaxauth/login'
        login_payload = {
            'identity': user_id,
            'password': password
        }

        response = session.post(login_url, data=login_payload)
        if response.status_code != 200:
            tle_result = None
        
        else:
            # Get TLE data
            query_url = (
                "https://www.space-track.org/basicspacedata/query/class/gp/"
                "NORAD_CAT_ID/{0}/"
                "orderby/TLE_LINE1%20ASC/format/3le".format(norad_id)
            )

            response = session.get(query_url, stream=True)
            tle_result = response.text

        return response.status_code,tle_result
    
    def get_past_TLE(
            date: str,
            range: int,
            norad_id: int | str,
            user_id: str,
            password: str,
            nearest: bool = True
            ):
        """
        Get past Two-Line Element set from space-track.org

        Parameters
        ----------
        date: `str`
            date to search TLE [YYYY-MM-DD]
        range: `int`
            TLE search range [day]
        norad_id: `int` or `str`
            NORAD catalog number
        user_id: `str`
            space-track.org user id
        password: `str`
            space-track.org password
        nearest: `bool`
            return only nearest TLE. Default is True

        Returns
        -------
        response.status_code: `int`
            status code of query
        tle_result: `str`
            Two-Line Element set

        Notes
        -----
            (c) 2025 Kiyoaki Okudaira - Kyushu University Hanada Lab (SSDL) / IAU CPS SatHub
        """
        center_date = datetime.strptime(date, "%Y-%m-%d").date()
        start_date = center_date - timedelta(days=range)
        if nearest:
            end_date   = center_date
        else:
            end_date   = center_date + timedelta(days=range)

        start_str = start_date.strftime("%Y-%m-%d")
        end_str   = end_date.strftime("%Y-%m-%d")

        # Start Session
        session = requests.Session()

        # Log in
        login_url = 'https://www.space-track.org/ajaxauth/login'
        login_payload = {
            'identity': user_id,
            'password': password
        }

        response = session.post(login_url, data=login_payload)
        if response.status_code != 200:
            tle_result = None
        else:
            query_url = (
                "https://www.space-track.org"
                "/basicspacedata/query/"
                "class/gp_history/"
                f"NORAD_CAT_ID/{norad_id}/"
                f"EPOCH/{start_str}--{end_str}/"
                "orderby/EPOCH/"
                "format/3le"
            )

            response = session.get(query_url, stream=True)
            if nearest:
                tle_result_list = response.text.splitlines()[-3:]
                tle_result = tle_result_list[0] + "\r\n" + tle_result_list[1] + "\r\n" + tle_result_list[2]
            else:
                tle_result = response.text

        return response.status_code,tle_result
    
    def get_past_TLEs(
            date: str,
            range: int,
            user_id: str,
            password: str
            ):
        """
        Get past Two-Line Element set of all objects from space-track.org

        Parameters
        ----------
        date: `str`
            date to search TLE [YYYY-MM-DD]
        range: `int`
            TLE search range [day]
        user_id: `str`
            space-track.org user id
        password: `str`
            space-track.org password

        Returns
        -------
        response.status_code: `int`
            status code of query
        tle_result: `str`
            Two-Line Element set

        Notes
        -----
            (c) 2025 Kiyoaki Okudaira - Kyushu University Hanada Lab (SSDL) / IAU CPS SatHub
        """
        center_date = datetime.strptime(date, "%Y-%m-%d").date()
        start_date = center_date - timedelta(days=range)
        end_date   = center_date + timedelta(days=range)

        start_str = start_date.strftime("%Y-%m-%d")
        end_str   = end_date.strftime("%Y-%m-%d")

        # Start Session
        session = requests.Session()

        # Log in
        login_url = 'https://www.space-track.org/ajaxauth/login'
        login_payload = {
            'identity': user_id,
            'password': password
        }

        response = session.post(login_url, data=login_payload)
        if response.status_code != 200:
            tle_result = None
        
        else:
            query_url = (
                "https://www.space-track.org"
                "/basicspacedata/query/"
                "class/gp_history/"
                f"EPOCH/{start_str}--{end_str}/"
                "orderby/NORAD_CAT_ID,EPOCH/"
                "format/3le"
            )

            response = session.get(query_url, stream=True)
            tle_result = response.text

        return response.status_code,tle_result

class celes_trak:
    def get_latest_TLE(
            norad_id: int
            ):
        """
        Get latest Two-Line Element set from space-track.org

        Parameters
        ----------
        norad_id: `int` or `str`
            NORAD catalog number

        Returns
        -------
        response.status_code: `int`
            status code of query
        tle_result: `str`
            Two-Line Element set

        Notes
        -----
            (c) 2025 Kiyoaki Okudaira - Kyushu University Hanada Lab (SSDL) / IAU CPS SatHub
        """
        # Start Session
        session = requests.Session()

        # Get TLE data
        query_url = (
            "https://celestrak.org/NORAD/elements/gp.php?CATNR={0}".format(norad_id)
        )

        response = session.get(query_url, stream=True)

        if response.status_code == 200:
            tle_result = response.text
        else:
            tle_result = None

        return response.status_code,tle_result

class parse:
    def parse_tles_file(
            tle_path: str
            ):
        """
        Read and parse TLE file with multiple Two-Line Element Sets

        Parameters
        ----------
        tle_path: `str`
            PATH of TLE file

        Returns
        -------
        tle_dict: `dict`
            parsed Two-Line Elements Sets ("name", "line1", "line2", "epoch")

        Notes
        -----
            (c) 2025 Kiyoaki Okudaira - Kyushu University Hanada Lab (SSDL) / IAU CPS SatHub
        """
        with open(tle_path, "r", encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f if ln.strip()]

        tle_dict = {}

        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("1 ") and i + 1 < len(lines) and lines[i + 1].startswith("2 "):
                name = None
                line1 = lines[i]
                line2 = lines[i + 1]
                i_next = i + 2
            elif (
                i + 2 < len(lines)
                and lines[i + 1].startswith("1 ")
                and lines[i + 2].startswith("2 ")
            ):
                name = lines[i]
                line1 = lines[i + 1]
                line2 = lines[i + 2]
                i_next = i + 3
            else:
                i += 1
                continue

            satnum = str(line1[2:7].strip())

            # Epoch
            epoch_str = line1[18:32].strip()
            year_2 = int(epoch_str[0:2])
            doy = float(epoch_str[2:])
            year = 2000 + year_2 if year_2 < 57 else 1900 + year_2
            epoch_dt = datetime(year, 1, 1) + timedelta(days=doy - 1.0)

            # TLE info
            tle_info = {
                "name": name,
                "line1": line1,
                "line2": line2,
                "epoch": epoch_dt,
            }

            tle_dict.setdefault(satnum, []).append(tle_info)
            i = i_next

        return tle_dict


    def filter_nearest_tles(
            tle_dict: dict,
            obs_time: str
            ):
        """
        Select nearest TLE to given datetime and filter

        Parameters
        ----------
        tle_dict: `dict`
            parsed Two-Line Elements Sets ("name", "line1", "line2", "epoch")
        obs_time: `str`
            given datetime ("%Y-%m-%dT%H:%M:%S")

        Returns
        -------
        filtered_tle_dict: `dict`
            filtered Two-Line Elements Sets ("name", "line1", "line2", "epoch")

        Notes
        -----
            (c) 2025 Kiyoaki Okudaira - Kyushu University Hanada Lab (SSDL) / IAU CPS SatHub
        """
        filtered_tle_dict = []
        obs_time = datetime.strptime(obs_time[0:19], "%Y-%m-%dT%H:%M:%S")

        for satnum, tle_list in tle_dict.items():
            # Sort TLE based on epoch
            tle_list_sorted = sorted(tle_list, key=lambda x: x["epoch"])

            # TLEs BEFORE observation
            past_candidates = [t for t in tle_list_sorted if t["epoch"] <= obs_time]
            past_best = past_candidates[-1] if past_candidates else None

            # TLEs AFTER observation
            future_candidates = [t for t in tle_list_sorted if t["epoch"] >= obs_time]
            future_best = future_candidates[0] if future_candidates else None

            if past_best is not None:
                filtered_tle_dict.append(past_best)
            if future_best is not None and future_best is not past_best:
                filtered_tle_dict.append(future_best)

        return filtered_tle_dict

def parse_tle2epoch_fname(
        tle_line1: str
        ):
    """
    Retrieve epoch of TLE and parse for file name

    Parameters
    ----------
    tle_line1: `str`
        TLE line 1

    Returns
    -------
    epoch_fname: `str`
        epoch string for file name

    Notes
    -----
        (c) 2025 Kiyoaki Okudaira - Kyushu University Hanada Lab (SSDL) / IAU CPS SatHub
    """
    year = int(tle_line1[18:20])
    year += 2000 if year < 57 else 1900
    day_of_year = float(tle_line1[20:32])
    date = datetime(year, 1, 1) + timedelta(days=day_of_year - 1)
    epoch_fname = date.strftime('%Y%m%d_%H%M%S')

    return epoch_fname

#--------------------------------------------------------------------------------------------------#
# Test                                                                                             #
#--------------------------------------------------------------------------------------------------#