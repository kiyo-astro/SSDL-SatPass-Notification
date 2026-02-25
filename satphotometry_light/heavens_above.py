#--------------------------------------------------------------------------------------------------#
# heavens_above.py                                                                                 #
# Developed by Kiyoaki Okudaira * University of Washington / Kyushu University / IAU CPS SatHub    #
#--------------------------------------------------------------------------------------------------#
# Description                                                                                      #
#--------------------------------------------------------------------------------------------------#
# Retrieve orbit data from heavens-above.com                                                       #
#--------------------------------------------------------------------------------------------------#
# History                                                                                          #
#--------------------------------------------------------------------------------------------------#
# coding 2026.02.13: 1st coding                                                                    #
#--------------------------------------------------------------------------------------------------#

#--------------------------------------------------------------------------------------------------#
# Libraries                                                                                        #
#--------------------------------------------------------------------------------------------------#
import requests
import re
import html
import numpy as np
import math
from urllib.parse import urlparse, parse_qs

from astropy.time import Time, TimeDelta
from astropy.table import Table
import astropy.units as u

#--------------------------------------------------------------------------------------------------#
# Main                                                                                             #
#--------------------------------------------------------------------------------------------------#
PASSSUMMARY_URL  = "https://www.heavens-above.com/PassSummary.aspx"
PASSDETAIL_URL   = "https://www.heavens-above.com/passdetails.aspx"
PASSSKYCHART_URL = "https://www.heavens-above.com/PassSkyChart2.ashx"
SKYCHART_URL     = "https://www.heavens-above.com/wholeskychart.ashx"

def get_pass_summary(
        norad_id: int | str,
        obs_gd_lon_deg: float,
        obs_gd_lat_deg: float,
        obs_gd_height: float,
        ha_timezone: str ="UCT"
        ):
    """
    Get satellite pass summary from heavens-above.com

    Parameters
    ----------
    norad_id: `int` or `str`
        NORAD catalog number
    obs_gd_lon_deg: `float`
        Geodetic longitude [deg]
    obs_gd_lat_deg: `float`
        Geodetic latitude [deg]
    obs_gd_height: `float`
        Geodetic height [km]
    ha_timezone: `str`
        Pass Chart display timezone. Default is "UCT"

    Returns
    -------
    query_result: `str`
        Satellite pass summary (HTML format)

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    query_params = {
        "satid" : f"{norad_id:.0f}",
        "lat"   : f"{obs_gd_lat_deg:.6f}",
        "lng"   : f"{obs_gd_lon_deg:.6f}",
        "loc"   : "Unspecified",
        "alt"   : f"{obs_gd_height*1000:.0f}",
        "tz"    : f"{ha_timezone}"
        }

    r = requests.get(PASSSUMMARY_URL, params=query_params)
    r.raise_for_status()
    query_result = r.text

    return query_result

def parse_summary2mjd(
        query_result: str
        ):
    """
    Parse satellite pass summary to pass MJD list

    Parameters
    ----------
    query_result: `str`
        Satellite pass summary (HTML format)

    Returns
    -------
    mjds: `np.ndarray`
        Satellite pass MJD list

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    s = html.unescape(query_result)
    mjd_strs = re.findall(r'passdetails\.aspx\?[^"\']*?\bmjd=([0-9.]+)\b', s)
    mjds = [float(x) for x in mjd_strs]
    mjds = np.array(list(dict.fromkeys(mjds)))

    return mjds

