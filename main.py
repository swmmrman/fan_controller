import machine
import time
import network
import urequests
import wifi

relay_pin = 14

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi.ssid, wifi.password)


time_nc = 0
while wlan.status() != 3:
    print(f"\rNo wifi, {time_nc} seconds", end="")
    time.sleep(1)
    time_nc = time_nc + 1

print(f"\r\nWifi connected: {wlan.ifconfig()}")

relay = machine.Pin(relay_pin, machine.Pin.OUT)
relay.on()
time.sleep(5)
relay.off()


while True:
    resp = urequests.get('http://192.168.1.134/temp_in.txt')
    print(f"\r{resp.text}", end="")
    time.sleep(1)
 