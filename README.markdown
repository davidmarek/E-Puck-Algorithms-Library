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

        # rfcomm connect rfcomm0

    Něco by se mělo zeptat na heslo, to je stejné s číslem robota (je na něm
    napsané).

    Možné chyby:

    * _Can't connect RFCOMM socket: Connection refused_

        Nejspíše neběží žádná aplikace, která by se na heslo zeptala. Je třeba spustit např.
        bluetooth-applet.
    * _Can't create RFCOMM TTY: Address already in use_

        Možná příčína je už připojené zařízení. Buď už běží rfcomm, anebo jiná
        aplikace, která komunikuje se zařízením někdo robota přivlastnil. Občas
        pomůže:

            # rfcomm release rfcomm0
            # rfcomm connect rfcomm0

5. Pokud se robot chová podivně (např. nereaguje na nějaké příkazy) tak je to
   nejspíše tím, že mu dochází baterka! Není dobré ladit kód na robotovi, který
   mele z posledního :-(

Instalace BTcom
---------------

Je potřeba mít robota připojeného k počítači. Pak stačí použít perlovský skript
[epuckupload](http://svn.gna.org/viewcvs/e-puck/trunk/tool/bootloader/computer_side/multi_platform/
"epuckupload"). Stačí se řídit instrukcemi v přiloženém README.

