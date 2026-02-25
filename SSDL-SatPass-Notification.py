# %% [markdown]
# # SSDL SatPass Notification
# Written by Kiyoaki Okudaira<br>
# *Kyushu University Hanada Lab / University of Washington / IAU CPS SatHub<br>
# (okudaira.kiyoaki.528@s.kyushu-u.ac.jp or kiyoaki@uw.edu)<br>
# <br>
# This app notifies bright artificial objects expected in 10 days. Data provided by heavens-above.com and SatPhotometry Library.<br>
# <br>
# **History**<br>
# coding 2026-02-24 : 1st coding<br>
# <br>
# (c) 2026 Kiyoaki Okudaira - Kyushu University Hanada Lab (SSDL) / University of Washington / IAU CPS SatHub

# %% [markdown]
# ### Parameters
# **Target**<br>
# In UTC

# %%
from input.satlist.BRIGHT_LEO import *
from pathlib import Path
import os
import sys

# %% [markdown]
# **Heavens-Above settings**

# %%
min_alt      = 30   # minimum altitude of objects [deg] | int or float
min_duration = 60  # minimum duration of objects [sec] | int or float
time_window  = os.getenv("TIME_WINDOW")    # morning, evening or all   | str or bool

# %% [markdown]
# **Slack API settings**

BASE_DIR = Path(__file__).resolve().parent  # .../SSDL-SatPass-Notification
REPO_DIR = BASE_DIR.parent                  # repo root (one level up)

sys.path.insert(0, str(REPO_DIR))
sys.path.insert(0, str(BASE_DIR))

base_PATH = str(BASE_DIR) + "/"
output_PATH = str(BASE_DIR / "output" / "heavens-above")
input_PATH  = str(BASE_DIR / "input" / "heavens-above")
tmp_PATH    = str(BASE_DIR / "tmp" / "heavens-above")

os.makedirs(output_PATH, exist_ok=True)
os.makedirs(input_PATH, exist_ok=True)
os.makedirs(tmp_PATH, exist_ok=True)

token = os.getenv("SLACK_TOKEN")
if not token:
    raise RuntimeError("SLACK_TOKEN is not set. Please set it as an env var or GitHub Actions secret.")

meteoblue_api_key = os.getenv("METEOBLUE_API_KEY")
if not meteoblue_api_key:
    raise RuntimeError("METEOBLUE_API_KEY is not set. Please set it as an env var or GitHub Actions secret.")

channel_id = os.getenv("SLACK_CHANNEL")
send_notice = os.getenv("SEND_NOTICE")
if send_notice == "TRUE":
    send_notice = True
else:
    send_notice = False

notify_type = os.getenv("NOTIFY_TYPE")  # Notification type; "bydate" or "bysat" | str

# %% [markdown]
# **Standard libraries**

# %%
import numpy as np
# from __future__ import annotations
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from time import sleep
import requests, json, pickle

from astropy.table import Table
from astropy.time import Time, TimeDelta
import astropy.units as u
from astroplan import Observer
from astropy.table import vstack

# %% [markdown]
# **Satphotometry library**

# %%
from satphotometry_light import heavens_above,gettle

# %% [markdown]
# **Observatory setting**

# %%
from input.obs_site.KUPT import *

obs_obj = Observer(
    longitude = obs_gd_lon_deg * u.deg,
    latitude = obs_gd_lat_deg * u.deg,
    timezone = obs_timezone,
    name = obs_name
)

now_local = datetime.now(ZoneInfo(obs_timezone))
offset = now_local.utcoffset()

lst_h = offset.total_seconds() // 3600
lst_m = (offset.total_seconds() % 3600) // 60


# %% [markdown]
# **Global constants**

# %%
WEEKDAY_JP = ["月", "火", "水", "木", "金", "土", "日"]
HEAVENS_ABOVE_URL = "https://www.heavens-above.com/"

# %% [markdown]
# ### Heavens-Above
# **Get pass Summary**<br>
# Get pass Summary from www.heavens-above.com/PassSummary.aspx

