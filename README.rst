E-Puck
======

Vytvoření spojení s robotem
---------------------------

1. Je třeba mít nainstalované: ``bluez-firmware`` ``bluez-utils`` (``bluez-pin`` nebo něco
   jiného co se zeptá na heslo, např ``bluez-gnome`` a jeho ``bluetooth-applet``)

2. Zjištění adresy robota::

    $ hcitool scan

3. Nastavení sériového portu ``/etc/bluetooth/rfcomm.conf``::

    rfcomm0 {
        bind yes;
        device 08:00:17:2C:E0:88; # Adresa z hcitool
        channel 1;
        comment "e-puck_0006";    # Komentář
    }

4. Vlastní připojení::

    $ rfcomm connect rfcomm0

   Po tomto příkazu by se měla nějaká služba zeptat na PIN heslo. Číslo je
   napsáno na horní straně robota.

   Možné chyby:

    *Can't connect RFCOMM socket: Connection refused*
        Nejspíše neběží žádná aplikace, která by se na heslo zeptala. Je třeba spustit např.
        bluetooth-applet.

    *Can't create RFCOMM TTY: Address already in use*
        Možná příčína je už připojené zařízení, anebo existuje aplikace, která
        má stále otevřené spojení s robotem. Řešením je ukončit aplikace, které
        s robotem komunikují, případně následující příkazy::

        $ rfcomm release rfcomm0
        $ rfcomm connect rfcomm0

5. Pokud se robot chová podivně (např. nereaguje na nějaké příkazy) tak je to
   nejspíše tím, že mu dochází baterie. V poslední verzi BTcom robot dá vědět,
   že mu dochází baterie, rozsvícením všech LED.

Instalace firmware
------------------

Knihovna komunikuje s E-puck robotem pomocí posílání textových příkazů. Je
třeba do robota nahrát upravenou verzi firmware BTcom. Ta je dodávána s
knihovnou.

K jejímu nahrání stačí použít `epuckupload
<http://svn.gna.org/viewcvs/e-puck/trunk/tool/bootloader/computer_side/multi_platform/>`_.
Stačí se řídit pomocí ``README`` a na E-puck nahrát soubor ``BTcom.hex``.
Příklad použití::

    $ epuckupload -f BTcom.hex rfcomm0

Po spuštění příkazu je třeba robota restartovat (modré tlačítko na horní
straně). Teprve pak se začne nahrávat nový firmware.

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
    controller = Controller('/dev/rfcomm2', asynchronous=True)

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
