E-Puck Robot
============

Připojení
---------

1. Je třeba mít nainstalované: bluez-firmware bluez-utils (bluez-pin nebo něco
   jiného co se zeptá na heslo, např bluez-gnome a jeho bluetooth-applet)

2. Zjištění adresy robota:

        # hcitool scan

3. Nastavení sériového portu /etc/bluetooth/rfcomm.conf:
    
        rfcomm0 {
            bind yes;
            device 08:00:17:2C:E0:88; # Dopsat vlastní adresu
            channel 1;
            comment "e-puck_0006";    # Vlastní komentář
        }

4. Vlastní připojení:

        # rfcomm bind rfcomm0
        # rfcomm connect rfcomm0

    Po druhém příkazu by se mělo něco zeptat na heslo, to je stejné s číslem
    robota (je na něm napsané). 
 
    Možné chyby: 

    * _Can't connect RFCOMM socket: Connection refused_

        Nejspíše neběží žádná aplikace, která by se na heslo zeptala. Je třeba spustit např.
        bluetooth-applet.
    * _Can't create RFCOMM TTY: Address already in use_

        Možná příčína je už připojené zařízení. Buď už běží rfcomm, anebo si
        někdo robota přivlastnil. Občas pomůže:

            # rfcomm release rfcomm0
            # rfcomm connect rfcomm0