# %%
print()
print("Retrieving satellite passes from heavens above...")
print()
pass_table = None
for norad_id in norad_ids:
    _,tle_result = gettle.celes_trak.get_latest_TLE(norad_id)
    with open(f"{base_PATH}tmp/heavens-above/tle.txt","w") as f:
        f.write(tle_result)
    tle_dict = gettle.parse.parse_tles_file(f"{base_PATH}tmp/heavens-above/tle.txt")
    satname = tle_dict[str(norad_id)][0]['name'].rstrip()

    query_result = heavens_above.get_pass_summary(norad_id,obs_gd_lon_deg,obs_gd_lat_deg,obs_gd_height,"UCT")
    sat_pass_table = heavens_above.parse_summary2table(query_result,satname)
    if pass_table is None:
        pass_table = sat_pass_table
    else:
        pass_table = vstack([pass_table, sat_pass_table])
    sleep(0.25)

print("Completed : Retrieve satellite passes from heavens above")

# %% [markdown]
# **Timewindow**<br>
# Morning / Evening observation

# %%
print()
print("Processing data from heavens above...")
print()
time_windows = []
dates = []
for row in pass_table:
    obs_start = Time(row["start_utc"]).mjd
    obs_noon = obs_obj.noon(Time(row["start_utc"]), which = "previous")
    sun_horizon = obs_obj.tonight(obs_noon, horizon = 0 * u.deg)
    sunset_lst  = sun_horizon[0].mjd
    sunrise_lst = sun_horizon[1].mjd
    if abs(obs_start-sunset_lst) < abs(obs_start-sunrise_lst):
        time_windows.append("evening")
    else:
        time_windows.append("morning")
    dates.append((Time(row["max_utc"]) + TimeDelta(lst_h*u.hour + lst_m*u.minute)).isot[0:10])
pass_table["date"] = dates
pass_table["time_window"] = time_windows

print("Completed : Process data from heavens above")

# %% [markdown]
# ### METEOBLUE

# %%
METEOBLUE_URL = "https://my.meteoblue.com/packages"

def fetch_meteoblue_10day_astropy(
    lat: float,
    lon: float,
    apikey: str | None = None,
    tz: str = "UTC",
    asl: float | None = None,
    days: int = 10,
    timeout: int = 30,
) -> Table:
    """
    Fetch 10-day forecast from meteoblue and return as Astropy Table.
    
    Columns:
        date (Time)
        pictocode
        t_min [degC]
        t_mean [degC]
        t_max [degC]
        wind_speed_mean [m/s]
        wind_dir [deg]
        cloud_total_mean [%]
    """

    apikey = apikey or os.environ.get("METEOBLUE_APIKEY")
    if not apikey:
        raise ValueError("API key is missing.")

    package_path = "trendpro-1h"
    url = f"{METEOBLUE_URL}/{package_path}"

    params = {
        "lat": f"{lat:.6f}",
        "lon": f"{lon:.6f}",
        "apikey": apikey,
        "format": "json",
        "tz": tz,
    }

    if asl is not None:
        params["asl"] = str(asl)

    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    payload = r.json()

    tbl = Table()
    for key, values in payload["trend_1h"].items():
        if key == "time":
            tbl[key] = Time(values, format="iso")
        else:
            tbl[key] = values

    return tbl

# %%
weather_path = f"{base_PATH}tmp/heavens-above/meteoblue/meteoblue_{Time.now().isot[0:10]}"
if os.path.exists(f"{weather_path}.pkl"):
    with open(f"{weather_path}.pkl", "rb") as f:
        weather_table = pickle.load(f)
else:
    print()
    print("Retrieving weather forecast from meteoblue...")
    print()
    weather_table = fetch_meteoblue_10day_astropy(
        lat=obs_gd_lat_deg,
        lon=obs_gd_lon_deg,
        apikey=meteoblue_api_key,
        tz="UTC",
        asl=int(obs_gd_height*1000)
    )
    weather_table.write(f"{weather_path}.csv",overwrite=True)
    with open(f"{weather_path}.pkl", 'wb') as f:
        pickle.dump(weather_table, f)
    
    print("Completed : Retrieve weather forecast from meteoblue")
