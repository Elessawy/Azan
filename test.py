import soco as soco

sonos = soco.discovery.any_soco()

sonos.volume = 60

audio_url = "https://www.islamcan.com/audio/adhan/azan12.mp3"
sonos.play_uri(audio_url)