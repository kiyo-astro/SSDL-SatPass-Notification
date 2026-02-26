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
[cron-job](cron-job.org) => [GitHub Actions workflow](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/.github/workflows) => [SSDL-SatPass-Notification.py](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/SSDL-SatPass-Notification.py) => Slack App (SSDL SatPass Notification System)<br>
<br>
1. [cron-job](cron-job.org) sets running schedule of GitHub Actions workflow<br>
1. [GitHub Actions](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/.github/workflows) runs [Python script](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/SSDL-SatPass-Notification.py)<br>
1. [SSDL-SatPass-Notification.py](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/SSDL-SatPass-Notification.py) retrive data from [heavens-above](https://heavens-above.com) and [Meteoblue](https://www.meteoblue.com), make [iCalendar format file](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/output/heavens-above/SatPass.ics) and send notice to Slack via Slack API.

### Schedule settings
Due to unacceptable delay of the GitHub Actions native scheduler (written in workflow files), running frequency and timing are now controlled by [cron-job](cron-job.org) via GitHub PAT.<br>
Only the repository owner can change these settings. Therefore, in the future, this repository should ideally be managed by an organization rather than an individual developer.<br>
For further information about cron-job, please refer to [this useful article (in Japansese)](https://zenn.dev/ytkdm/articles/github-actions-cron-unreliable).

### Notice contents settings
the repository contributers can change some settings about notice contents at [workflow files](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/.github/workflows).<br>
- Hourly iCalendar update : Edit [SSDL-SatPass-Notification-hourly.yml](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/.github/workflows/SSDL-SatPass-Notification-hourly.yml)
- Weekly Slack notice : Edit [SSDL-SatPass-Notification-weekly.yml](https://github.com/kiyo-astro/SSDL-SatPass-Notification/blob/main/.github/workflows/SSDL-SatPass-Notification-weekly.yml)
<br>
Contributers can change `SLACK_CHANNEL`,`SEND_NOTICE`,`METEOBLUE_UPDATE`,`NOTIFY_TYPE`,`TIME_WINDOW`,`MIN_ALT`,`MIN_DURATION`<br>
ONLY owner can change `SLACK_TOKEN` and `METEOBLUE_API_KEY` from Repository Settings > Secrets and variables > Actions > Repository secrets<br>
<br>
**Caution : DO NOT HARDCODE ANY API KEYS** (`SLACK_TOKEN` and `METEOBLUE_API_KEY`) **on workflow files!** The workflow files are in public!<br>
<br>
#### Parameters

## Author
(c) 2026 **Kiyoaki Okudaira**<br>
Kyushu University Hanada Lab (SSDL)