# %%
print()
print("Processing data from meteoblue...")
print()
totalcloudcover = []
highclouds = []
midclouds = []
lowclouds = []
temperature = []
windspeed = []
pictocode = []

for row in pass_table:
    idxs = np.where(weather_table["time"] == row["start_utc"][0:13]+":00:00")
    if len(idxs) > 0:
        idx = idxs[0][0]
        totalcloudcover.append(weather_table[idx]["totalcloudcover"])
        highclouds.append(weather_table[idx]["highclouds"])
        midclouds.append(weather_table[idx]["midclouds"])
        lowclouds.append(weather_table[idx]["lowclouds"])
        temperature.append(weather_table[idx]["temperature"])
        windspeed.append(weather_table[idx]["windspeed"])
        pictocode.append(weather_table[idx]["pictocode"])
    else:
        totalcloudcover.append("N/A")
        highclouds.append("N/A")
        midclouds.append("N/A")
        lowclouds.append("N/A")
        temperature.append("N/A")
        windspeed.append("N/A")
        pictocode.append("N/A")
pass_table["totalcloudcover"] = totalcloudcover
pass_table["highclouds"] = highclouds
pass_table["midclouds"] = midclouds
pass_table["lowclouds"] = lowclouds
pass_table["temperature"] = temperature
pass_table["windspeed"] = windspeed
pass_table["pictocode"] = pictocode

# %%
pictocode_hourly = {
    1:  {"en": "Clear, cloudless sky",                                   "ja": "快晴（雲なし）",                         "emoji": "☀️"},
    2:  {"en": "Clear, few cirrus",                                      "ja": "晴れ（薄い巻雲少し）",                  "emoji": "☀️"},
    3:  {"en": "Clear with cirrus",                                      "ja": "晴れ（巻雲あり）",                      "emoji": "☀️"},
    4:  {"en": "Clear with few low clouds",                              "ja": "晴れ（低い雲少し）",                    "emoji": "🌤️"},
    5:  {"en": "Clear with few low clouds and few cirrus",               "ja": "晴れ（低い雲少し＋巻雲少し）",          "emoji": "🌤️"},
    6:  {"en": "Clear with few low clouds and cirrus",                   "ja": "晴れ（低い雲少し＋巻雲あり）",          "emoji": "🌤️"},
    7:  {"en": "Partly cloudy",                                          "ja": "晴れ時々曇り",                          "emoji": "⛅"},
    8:  {"en": "Partly cloudy and few cirrus",                           "ja": "晴れ時々曇り（巻雲少し）",              "emoji": "⛅"},
    9:  {"en": "Partly cloudy and cirrus",                               "ja": "晴れ時々曇り（巻雲あり）",              "emoji": "⛅"},
    10: {"en": "Mixed with some thunderstorm clouds possible",           "ja": "晴れ/曇り（積乱雲の可能性）",            "emoji": "🌦️"},
    11: {"en": "Mixed with few cirrus with some thunderstorm clouds possible",
         "ja": "晴れ/曇り（巻雲少し＋積乱雲の可能性）",                   "emoji": "🌦️"},
    12: {"en": "Mixed with cirrus with some thunderstorm clouds possible",
         "ja": "晴れ/曇り（巻雲あり＋積乱雲の可能性）",                   "emoji": "🌦️"},
    13: {"en": "Clear but hazy",                                         "ja": "晴れ（霞）",                            "emoji": "🌫️"},
    14: {"en": "Clear but hazy with few cirrus",                         "ja": "晴れ（霞＋巻雲少し）",                  "emoji": "🌫️"},
    15: {"en": "Clear but hazy with cirrus",                             "ja": "晴れ（霞＋巻雲あり）",                  "emoji": "🌫️"},
    16: {"en": "Fog/low stratus clouds",                                 "ja": "霧 / 低い層雲",                         "emoji": "🌫️"},
    17: {"en": "Fog/low stratus clouds with few cirrus",                 "ja": "霧/低い層雲（巻雲少し）",               "emoji": "🌫️"},
    18: {"en": "Fog/low stratus clouds with cirrus",                     "ja": "霧/低い層雲（巻雲あり）",               "emoji": "🌫️"},
    19: {"en": "Mostly cloudy",                                          "ja": "ほぼ曇り",                              "emoji": "☁️"},
    20: {"en": "Mostly cloudy and few cirrus",                           "ja": "ほぼ曇り（巻雲少し）",                  "emoji": "☁️"},
    21: {"en": "Mostly cloudy and cirrus",                               "ja": "ほぼ曇り（巻雲あり）",                  "emoji": "☁️"},
    22: {"en": "Overcast",                                               "ja": "本曇り",                                "emoji": "☁️"},
    23: {"en": "Overcast with rain",                                     "ja": "本曇り（雨）",                          "emoji": "🌧️"},
    24: {"en": "Overcast with snow",                                     "ja": "本曇り（雪）",                          "emoji": "🌨️"},
    25: {"en": "Overcast with heavy rain",                               "ja": "本曇り（強い雨）",                      "emoji": "🌧️🌧️"},
    26: {"en": "Overcast with heavy snow",                               "ja": "本曇り（大雪）",                        "emoji": "❄️"},
    27: {"en": "Rain, thunderstorms likely",                             "ja": "雨（雷の可能性）",                      "emoji": "⛈️"},
    28: {"en": "Light rain, thunderstorms likely",                       "ja": "弱い雨（雷の可能性）",                  "emoji": "🌦️⛈️"},
    29: {"en": "Storm with heavy snow",                                  "ja": "吹雪/嵐（大雪）",                       "emoji": "🌨️🌪️"},
    30: {"en": "Heavy rain, thunderstorms likely",                       "ja": "強い雨（雷の可能性）",                  "emoji": "⛈️🌧️"},
    31: {"en": "Mixed with showers",                                     "ja": "変わりやすい天気（にわか雨）",          "emoji": "🌦️"},
    32: {"en": "Mixed with snow showers",                                "ja": "変わりやすい天気（にわか雪）",          "emoji": "🌨️"},
    33: {"en": "Overcast with light rain",                               "ja": "本曇り（弱い雨）",                      "emoji": "🌦️"},
    34: {"en": "Overcast with light snow",                               "ja": "本曇り（弱い雪）",                      "emoji": "🌨️"},
    35: {"en": "Overcast with mixture of snow and rain",                 "ja": "本曇り（みぞれ/雨雪混在）",             "emoji": "🌧️❄️"},
}
print("Completed : Process data from meteoblue")

