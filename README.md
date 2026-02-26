# SSDL SatPass Notification
Automated notification system that notify bright artificial objects expected in 10 days and write iCalendar format(.ics) file for Kyushu University Hanada Lab Pegasus Observatory.<br>
Data provided by [heavens-above](https://heavens-above.com), [Meteoblue](https://www.meteoblue.com) and SatPhotometry Library.

## Usage
### iCalendar Subscription
**usage** :<br>
Subscribe [this URL](https://github.com/kiyo-astro/SSDL-SatPass-Notification/raw/refs/heads/main/output/heavens-above/SatPass.ics) at calendar App.<br>
Please set auto refresh frequency of your calendar subscription **LESS OFTEN than every 30 mins**.<br>
<br>
Also, you can manually download .ics file from [here](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/output/heavens-above/SatPass.ics).<br>
<br>
**update frequency** :<br>
Orbital information is updated every 1 hour at the top of the hour, and weather information is updated daily at 00:00 UTC.<br>
Note : Update frequency and timing are currently controlled by [cron-job](cron-job.org).<br>
<br>
iCalendar update follows GitHub Actions workflow [SSDL-SatPass-Notification-hourly.yml](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/.github/workflows/SSDL-SatPass-Notification-hourly.yml)

### Slack Notification
**update frequency** :<br>
Slack notification is sent weekly at 22:00 UTC on Sunday (07:00 JST on Monday).<br>
Note : Update frequency and timing are currently controlled by [cron-job](cron-job.org).<br>
<br>
Slack Notification follows GitHub Actions workflow [SSDL-SatPass-Notification-weekly.yml](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/.github/workflows/SSDL-SatPass-Notification-weekly.yml)

## Management
### Overview
[cron-job](cron-job.org) => [GitHub Actions workflow](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/.github/workflows) => [SSDL-SatPass-Notification.py](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/SSDL-SatPass-Notification.py) => Slack App (SSDL SatPass Notification System)

1. [cron-job](cron-job.org) sets running schedule of GitHub Actions workflow<br>
1. [GitHub Actions](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/.github/workflows) runs [Python script](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/SSDL-SatPass-Notification.py)<br>
1. [SSDL-SatPass-Notification.py](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/SSDL-SatPass-Notification.py) retrive data from [heavens-above](https://heavens-above.com) and [Meteoblue](https://www.meteoblue.com), make [iCalendar format file](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/output/heavens-above/SatPass.ics) and send notice to Slack via Slack API.

### Schedule settings
Due to unacceptable delay of the GitHub Actions native scheduler (written in workflow files), running frequency and timing are now controlled by [cron-job](cron-job.org) via GitHub PAT.
Only the repository owner can change these settings. Therefore, in the future, this repository should ideally be managed by an organization rather than an individual developer.<br>
For further information about cron-job, please refer to [this useful article (in Japansese)](https://zenn.dev/ytkdm/articles/github-actions-cron-unreliable).

### Notice contents settings
the repository contributers can change some settings about notice contents at [workflow files](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/.github/workflows).

- Hourly iCalendar update : Edit [SSDL-SatPass-Notification-hourly.yml](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/.github/workflows/SSDL-SatPass-Notification-hourly.yml)
- Weekly Slack notice : Edit [SSDL-SatPass-Notification-weekly.yml](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/.github/workflows/SSDL-SatPass-Notification-weekly.yml)

Contributers can change `SLACK_CHANNEL`,`SEND_NOTICE`,`METEOBLUE_UPDATE`,`NOTIFY_TYPE`,`TIME_WINDOW`,`MIN_ALT`,`MIN_DURATION` <br>
ONLY owner can change `SLACK_TOKEN` and `METEOBLUE_API_KEY` from Repository Settings > Secrets and variables > Actions > Repository secrets<br>
<br>
**Caution : DO NOT HARDCODE ANY API KEYS** (`SLACK_TOKEN` and `METEOBLUE_API_KEY`) **on workflow files!** The workflow files are in public!

### Parameters
**SLACK_CHANNEL** :<br>
Slack channel ID.<br>
Note that Slack channel ID is displayed at the bottom of Channel settings on the desktop Slack App.<br>
<br>
**SEND_NOTICE** :<br>
`SEND` | `NOT` : Send notice to Slack or not.<br>
<br>
**METEOBLUE_UPDATE** :<br>
`FORCE` | `DAY` : Force Meteoblue update at every run, or update once a day.<br>
The option `DAY` is highly recommended because the number of free calls of Meteoblue API is strictly limited (about 400 times per year).<br>
<br>
**NOTIFY_TYPE** :<br>
`bydate` | `bysat` : Slack notification type.
- `bydate` : Satellite passes is displayed by date (recommended)
- `bysat` : Satellite passes is displayed by satellites


**TIME_WINDOW** :<br>
`evening` | `morning` | `all` : Observation time window.
- `evening` : ONLY visible satellite passes in evening are notified
- `morning` : ONLY visible satellite passes in morning are notified
- `all` : All visible satellite passes in evening are notified


**MIN_ALT** :<br>
Minimum highest-altitude [deg] of visible satellite passes. Value must be integer greater than 10 and less than 90.<br>
<br>
**MIN_DURATION** :<br>
Minimum duration [sec] of visible satellite passes. Value must be integer greater than 0.<br>
<br>
**SLACK_TOKEN** :<br>
Slack API token.<br>
Note that this value is saved as Secrets of this repository and can be changed ONLY by the repository owner.<br>
For security reason, **DO NOT HARDCODE THIS VALUE ON WORKFLOW FILES!** <br>
<br>
**METEOBLUE_API_KEY** :<br>
Meteoblue API key.<br>
Note that this value is saved as Secrets of this repository and can be changed ONLY by the repository owner.<br>
For security reason, **DO NOT HARDCODE THIS VALUE ON WORKFLOW FILES!** <br>
<br>

## Author
(c) 2026 **Kiyoaki Okudaira**<br>
Kyushu University Hanada Lab (SSDL)
