import time

from soco.alarms import Alarms, Alarm, get_alarms, remove_alarm_by_id, parse_alarm_payload
from soco import SoCo

import soco
from soco import services

my_device = soco.SoCo('192.168.178.150')  # <---- insert IP of one of your zones
ac = services.AlarmClock(my_device)
# Print out all the available actions
# for i in ac.iter_actions():
#     print(i)

# print(ac.ListAlarms())
# ac.DestroyAlarm(ID=15)
# print(ac.ListAlarms())


# # create a SoCo instance for your Sonos speaker
# sonos = SoCo('192.168.178.150')
#
# sonos.alarmClock
#
# # create an instance of the Alarms class
# alarms = Alarms()
#
# print(alarms.alarms)

# alarm = Alarm(soco)


# get_alarms(my_device)

alarms = Alarms()
alarms.update()
print(alarms.alarms)
alarms['20'].remove()
print(alarms.alarms)


# print(parse_alarm_payload("<Alarm id:21@18:00:00 at 0x1057f9f70>", my_device))
# time.sleep(2)
# remove_alarm_by_id(my_device, '18')
# time.sleep(2)
#
# print(get_alarms(my_device))


# alarm.alarm_id = 18

# # Set the alarm parameters
# alarm.volume = 30
# # alarm.duration = timedelta(minutes=120)
# alarm.start_time = time(9, 0, 0)
# alarm.enabled = True
# alarm.play_mode = "SHUFFLE_NOREPEAT"
# alarm.recurrence = "ONCE"
# alarm.program_uri = "http://www.sonos.com/howdy.mp3"
#
# # Save the alarm to the Sonos speaker
# alarm.save()

# print(alarm)

# alarm.remove()
