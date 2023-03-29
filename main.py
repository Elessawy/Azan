import requests
import time
import datetime
import soco as soco
from soco.alarms import Alarms, Alarm
import os

# Set up the Sonos speaker
sonos = soco.discovery.any_soco()

# Prayers to notify
my_prayers = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
# my_prayers = ['Dhuhr', 'Asr', 'Maghrib', 'Isha']

# Mawaqit attrs > Blauwe Mosque
mosque_name = 'Blauwe'
mosque_uuid = '51d36aff-f636-48f0-8961-f279eabc2d22'

# Azan url
azan_url = "https://www.islamcan.com/audio/adhan/azan12.mp3"
dir_path = "/Users/abdelrahmanelessawy/PycharmProjects/Azan"


def load_prayer_times_from_mawaqit():
    url = 'https://mawaqit.net/api/2.0/mosque/search?word=' + mosque_name
    response = requests.get(url).json()

    for mosque in response:
        if mosque['uuid'] == mosque_uuid:
            return {
                'Fajr': mosque['times'][0],
                'Sunrise': mosque['times'][1],
                'Dhuhr': mosque['times'][2],
                'Asr': mosque['times'][3],
                'Maghrib': mosque['times'][4],
                'Isha': mosque['times'][5],
            }
    return {}


def load_prayer_times_from_aladhan_api():
    # Get the prayer times from the IslamicFinder API
    url = "http://api.aladhan.com/v1/timingsByCity"
    params = {
        "city": "Amsterdam",
        "country": "NL",
        "method": 2,  # Islamic Society of North America (ISNA) method
        "school": 0,  # Hanafi school
    }
    response = requests.get(url, params=params).json()
    return response["data"]["timings"]


def load_prayer_times():
    prayer_times = load_prayer_times_from_mawaqit()
    if not prayer_times:
        log("No results from Mawaqit, try aladhan API")
        prayer_times = load_prayer_times_from_aladhan_api()

    return convert_to_timestamp_and_filter(prayer_times)


def convert_to_timestamp_and_filter(prayer_times):
    # Convert prayer times to Unix timestamps
    today_str = time.strftime("%Y-%m-%d")
    prayer_timestamps = {}
    for prayer_name, prayer_time in prayer_times.items():
        if prayer_name in my_prayers:
            prayer_datetime_str = today_str + " " + prayer_time
            prayer_datetime = time.strptime(prayer_datetime_str, "%Y-%m-%d %H:%M")
            prayer_timestamps[prayer_name.lower()] = time.mktime(prayer_datetime)
    return prayer_timestamps


# Play the Azan on Sonos speaker
def play_azan(prayer_name):
    sonos.pause()
    time.sleep(2)
    sonos.volume = 15
    sonos.play_uri(azan_url)
    log(f"Playing {prayer_name} Azan")


def log(text):
    today = datetime.date.today().strftime("%Y-%m-%d")
    with open(f"{dir_path}/log/{today}.txt", 'a') as f:
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        f.write(f"[{dt_string}]:{text}.\n")
        f.close()
    print(text)


def clear_log_files():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=3)  # not yesterday, keep 3 days
    yesterday_str = yesterday.strftime("%Y-%m-%d")
    old_log_file_path = f"{dir_path}/log/{yesterday_str}.txt"
    if os.path.exists(old_log_file_path):
        os.remove(old_log_file_path)

    main_log_file_path = f"{dir_path}/log/file.log"
    if os.path.exists(main_log_file_path):
        os.remove(main_log_file_path)

    error_log_file_path = f"{dir_path}/log/file-error.log"
    if os.path.exists(error_log_file_path):
        os.remove(error_log_file_path)

    yesterday_done_file_path = f"{dir_path}/log/done-{yesterday_str}.txt"
    if os.path.exists(yesterday_done_file_path):
        os.remove(yesterday_done_file_path)


def get_next_prayer(prayer_timestamps):
    current_time = time.time()
    for prayer_name, prayer_timestamp in prayer_timestamps.items():
        if current_time >= prayer_timestamp:
            return prayer_name
    return ''


def run():
    log("Loading prayer times..")
    prayer_timestamps = load_prayer_times()
    log(f"Prayer times loaded, prayers={prayer_timestamps}")

    while True:

        # if map is empty (all prayers are consumed), break to load again
        if not prayer_timestamps:
            log("Prayer map is empty, goodbye!!")
            break

        cur_prayer_name = get_next_prayer(prayer_timestamps)

        if cur_prayer_name != '':
            cur_time = time.time()
            cur_prayer_time = prayer_timestamps[cur_prayer_name]

            if cur_time - cur_prayer_time >= 900:
                log(f"Prayer {cur_prayer_name} is too late, will not play Azan!")
            else:
                log(f"Start play azan for prayer {cur_prayer_name}, with time={cur_prayer_time}, current={cur_time}")
                play_azan(cur_prayer_name)
                time.sleep(1800)  # cool down for 30 mins

            del prayer_timestamps[cur_prayer_name]
            log(f"Prayer {cur_prayer_name} is removed from prayer map!")


def clear_all_alarms():
    alarms = Alarms()
    alarms.update()
    for alarm in alarms:
        alarm.remove()


def set_alarm(timestamp, volume):
    alarm = Alarm(sonos)

    # Set the alarm parameters
    alarm.volume = volume
    # alarm.duration =  time.
    alarm.start_time = datetime.datetime.fromtimestamp(timestamp).time()
    alarm.enabled = True
    alarm.play_mode = "SHUFFLE_NOREPEAT"
    alarm.recurrence = "ONCE"
    alarm.program_uri = azan_url

    alarm.save()


def get_done_file_path():
    today = datetime.date.today().strftime("%Y-%m-%d")
    return f"{dir_path}/log/done-{today}.txt"


def already_done_successfully_today():
    return os.path.exists(get_done_file_path())


def create_done_today_file():
    with open(get_done_file_path(), 'a') as f:
        f.write("DONE!")
        f.close()


def run_by_alarm():
    # if already_done_successfully_today():
    #     return

    log("Loading prayer times..")
    prayer_timestamps = load_prayer_times()
    log(f"Prayer times loaded, prayers={prayer_timestamps}")

    clear_all_alarms()

    for prayer_name, prayer_timestamp in prayer_timestamps.items():
        log(f"Set alarm from prayer {prayer_name}")
        if prayer_name == 'Fajr':
            set_alarm(prayer_timestamp, 5)
        else:
            set_alarm(prayer_timestamp, 20)

    create_done_today_file()


clear_log_files()

run_by_alarm()

# run()