def parse_summary2table(
        query_result: str,
        satname: str = ""
        ):
    """
    Parse satellite pass summary to pass MJD list

    Parameters
    ----------
    query_result: `str`
        Satellite pass summary (HTML format)

    Returns
    -------
    pass_table: `astropy.table.table.Table`
        Satellite pass MJD list
    satname: `str`
        Satellite name. Default is "".

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """    
    # internal functions
    def _strip_tags(s: str) -> str:
        return re.sub(r"<.*?>", "", s).strip()


    def _strip_deg(s: str) -> float:
        return float(s.replace("°", "").strip())


    def _extract_passdetails_url(tr_html: str) -> str:
        # 1) <a href="...">
        m = re.search(r'<a[^>]+href="([^"]*passdetails\.aspx[^"]*)"', tr_html)
        if m:
            return html.unescape(m.group(1))

        # 2) onclick="window.location='...'"
        m = re.search(r"window\.location\s*=\s*'([^']*passdetails\.aspx[^']*)'", tr_html)
        if m:
            return html.unescape(m.group(1))

        return ""

    def _qs_get_first(qs, key, default=None):
        v = qs.get(key)
        if not v:
            return default
        return v[0]
    tr_list = re.findall(
        r'<tr\s+class="clickableRow".*?</tr>',
        query_result,
        flags=re.DOTALL
    )

    # output canvas
    cols = {
        "satid": [],
        "satname": [],
        "mag": [],
        "duration": [],
        "start_utc": [],
        "start_alt": [],
        "start_az": [],
        "max_utc": [],
        "max_alt": [],
        "max_az": [],
        "end_utc": [],
        "end_alt": [],
        "end_az": [],
        "visible": [],
        "detail_url": [],
        "mjd": []
    }

    for tr_html in tr_list:

        url = _extract_passdetails_url(tr_html)

        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr_html, flags=re.DOTALL)
        tds_text = [_strip_tags(x) for x in tds]

        if len(tds_text) < 12:
            continue

        date_str = tds_text[0]
        try:
            brightness = float(tds_text[1])
        except:
            brightness = None

        start_time = tds_text[2]
        start_alt = _strip_deg(tds_text[3])
        start_az = tds_text[4]

        max_time = tds_text[5]
        max_alt = _strip_deg(tds_text[6])
        max_az = tds_text[7]

        end_time = tds_text[8]
        end_alt = _strip_deg(tds_text[9])
        end_az = tds_text[10]

        pass_type = tds_text[11]
        if pass_type == "visible":
            pass_type = True
        else:
            pass_type = False

        # PassDetail query
        qs = parse_qs(urlparse(url).query) if url else {}

        satid = _qs_get_first(qs, "satid", None)
        mjd = _qs_get_first(qs, "mjd", None)
        # pass_kind = _qs_get_first(qs, "type", "")

        satid_i = int(satid) if satid is not None else -1
        mjd_f = float(mjd) if mjd is not None else float("nan")

        max_time_obj = Time(mjd_f, format="mjd", scale="utc")
        max_time = max_time_obj.isot[:11] + max_time
        max_time_obj = Time(max_time)

        start_time = max_time_obj.isot[:11] + start_time
        start_time_obj = Time(start_time)
        end_time = max_time_obj.isot[:11] + end_time
        end_time_obj = Time(end_time)

        duration = (end_time_obj - start_time_obj).sec
        # duration_min = int(duration // 60)
        # duration_sec = int(duration % 60)

        # duration_f = f"{duration_min:02d}:{duration_sec:02d}"

        if start_time_obj > max_time_obj:
            start_time_obj - TimeDelta(1 * u.day)
        if end_time_obj < max_time_obj:
            end_time_obj + TimeDelta(1 * u.day)

        start_time = start_time_obj.isot[0:19]
        max_time = max_time_obj.isot[0:19]
        end_time = end_time_obj.isot[0:19]

        # output
        # cols["date_str"].append(date_str)
        cols["satid"].append(satid_i)
        cols["satname"].append(satname)
        cols["mag"].append(brightness)
        cols["duration"].append(int(duration))
        cols["start_utc"].append(start_time)
        cols["start_alt"].append(start_alt)
        cols["start_az"].append(start_az)
        cols["max_utc"].append(max_time)
        cols["max_alt"].append(max_alt)
        cols["max_az"].append(max_az)
        cols["end_utc"].append(end_time)
        cols["end_alt"].append(end_alt)
        cols["end_az"].append(end_az)
        cols["visible"].append(pass_type)
        cols["detail_url"].append(url)
        cols["mjd"].append(mjd_f)
        # cols["pass_kind"].append(pass_kind)
    
    pass_table = Table(
        cols,
        dtype=[object, object, object, object, object, object, object, object, object, object, object, object, object, object, object, object]
        )

    return pass_table

