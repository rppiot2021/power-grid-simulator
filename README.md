# power-grid-simulator

setup
------

    python3 -m venv venv

    source venv/bin/activate

    pip install -r requirements.pip.txt


starting simulator
------


    python3 simulator/main.py



*IEC 60870-5-104* protocol
------

*IEC 104* is industrial communication protocol which is being used in
energetics for communication with field devices.  It is one of many protocols
that are being used for this purpose.

Affiliate links for connecting to simulator using Hat-core iec wrapper
implementation:

[IEC 60870-5-104 Hat-core implementation](https://core.hat-open.com/docs/libraries/drivers/iec104.html)  
[IEC 60870-5-104 Hat-core documentation](https://core.hat-open.com/docs/pyhat/hat/drivers/iec104/index.html)

This repository contains simulator and adapter.

Simulator generates values for small electrical scheme. Generated values change
periodically and can be changed by users action.

Simulator can be started with:

    .../simulator python3 main.py


Adapter is component that communicates with simulator and acts a abstraction
level. It communicates with simulator using protocol iec-104. Also, It can
forward values from simulator using one of the following protocols:

    http
    tcp
    websocket

Adapter can be started with:
    
    .../adapter python3 main.py -p {http/tcp/ws}


