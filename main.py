import machine
import time
import ntptime
import network
import urequests
import wifi
import _thread


relay_pin = 14
tzoffset = -21600

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi.ssid, wifi.password)


time_nc = 0
while wlan.status() != 3:
    print(f"\rNo wifi, {time_nc} seconds", end="")
    time.sleep(1)
    time_nc = time_nc + 1
else:
    print()


time_not_set = True
fails = 0

while time_not_set:
    try:
        ntptime.settime()
    except OSError:
        fails = fails + 1
        print(f"\rFails: {fails}", end="")
        time.sleep(1)
        continue
    finally:
        time_not_set = False


tt = time.localtime(time.time() + tzoffset)
ts = f"[{tt[0]}-{tt[1]:02}-{tt[2]} {tt[3]}:{tt[4]}:{tt[5]}]"
print(f"\r\n{ts} Wifi connected: {wlan.ifconfig()[0]}")


relay = machine.Pin(relay_pin, machine.Pin.OUT)
relay.on()
time.sleep(5)
relay.off()

def watcher():
    while True:
        resp = urequests.get('http://192.168.1.134/fan_call.txt')
        if int(resp.text):
            relay.on()
        else:
            relay.off()
        time.sleep(5)


_thread.start_new_thread(watcher, ())