def get_pass_detail(
        norad_id: int | str,
        obs_gd_lon_deg: float,
        obs_gd_lat_deg: float,
        obs_gd_height: float,
        ha_mjd: float,
        ha_timezone: str = "UCT"
        ):
    """
    Get satellite pass detail from heavens-above.com

    Parameters
    ----------
    norad_id: `int` or `str`
        NORAD catalog number
    obs_gd_lon_deg: `float`
        Geodetic longitude [deg]
    obs_gd_lat_deg: `float`
        Geodetic latitude [deg]
    obs_gd_height: `float`
        Geodetic height [km]
    ha_mjd: `float`
        MJD at start of satellite pass
    ha_timezone: `str`
        Pass Chart display timezone. Default is "UCT"

    Returns
    -------
    query_result: `str`
        Satellite pass detail (HTML format)

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    query_params = {
        "lat"   : f"{obs_gd_lat_deg:.6f}",
        "lng"   : f"{obs_gd_lon_deg:.6f}",
        "loc"   : "Unspecified",
        "alt"   : f"{obs_gd_height*1000:.0f}",
        "tz"    : f"{ha_timezone}",
        "satid" : f"{norad_id:.0f}",
        "mjd"   : f"{ha_mjd}",
        "type"  : "V"
        }

    r = requests.get(PASSDETAIL_URL, params=query_params)
    r.raise_for_status()
    query_result = r.text

    return query_result

def parse_detail2passid(
        query_result: str
        ):
    """
    Parse satellite pass summary to satellite pass ID for PassSkyChart query

    Parameters
    ----------
    query_result: `str`
        Satellite pass detail (HTML format)

    Returns
    -------
    pass_id: `str`
        Satellite pass ID for PassSkyChart query

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    m = re.search(r'PassSkyChart2\.ashx\?[^"\']*\bpassID=(\d+)\b', query_result)
    if not m:
        raise ValueError("Error : Pass SKY Chart not found")
    pass_id = m.group(1)

    return pass_id

def get_pass_chart(
        pass_id: int | str,
        obs_gd_lon_deg: float,
        obs_gd_lat_deg: float,
        obs_gd_height: float,
        ha_timezone: str = "UCT",
        ha_imgsize: int = 800
        ):
    """
    Get satellite pass detail from heavens-above.com

    Parameters
    ----------
    pass_id: `str`
        Satellite pass ID for PassSkyChart query
    obs_gd_lon_deg: `float`
        Geodetic longitude [deg]
    obs_gd_lat_deg: `float`
        Geodetic latitude [deg]
    obs_gd_height: `float`
        Geodetic height [km]
    ha_timezone: `str`
        Pass Chart display timezone. Default is "UCT"
    ha_timezone: `int`
        Pass Chart image size [pix]. Default is 800

    Returns
    -------
    query_result: `bytes`
        Satellite pass chart image

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    query_params = {
        "passID"    : f"{pass_id}",
        "size"      : f"{ha_imgsize:.0f}",
        "lat"       : f"{obs_gd_lat_deg:.6f}",
        "lng"       : f"{obs_gd_lon_deg:.6f}",
        "loc"       : "Unspecified",
        "alt"       : f"{obs_gd_height*1000:.0f}",
        "tz"        : f"{ha_timezone}",
        "showUnlit" : "false"
        }

    r = requests.get(PASSSKYCHART_URL, params=query_params)
    r.raise_for_status()
    query_result = r.content

    return query_result

def get_wholeskychart(
        obs_gd_lon_deg: float,
        obs_gd_lat_deg: float,
        obs_gd_height: float,
        ha_mjd: float,
        ha_timezone: str = "UCT",
        ha_imgsize: int = 800
        ):
    """
    Get satellite pass detail from heavens-above.com

    Parameters
    ----------
    obs_gd_lon_deg: `float`
        Geodetic longitude [deg]
    obs_gd_lat_deg: `float`
        Geodetic latitude [deg]
    obs_gd_height: `float`
        Geodetic height [km]
    ha_mjd: `float`
        MJD
    ha_timezone: `str`
        Pass Chart display timezone. Default is "UCT"
    ha_timezone: `int`
        Pass Chart image size [pix]. Default is 800

    Returns
    -------
    query_result: `bytes`
        Satellite pass chart image

    Notes
    -----
        (c) 2026 Kiyoaki Okudaira - University of Washington / IAU CPS SatHub
    """
    "lat=0&lng=0&loc=Unspecified&alt=0&tz=UCT&size=800  SL=1&SN=1&BW=1&time=61085.28472&ecl=0&cb=0"
    query_params = {
        "lat"       : f"{obs_gd_lat_deg:.6f}",
        "lng"       : f"{obs_gd_lon_deg:.6f}",
        "loc"       : "Unspecified",
        "alt"       : f"{obs_gd_height*1000:.0f}",
        "tz"        : f"{ha_timezone}",
        "size"      : f"{ha_imgsize:.0f}",
        "SL"        : "1",
        "SN"        : "1",
        "BW"        : "1",
        "time"      : f"{ha_mjd}",
        "ecl"       : "0",
        "cb"        : "0"
        }

    r = requests.get(SKYCHART_URL, params=query_params)
    r.raise_for_status()
    query_result = r.content

    return query_result


#--------------------------------------------------------------------------------------------------#
# Test                                                                                             #
#--------------------------------------------------------------------------------------------------#