import dht
import machine
import time
import ntptime
import network
import urequests
import wifi
import socket
import _thread


relay_pin = 14
tzoffset = -21600
sensor_1 = dht.DHT22(machine.Pin(0, machine.Pin.IN))
sensor_2 = dht.DHT11(machine.Pin(1, machine.Pin.IN))

def temp_loop():
    while True:
        time.sleep(2)
        sensor_1.measure()
        temp_1 = sensor_1.temperature() * 1.8 + 32
        sensor_2.measure()
        temp_2 = sensor_2.temperature() * 1.8 + 32
        print(f"\rTemp 1: {temp_1: 4.2f}f\tTemp 2: {temp_2: 4.2f}f", end="")


def test_relay():
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


wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi.ssid, wifi.password)

test_relay()

times_nc = 0
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
    else:
        time_not_set = False


tt = time.localtime(time.time() + tzoffset)
ts = f"[{tt[0]}-{tt[1]:02}-{tt[2]} {tt[3]:02}:{tt[4]:02}:{tt[5]:02}]"
print(f"\r\n{ts} Wifi connected: {wlan.ifconfig()[0]}")

_thread.start_new_thread(watcher, ())
temp_loop()