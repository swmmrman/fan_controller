import dht
import machine
import time
import ntptime
import network
import urequests
import socket
import _thread
import gc
import micropython
import diags

## Setup global variables
reedpin = 15
relay_pin = 14
tzoffset = -21600

class temp:
    def __init__(self):
        self.min = 255
        self.max = -200
        self.cur = -200

    def update(self, temp):
        self.cur = temp
        if self.min > temp:
            self.min = temp

        if self.max < temp:
            self.max = temp

    def get_cur(self):
        return self.cur

    def get_max(self):
        return self.max
    
    def get_min(self):
        return self.min
        
class readings:
    def __init__(self):
        self.temps = {
            '1': temp(),
            '2': temp()
        }
    
    def update(self, temp, id):
        self.temps[id].update(temp)
    
    def get(self, id):
        return self.temps[id].get_cur()
    
    def get_min(self, id):
        return self.temps[id].get_min()
    
    def get_max(self, id):
        return self.temps[id].get_max()


class counter:
    def __init__(self):
        self.count = 0

    def get(self):
        cur = self.count
        self.count += 1
        return(cur)
        

temps = readings()
count = counter()
#Setup sensors/relays/wifi
relay = machine.Pin(relay_pin, mode=machine.Pin.OUT)
reedswitch = machine.Pin(reedpin, mode=machine.Pin.IN, pull=machine.Pin.PULL_UP)
sensor_1 = dht.DHT22(machine.Pin(0, mode=machine.Pin.IN))
sensor_2 = dht.DHT22(machine.Pin(1, mode=machine.Pin.IN))
wlan = network.WLAN(network.STA_IF)
wlan.active(True)


def sync_time():
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


def temp_loop():
    s = socket.socket()
    s.bind(('0.0.0.0', 80))
    s.listen(1)
    while True:
        diags.re(s, temps, count)

def temp_update(isr):
    sensor_1.measure()
    sensor_2.measure()
    temps.update( sensor_1.temperature() * 1.8 + 32, '1')
    temps.update( sensor_2.temperature() * 1.8 + 32, '2')

def test_relay(relay):
    relay.on()
    time.sleep(5)
    relay.off()


def watcher(isr):
    #Grounded(0) if hatch closed
    if reedswitch.value() == 0:
        resp = urequests.get('http://192.168.1.134/fan_call.txt')
        if resp.text == "on":
            relay.on()
        else:
            relay.off()
    else:
        relay.off()


def connect_wifi(wlan):
    import wifi
    #Connect wifi to network.
    wlan.connect(wifi.ssid, wifi.password)
    times_nc = 0
    while wlan.status() != 3:
        print(f"\rNo wifi, {times_nc} seconds", end="")
        time.sleep(1)
        times_nc = times_nc + 1
    else:
        print()


test_relay(relay)
connect_wifi(wlan)
sync_time()
tt = time.localtime(time.time() + tzoffset)
ts = f"[{tt[0]}-{tt[1]:02}-{tt[2]} {tt[3]:02}:{tt[4]:02}:{tt[5]:02}]"
print(f"\r\n{ts} Wifi connected: {wlan.ifconfig()[0]}")

_thread.start_new_thread(temp_loop, ())

tmr = machine.Timer()
tmr.init(mode=tmr.PERIODIC, period=1010, callback=temp_update)
tmr2 = machine.Timer()
tmr2.init(mode=tmr2.PERIODIC, period=500, callback=watcher)