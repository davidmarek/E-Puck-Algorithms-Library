E-Puck
======

Vytvoření spojení s robotem
---------------------------

1. Je třeba mít nainstalované: ``bluez-firmware``, ``bluez-utils``,
   ``bluez-pin`` nebo jiný program pro spravování hesel, např ``bluez-gnome`` a
   jeho ``bluetooth-applet``.

2. Zjištění adresy robota::

    $ hcitool scan
    Scanning ...
        10:00:E8:52:C6:3E	e-puck_1055

3. Nastavení sériového portu ``/etc/bluetooth/rfcomm.conf``::

    rfcomm0 {
        bind yes;
        device 10:00:E8:52:C6:3E; # Adresa zařízení
        channel 1;
        comment "e-puck_1055";    # Vlastní komentář
    }

4. Vlastní připojení::

    $ sudo rfcomm connect rfcomm0
    Connected /dev/rfcomm0 to 10:00:E8:52:C6:3E on channel 1
    Press CTRL-C for hangup

   Po tomto příkazu by se měla nějaká služba zeptat na PIN heslo. Číslo je
   napsáno na horní straně robota.

   Možné chyby:
    *Can't connect RFCOMM socket: Connection refused*
        Nejspíše neběží žádná aplikace, která by se na heslo zeptala. Je třeba
        spustit např. ``bluetooth-applet``.
    *Can't open RFCOMM device: Permission denied*
        Uživatel nemůže přistupovat k zařízení ``/dev/rfcomm0``.
    *Can't create RFCOMM TTY: Address already in use*
        Možná příčina je už připojené zařízení. Buď už běží ``rfcomm``, anebo
        jiná aplikace, která s robotem udržuje komunikaci. Řešením je zavřít
        aplikace komunikující s robotem, popř. zkusit následující příkazy::

            $ rfcomm release rfcomm0
            $ rfcomm connect rfcomm0

5. Pokud se robot chová podivně (např. nereaguje na nějaké příkazy) tak je to
   nejspíše tím, že mu dochází baterie. V poslední verzi BTcom robot dá vědět,
   že mu dochází baterie, rozsvícením všech LED.

Instalace firmware BTcomDM
--------------------------

Knihovna komunikuje s E-puck robotem pomocí posílání textových příkazů. Je
třeba do robota nahrát firmware BTcomDM. Ten je dodáván s knihovnou.

K jejímu nahrání stačí použít `epuckupload
<http://svn.gna.org/viewcvs/e-puck/trunk/tool/bootloader/computer_side/multi_platform/>`_.
Stačí se řídit pomocí ``README`` a na E-puck nahrát soubor ``BTcomDM.hex``.
Příklad použití::

    $ epuckupload -f BTcomDM.hex rfcomm0

Po spuštění příkazu je třeba robota restartovat (modré tlačítko na horní
straně). Teprve pak se začne nahrávat nový firmware.

Instalace knihovny
------------------

Knihovna je ke stáhnutí na `stránkách
projektu <http://atrey.karlin.mff.cuni.cz/~davidm/epuck-0.9.1.tar.gz>`_.
Podporuje standardní instalaci, takže je možné ji nainstalovat pomocí skriptu
``setup.py``::

    $ wget http://atrey.karlin.mff.cuni.cz/~davidm/epuck-0.9.1.tar.gz
    $ tar -xvf epuck-0.9.1.tar.gz
    $ cd epuck-0.9.1/
    $ sudo python setup.py install

Také je možné ji nainstalovat z webového repositáře `PyPI (Python Package
Index) <http://pypi.python.org>`_ pomocí programu ``easy_install``::

    $ easy_install epuck


Příklad
-------
::

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    """Go forward, stop in front of an obstacle."""

    import time

    from epuck import Controller

    # Input larger than the threshold means there is an obstacle.
    threshold = 300

    # Create the controller. Robot is connected to /dev/rfcomm2 and the
    # communication will be asynchronous.
    controller = Controller('/dev/rfcomm0', asynchronous=True)

    # Set the speed of left and right wheel to 100.
    controller.set_speed(100, 100)

    # Ask for the values of proximity sensors
    sensor_request = controller.get_proximity_sensors()
    # Wait until the robot returns them.
    sensor_values = sensor_request.get_response()

    # Continue while there is nothing in front of the front left and front right sensor.
    while (sensor_values['L10'] < threshold) and (sensor_values['R10'] < threshold):
        # Wait for a while
        time.sleep(0.1)
        # Read new values
        sensor_request = controller.get_proximity_sensors()
        sensor_values = sensor_request.get_response()

    # Stop the robot
    controller.set_speed(0, 0)
