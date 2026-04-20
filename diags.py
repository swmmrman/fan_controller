import gc
import micropython
import socket
import time

def re(s,mesg, temps):
    sock, addr = s.accept()
    req = sock.recv(2048)
    header = "http/1.1 200 OK\r\nContent-type: text/html\r\n\r\n"
    free_mem = gc.mem_free()
    gc_status = gc.isenabled()
    lt = time.localtime(time.time()-21600)
    t = "{: 2}:{:02}:{:02} {}-{:02}-{:02}".format(lt[3],lt[4],lt[5],lt[0],lt[1],lt[2])
    sock.send(f"{header}Your IP:{addr[0]}\r\nFree Memory: {free_mem:,}\r\nGC Enanbled: {gc_status}\r\n")
    sock.send(f"Current Time:{t}\r\n{mesg}\r\nCurrent Temps\r\nSensor 1:{temp_1: 4.2f}f\r\nSensor 2:{temp_2: 4.2f}f\r\n\r\n")
    sock.send("\r\n")
    sock.close()