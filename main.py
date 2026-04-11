import machine
import time
import ntptime
import network
import urequests
import wifi

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

ntptime.settime()
tt = time.localtime(time.time() + tzoffset)
ts = f"{tt[0]}/{tt[1]}\{tt[2]} {tt[3]}:{tt[4]}:{tt[5]}"
print(f"\r\n{ts}Wifi connected: {wlan.ifconfig()}")


relay = machine.Pin(relay_pin, machine.Pin.OUT)
relay.on()
time.sleep(5)
relay.off()


while True:
    resp = urequests.get('http://192.168.1.134/fan_call.txt')
    if int(resp.text):
        relay.on()
    else:
        relay.off()
    time.sleep(5)
 