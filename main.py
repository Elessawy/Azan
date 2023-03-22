import requests
import time
import datetime
import soco as soco

# Set up the Sonos speaker
sonos = soco.discovery.any_soco()

# Prayers to notify
# my_prayers = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']
my_prayers = ['Dhuhr', 'Asr', 'Maghrib', 'Isha']

# Mawaqit attrs > Blauwe Mosque
mosque_name = 'Blauwe'
mosque_uuid = '51d36aff-f636-48f0-8961-f279eabc2d22'

# Azan url
azan_url = "https://www.islamcan.com/audio/adhan/azan12.mp3"


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
    sonos.volume = 15
    sonos.play_uri(azan_url)
    log(f"Playing {prayer_name} Azan")


def log(text):
    today = datetime.date.today().strftime("%Y-%m-%d")
    with open(f"log/{today}.txt", 'a') as f:
        # Write new lines to the file
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        f.write(f"[{dt_string}]:{text}.\n")
        f.close()
    print(text)


def run():
    log("Load prayer times")
    prayer_timestamps = load_prayer_times()

    while True:

        # if map is empty (all prayers are consumed), break to load again
        if not prayer_timestamps:
            log("Prayer map is empty, goodbye!!")
            break

        current_time = time.time()
        current_prayer_name = ''

        for prayer_name, prayer_timestamp in prayer_timestamps.items():
            if current_time >= prayer_timestamp:
                current_prayer_name = prayer_name
                break

        if current_prayer_name != '':
            if current_time - prayer_timestamps[current_prayer_name] >= 600:
                log(f"Prayer {current_prayer_name} is too late, will not play Azan!")
            else:
                play_azan(current_prayer_name)
                time.sleep(1800)  # cool down for 30 mins

            del prayer_timestamps[current_prayer_name]
            log(f"Prayer {current_prayer_name} is removed from prayer map!")


run()
