import dht
import machine
import time
import ntptime
import network
import urequests
import socket
import _thread

## Setup global variables
relay_pin = 14
tzoffset = -21600

#Setup sensors/relays/wifi
relay = machine.Pin(relay_pin, machine.Pin.OUT)
sensor_1 = dht.DHT22(machine.Pin(0, machine.Pin.IN))
sensor_2 = dht.DHT11(machine.Pin(1, machine.Pin.IN))
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
    temp_1 = 0.0
    temp_2 = 0.0
    last_update = time.time()
    while True:
        try:
            sock , addr = s.accept()
            print(f"Connection from: {addr}")
            request = sock.recv(1024)
            # print(time.time() - last_update)
            if  time.time() - last_update >= 3:
                last_update = time.time()
                sensor_1.measure()
                temp_1 = sensor_1.temperature() * 1.8 + 32
                sensor_2.measure()
                temp_2 = sensor_2.temperature() * 1.8 + 32
                print(f"\rTemp 1: {temp_1: 4.2f}f\tTemp 2: {temp_2: 4.2f}f", end="")
            sock.send('http/1.1 200 OK\r\nContent-type: text/html\r\n\r\n')
            sock.send(f"Temp 1:{temp_1: 4.2f} Temp 2:{temp_2: 4.2f}")
            sock.close()
        except OSError:
            print("No connect")
            sock.close()


            




def test_relay(relay):
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

_thread.start_new_thread(watcher, ())
temp_loop()