import network
import time
from machine import Pin
import onewire, ds18x20
try:
    import usocket as socket
except:
    import socket

print('Http webserver startup code')
pin = Pin(2, Pin.OUT)
pin.value(1)

led = Pin(14, Pin.OUT)
led.off()

# the device is on GPIO12
dat = Pin(12)

# create the onewire object
ds = ds18x20.DS18X20(onewire.OneWire(dat))

# scan for devices on the bus
roms = ds.scan()
print('Found 1-wire devices:', roms)


sta_if = network.WLAN(network.STA_IF)
if not sta_if.isconnected():
    print('connecting to network...')
    sta_if.active(True)
    sta_if.connect('Bubuka', 'gyroshusisalival2016')
    while not sta_if.isconnected():
        pin.value(0)
        time.sleep(0.1)
        pin.value(1)
        time.sleep(0.1)
    pin.value(1)
print('network config:', sta_if.ifconfig())

f = open('index.html','r')
CONTENT = b"""\
HTTP/1.0 200 OK
Content-Type: text/html
Connection: Closed

""" + f.read()
f.close()

def main(micropython_optimize=True):
    global temp
    s = socket.socket()

    # Binding to all interfaces - server will be accessible to other hosts!
    ai = socket.getaddrinfo("0.0.0.0", 8080)
    print("Bind address info:", ai)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(5)
    pin.value(0)
    print("Listening, connect your browser to http://<this_host>:8080/")

    counter = 0
    while True:
        res = s.accept()
        client_sock = res[0]
        client_addr = res[1]
        print("Client address:", client_addr)
        print("Client socket:", client_sock)

        if not micropython_optimize:
            # To read line-oriented protocol (like HTTP) from a socket (and
            # avoid short read problem), it must be wrapped in a stream (aka
            # file-like) object. That's how you do it in CPython:
            client_stream = client_sock.makefile("rwb")
        else:
            # .. but MicroPython socket objects support stream interface
            # directly, so calling .makefile() method is not required. If
            # you develop application which will run only on MicroPython,
            # especially on a resource-constrained embedded device, you
            # may take this shortcut to save resources.
            client_stream = client_sock

        print("Request:")
        pin.value(1)
        time.sleep(0.2)
        pin.value(0)
        time.sleep(0.1)
        pin.value(1)
        time.sleep(0.2)
        pin.value(0)
        req = client_stream.readline()
        print(req)
        while True:
            h = client_stream.readline()
            if h == b"" or h == b"\r\n":
                break
            print(h)
        ledOn = req.decode('utf-8').find('ledON')
        ledOff = req.decode('utf-8').find('ledOFF')
        if ledOn > 0:
            led.on()
        if ledOff > 0:
            led.off()
        ds.convert_temp()
        time.sleep_ms(750)
        temp = 0
        for rom in roms:
            temp = ds.read_temp(rom)
        client_stream.write(CONTENT % temp)

        client_stream.close()
        if not micropython_optimize:
            client_sock.close()
        counter += 1
        print()


main()