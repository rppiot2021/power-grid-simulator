# power-grid-simulator

setup
------

    python3 -m venv venv

    source venv/bin/activate

    pip install -r requirements.pip.txt

    try:

        sudo apt-get install $(grep -vE "^\s*#" requirements.ubuntu.txt  | tr "\n" " ")

    except:

        sudo apt-get install binutils-mingw-w64-x86-64 clang doxygen gcc gcc-mingw-w64-x86-64 git graphviz libffi-dev libisoburn-dev libjansson-dev libuv1-dev libyaml-dev nodejs npm openssl pandoc plantuml python3 python3-pip samba socat sqlite3 unixodbc yarn

run all tests
todo


starting project
------


    python3 simulator/main.py



*IEC 60870-5-104* protocol
------

*IEC 104* is industrial communication protocol which is being used in energetics
for communication with field devices. 
It is one of many protocols that are being used for this purpose.

Affiliate links for connecting to simulator using Hat-core iec wrapper implementation:

[IEC 60870-5-104 Hat-core implementation](https://core.hat-open.com/docs/libraries/drivers/iec104.html)  
[IEC 60870-5-104 Hat-core documentation](https://core.hat-open.com/docs/pyhat/hat/drivers/iec104/index.html)


*IEC 104* je industrijski komunikacijski protokol koji se koristi u energetici
za komunikaciju s terenskim uređajima.  Jedan je od raznim protokola koji se
koriste za tu svrhu.   Vaš zadatak je da iskoristite implementaciju IEC 104
drivera iz  Hat-core repozitorija da bi ostvarili komunikaciju sa simulatorom.
Primjer korištenja drivera se nalazi na donjim linkovima.