import gc
import micropython
import machine
import socket
import time

def re(s, temps, count):
    sock, addr = s.accept()
    req = sock.recv(2048)
    request = req.decode('utf8').split()
    path = request[1]
    if path == "/favicon.ico":
        sock.send("HTTP/1.1 404 Not Found\r\nContent-type: text/plain\r\n\r\n")
        sock.send("Not Found\r\n\r\n")
        sock.close()
        return
    elif path == "/reset":
        machine.reset()
    else:
        header = "HTTP/1.1 200 OK\r\nContent-type: text/plain\r\n\r\n"
        free_mem = gc.mem_free()
        gc_status = gc.isenabled()
        lt = time.localtime(time.time()-21600)
        t = "{: 2}:{:02}:{:02} {}-{:02}-{:02}".format(lt[3],lt[4],lt[5],lt[0],lt[1],lt[2])
        sock.send(f"{header}Your IP:{addr[0]}\r\nFree Memory: {free_mem:,}\r\nGC Enanbled: {gc_status}\r\n")
        sock.send(f"Current Time:{t}\r\nCount: {count.get():,}\r\nCurrent Temps\r\n")
        sock.send(f"Sensor 1:{temps.get('1'): 5.2f}f\t Max: {temps.get_max('1'): 5.2f}f\tMin: {temps.get_min('1'): 5.2f}\r\n")
        sock.send(f"Sensor 2:{temps.get('2'): 5.2f}f\t Max: {temps.get_max('2'): 5.2f}f\tMin: {temps.get_min('2'): 5.2f}\r\n")
        sock.send("\r\n")
        sock.close()