# %% [markdown]
# ### Save CSV

# %%
pass_table.write(f"{output_PATH}/SatPass.csv",overwrite=True)

# %% [markdown]
# ### iCalendar

# %%
print()
print("Writing ics file...")
print()
def _ics_dt(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def _ics_lst_dt(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%S")

def _ics_escape(text: str) -> str:
    text = str(text)
    return (
        text.replace("\\", "\\\\")
            .replace(";", r"\;")
            .replace(",", r"\,")
            .replace("\r\n", r"\n")
            .replace("\n", r"\n")
    )

def _ics_escape_uri(uri: str) -> str:
    return str(uri).replace("\\", "\\\\")

def _fold_ics_line(line: str, limit: int = 75) -> str:
    if len(line) <= limit:
        return line
    out = []
    while len(line) > limit:
        out.append(line[:limit])
        line = " " + line[limit:]
    out.append(line)
    return "\r\n".join(out)


def write_passes_to_ics(pass_table, out_path, calendar_name: str = "Satellite Passes") -> str:
    out_path
    now_utc = datetime.now(timezone.utc)

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//SatPhotometry//SatPass//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:{_ics_escape(calendar_name)}",
    ]

    # Astropy Table rows can be iterated directly
    for row in pass_table:
        satid = row["satid"]
        satname = row["satname"]

        event_url = f"{HEAVENS_ABOVE_URL}{row["detail_url"]}"

        start_lst_obj = (Time(row["start_utc"]) + TimeDelta(lst_h*u.hour + lst_m*u.minute))
        start_lst_time = start_lst_obj.isot[11:19]
        max_lst_time = (Time(row["max_utc"]) + TimeDelta(lst_h*u.hour + lst_m*u.minute)).isot[11:19]
        end_lst_obj = (Time(row["end_utc"]) + TimeDelta(lst_h*u.hour + lst_m*u.minute))
        end_lst_time = (Time(row["end_utc"]) + TimeDelta(lst_h*u.hour + lst_m*u.minute)).isot[11:19]

        start_lst_dt = start_lst_obj.to_datetime()
        end_lst_dt = end_lst_obj.to_datetime()

        obs_noon = obs_obj.noon(Time(row["start_utc"]), which = "previous")
        sun_horizon = obs_obj.tonight(obs_noon, horizon = 0 * u.deg)
        astro_twilight = obs_obj.tonight(obs_noon, horizon = -18 * u.deg)
        sunset_lst  = (sun_horizon[0]+ TimeDelta(lst_h*u.hour + lst_m*u.minute)).isot[11:16]
        sunrise_lst = (sun_horizon[1]+ TimeDelta(lst_h*u.hour + lst_m*u.minute)).isot[11:16]
        astro_dusk_lst = (astro_twilight[0]+ TimeDelta(lst_h*u.hour + lst_m*u.minute)).isot[11:16]
        astro_dawn_lst = (astro_twilight[1]+ TimeDelta(lst_h*u.hour + lst_m*u.minute)).isot[11:16]

        if row['totalcloudcover'] != "N/A":
            pict = pictocode_hourly[row["pictocode"]]["emoji"]
            pict_desc = pictocode_hourly[row["pictocode"]]["en"]

        # Summary (event title)
        summary = f"{pict} {satname}"

        # Description (details)
        desc = (
            f"================================\n"
            f"{satname} | NORAD ID {satid}\n"
            f"================================\n"
            f"Mag : {row['mag']}\n"
            f"Duration : {row['duration']//60} min {row['duration']%60} sec\n"
            f"Pass start : {start_lst_time} (el={row['start_alt']}° / {row['start_az']})\n"
            f"Highest : {max_lst_time} (el={row['max_alt']}° / {row['max_az']})\n"
            f"Pass end : {end_lst_time} (el={row['end_alt']}° / {row['end_az']})\n"
            f"----------------------------------------\n"
            f"Sunset : {sunset_lst}\n"
            f"Astronomical dusk : {astro_dusk_lst}\n"
            f"Astronomical dawn : {astro_dawn_lst}\n"
            f"Sunrise : {sunrise_lst}\n"
            f"----------------------------------------\n"
            f"{pict} {pict_desc}\n"
            f"Clouds : {row["totalcloudcover"]}% (L:{row["lowclouds"]} M:{row["midclouds"]} H:{row["highclouds"]})\n"
            f"Temperature : {row["temperature"]:.0f} °C\n"
            f"Wind : {row["windspeed"]:.1f} m/s\n"
            f"----------------------------------------\n"
            f"Data Provided by Heavens-Above\n"
            f"Created / updated at {Time.now().isot[0:19]}\n"
            f"================================\n"
            f"SSDL SatPass Notification System\n"
            f"with SatPhotometry Library\n"
            f"(c) 2026 Kiyoaki Okudaira - Kyushu University\n"
            f"================================"
        )
        uid = f"{satid}.{row["mjd"]:.1f}@SatPass"

        event_lines = [
            "BEGIN:VEVENT",
            f"UID:{uid}",
            f"DTSTAMP:{_ics_dt(now_utc)}",
            f"DTSTART;TZID={obs_timezone}:{_ics_lst_dt(start_lst_dt)}",
            f"DTEND;TZID={obs_timezone}:{_ics_lst_dt(end_lst_dt)}",
            f"SUMMARY:{_ics_escape(summary)}",
            f"LOCATION:{obs_name}",
            f"GEO:{obs_gd_lat_deg:.6f};{obs_gd_lon_deg:.6f}",
            f"X-APPLE-STRUCTURED-LOCATION;VALUE=URI;X-APPLE-RADIUS=72;X-TITLE={obs_name}:geo:{obs_gd_lat_deg:.6f},{obs_gd_lon_deg:.6f}",
            f"URL:{_ics_escape_uri(event_url)}",
            f"DESCRIPTION:{_ics_escape(desc)}",
            "END:VEVENT",
        ]

        # Fold long lines
        for el in event_lines:
            lines.append(_fold_ics_line(el))

    lines.append("END:VCALENDAR")

    ics_text = "\r\n".join(lines) + "\r\n"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(ics_text)

    return out_path

# %%
if time_window == "evening" or time_window == "morning":
    good_pass_table = pass_table[(pass_table["max_alt"] >= min_alt) & (pass_table["duration"] > min_duration) & (pass_table["visible"] == True) & (pass_table["time_window"] == time_window)]
else:
    good_pass_table = pass_table[(pass_table["max_alt"] >= min_alt) & (pass_table["duration"] > min_duration) & (pass_table["visible"] == True)]

good_pass_table = good_pass_table.group_by("satname")
out_file = write_passes_to_ics(good_pass_table, out_path=f"{output_PATH}/SatPass.ics")

print("Completed : Write ics file")

# %% [markdown]
# **Upload to Server**

# %%
# !scp /Users/kiyoaki/VScode/satphotometry_package/output/heavens-above/SatPass.ics samc@m39.coreserver.jp:/virtual/samc/public_html/www.kiyoaki.jp/wp-content/uploads/SatPass-KUPT-bright.ics

# %% [markdown]
# ### Slack Notification
# **Construct contents**<br>
# By satellites

print()
print("Writing Slack messages...")
print()

# %%
if notify_type == "bysat":
    lines = []
    lines.append(f"*🛰️ 注目すべき人工天体の上空通過予測 (試験送信)*")
    lines.append(f"直近10日間の注目すべき人工天体の上空通過予測をお知らせします．")
    lines.append(f"(Filter : alt > {min_alt} deg & duration > {min_duration} sec & time window = {time_window})")
    lines.append("")
    
    for group in pass_table.groups:
        satname = group[0]["satname"]
        norad_id = group[0]["satid"]

        if len(pass_table) > 0:
            lines.append(f"*{satname} (NORAD ID {norad_id})* は直近10日間で{len(group)}件の観測可能な上空通過が予測されています．")
        else:
            lines.append(f"*{satname} (NORAD ID {norad_id})* は直近10日間に観測可能な上空通過がありません．")
        
        if time_window == "evening" or time_window == "morning":
            good_condition = (group["max_alt"] > 30) & (group["duration"] > 120) & (group["visible"] == True) & (pass_table["time_window"] == time_window)
        else:
            good_condition = (group["max_alt"] > 30) & (group["duration"] > 120) & (group["visible"] == True)

        if np.sum(good_condition) > 0:
            lines.append(f"良い観測条件の上空通過({np.sum(good_condition)}件)は以下の通りです．")
            lines.append("")

            table_lines = []
            table_lines.append("　　　            Start              Highest            End                Clouds      Wind")
            table_lines.append("観測日            LST      (ALT AZ)  LST      (ALT AZ)  LST      (ALT AZ)   L | M | H  Speed")

            for row in group[good_condition]:
                start_lst_obj = (Time(row["start_utc"]) + TimeDelta(lst_h*u.hour + lst_m*u.minute))
                start_lst_weekday = WEEKDAY_JP[start_lst_obj.to_datetime().weekday()]
                start_lst_date = start_lst_obj.isot[0:10]
                start_lst_time = start_lst_obj.isot[11:19]

                max_lst_time = (Time(row["max_utc"]) + TimeDelta(lst_h*u.hour + lst_m*u.minute)).isot[11:19]
                end_lst_time = (Time(row["end_utc"]) + TimeDelta(lst_h*u.hour + lst_m*u.minute)).isot[11:19]

                if row['totalcloudcover'] == "N/A":
                    cloud_desc = "N/A"
                    wind_desc = "N/A"
                else:
                    cloud_desc = f"{row['lowclouds']}".rjust(3)+f"|"+f"{row['midclouds']}".rjust(3)+f"|"+f"{row['highclouds']}".rjust(3)
                    wind_desc = f"{row['windspeed']:.1f} mps"

                table_lines.append(
                    f"{start_lst_date} {start_lst_weekday}曜日 "
                    + f"{start_lst_time} ({row['start_alt']:.0f}° {row['start_az']})".ljust(19)
                    + f"{max_lst_time} ({row['max_alt']:.0f}° {row['max_az']})".ljust(19)
                    + f"{end_lst_time} ({row['end_alt']:.0f}° {row['end_az']})".ljust(19)
                    + f"{cloud_desc}".ljust(12)
                    + f"{wind_desc}"
                )

            # Code block
            lines.append("```" + "\n".join(table_lines) + "```")
        else:
            lines.append("良い観測条件の上空通過はありません．")
        lines.append("")

    lines.append(f"📅 <https://www.kiyoaki.jp/wp-content/uploads/SatPass-KUPT-bright.ics|*カレンダーをダウンロード*>")
    lines.append(f"URLを照会カレンダーとして Appleカレンダー または Googleカレンダー に登録・表示できます．")
    lines.append(f"Data Provided by <https://www.heavens-above.com|Heavens-Above> / <https://www.meteoblue.com/en/weather/week/33.599N130.212E|Meteoblue> / <https://github.com/kiyo-astro/satphotometry_package/|SatPhotometry Library>")
    lines.append(f"This message is automatically sent by SSDL SatPass Notification System")
    lines.append(f"Created at {Time.now().iso[0:19]} (UTC)")

# %% [markdown]
# By date

# %%
if notify_type == "bydate":
    if time_window == "evening" or time_window == "morning":
        good_pass_table = pass_table[(pass_table["max_alt"] >= min_alt) & (pass_table["duration"] > min_duration) & (pass_table["visible"] == True) & (pass_table["time_window"] == time_window)]
    else:
        good_pass_table = pass_table[(pass_table["max_alt"] >= min_alt) & (pass_table["duration"] > min_duration) & (pass_table["visible"] == True)]
    good_pass_table.sort("start_utc")
    good_pass_table = good_pass_table.group_by("date")

    lines = []
    lines.append(f"*🛰️ 注目すべき人工天体の上空通過予測 (試験送信)*")
    lines.append(f"直近10日間の注目すべき人工天体の上空通過予測をお知らせします．")
    lines.append(f"(Filter : alt > {min_alt} deg & duration > {min_duration} sec & time window = {time_window})")
    lines.append("")

    if len(good_pass_table) > 0:
        for group in good_pass_table.groups:
            date = group[0]["date"]
            start_lst_obj = (Time(group[0]["start_utc"]) + TimeDelta(lst_h*u.hour + lst_m*u.minute))
            start_lst_weekday = WEEKDAY_JP[start_lst_obj.to_datetime().weekday()]
            lines.append(f"*{date[0:4]}年{date[5:7]}月{date[8:10]}日 {start_lst_weekday}曜日*")

            weather_available = group[group["totalcloudcover"] != "N/A"]
            if len(weather_available) > 0:
                cloud_min = np.min(weather_available["totalcloudcover"])
                cloud_max = np.max(weather_available["totalcloudcover"])
                cloud_avg = np.mean(weather_available["totalcloudcover"])
                pict = pictocode_hourly[np.max(weather_available["pictocode"])]["emoji"]
                pict_desc = pictocode_hourly[np.max(weather_available["pictocode"])]["ja"]
                wind_avg = np.mean(weather_available["windspeed"])
                temp_avg = np.mean(weather_available["temperature"])
                lines.append(f"{pict} {pict_desc} | {temp_avg:.0f}°C | Wind {wind_avg:.1f}mps | Clouds max:{cloud_max}% avg:{cloud_avg:.0f}% min:{cloud_min}%")
            
            lines.append(f"注目すべき衛星の良い観測条件の上空通過が{len(group)}件予測されています．")

            lines.append("")

            table_lines = []
            table_lines.append(f"{date}           Start              Highest            End                Clouds      Wind")
            table_lines.append(f"Satellite            LST      (ALT AZ)  LST      (ALT AZ)  LST      (ALT AZ)   L | M | H  Speed")
            for row in group:
                start_lst_obj = (Time(row["start_utc"]) + TimeDelta(lst_h*u.hour + lst_m*u.minute))
                start_lst_weekday = WEEKDAY_JP[start_lst_obj.to_datetime().weekday()]
                start_lst_date = start_lst_obj.isot[0:10]
                start_lst_time = start_lst_obj.isot[11:19]

                max_lst_time = (Time(row["max_utc"]) + TimeDelta(lst_h*u.hour + lst_m*u.minute)).isot[11:19]
                end_lst_time = (Time(row["end_utc"]) + TimeDelta(lst_h*u.hour + lst_m*u.minute)).isot[11:19]

                if row['totalcloudcover'] == "N/A":
                    cloud_desc = "N/A"
                    wind_desc = "N/A"
                else:
                    cloud_desc = f"{row['lowclouds']}".rjust(3)+f"|"+f"{row['midclouds']}".rjust(3)+f"|"+f"{row['highclouds']}".rjust(3)
                    wind_desc = f"{row['windspeed']:.1f} mps"

                table_lines.append(
                    f"{row["satname"]}".ljust(21) 
                    + f"{start_lst_time} ({row['start_alt']:.0f}° {row['start_az']})".ljust(19)
                    + f"{max_lst_time} ({row['max_alt']:.0f}° {row['max_az']})".ljust(19)
                    + f"{end_lst_time} ({row['end_alt']:.0f}° {row['end_az']})".ljust(19)
                    + f"{cloud_desc}".ljust(12)
                    + f"{wind_desc}"
                )

            # Code block
            lines.append("```" + "\n".join(table_lines) + "```")

            lines.append("")
    else:
        lines.append("直近10日間に注目すべき人工天体の容易観測条件での上空通過はありません．")
        lines.append("")
    lines.append(f"📅 <https://www.kiyoaki.jp/wp-content/uploads/SatPass-KUPT-bright.ics|*カレンダーをダウンロード*>")
    lines.append(f"URLを照会カレンダーとして Appleカレンダー または Googleカレンダー に登録・表示できます．")
    lines.append(f"")
    lines.append(f"Data Provided by <https://www.heavens-above.com|Heavens-Above> / <https://www.meteoblue.com/en/weather/week/33.599N130.212E|Meteoblue> / <https://github.com/kiyo-astro/satphotometry_package/|SatPhotometry Library>")
    lines.append(f"This message is automatically sent by SSDL SatPass Notification System")
    lines.append(f"Created at {Time.now().iso[0:19]} (UTC)")

print("Completed : Write Slack messages. Preview will be displayed below.")
print()

# %% [markdown]
# **Preview**

# %%
for f in lines:
    print(f)

print()
print("Uploading messages and files to Slack...")
print()

# %% [markdown]
# **Send notification**

# %%
if send_notice:
    content = "\n".join(lines)

    # upload file path
    file_path = f"{output_PATH}/SatPass.ics"

    # comment
    title = os.path.basename(file_path)

    def slack_api_post(url: str, token: str, data=None, files=None, timeout=60):
        r = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            data=data,
            files=files,
            timeout=timeout,
        )
        r.raise_for_status()
        payload = r.json()
        if not payload.get("ok", False):
            raise RuntimeError(f"Slack API error: {payload}")
        return payload

    # retrieve file id and url
    file_size = os.path.getsize(file_path)
    filename = os.path.basename(file_path)

    get_url_payload = slack_api_post(
        "https://slack.com/api/files.getUploadURLExternal",
        token=token,
        data={
            "filename": filename,
            "length": str(file_size),  # bytes
        },
    )
    upload_url = get_url_payload["upload_url"]
    file_id = get_url_payload["file_id"]

    # upload file
    with open(file_path, "rb") as f:
        upload_resp = requests.post(
            upload_url,
            headers={"Content-Type": "application/octet-stream"},
            data=f,
            timeout=300,
        )
    upload_resp.raise_for_status()

    # confirm file share
    complete_payload = slack_api_post(
        "https://slack.com/api/files.completeUploadExternal",
        token=token,
        data={
            "files": json.dumps([{"id": file_id, "title": title}]),
            "channel_id": channel_id,
            "initial_comment": content,
        },
    )

    print("Uploaded OK")
    print(json.dumps(complete_payload, indent=2, ensure_ascii=False))


