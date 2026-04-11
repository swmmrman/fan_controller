import machine
import time
import network
import urequests
import wifi

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(wifi.ssid, wifi.password)

while wlan.status() != 3:
    print("\rNo wifi", end="")
    time.sleep(1)

print(f"\rWifi connected: {wlan.ifconfig()}")

while True:
    resp = urequests.get('http://192.168.1.134/temp_in.txt')
    print(f"\r{resp.text}", end="")
    time.sleep(1)
 