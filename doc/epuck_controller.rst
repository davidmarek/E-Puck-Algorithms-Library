:mod:`epuck` --- Ovládání robota
================================

.. module:: epuck

Ovládání robota je velmi jednoduché a přímočaré. V první řadě je potřeba mít
robota již připojeného. Návod je k nalezení v sekci :ref:`vytvoreni-spojeni-s-robotem`.
Celá komunikace probíhá přes třídu :class:`Controller`.

Příklad::

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


Třída :class:`Controller`
-------------------------

.. class:: Controller(port [, asynchronous=False [, timeout=0.5 [, max_tries=10]]])

    Ovládání e-puck robota přes bluetooth z počítače.

    Při vytváření objektu je možné rozhodnout, zda-li má komunikace probíhat
    synchronně, anebo asynchronně. Tato volba ovlivňuje zda-li se pro
    komunikaci použije třída :class:`~epuck.comm.SyncComm` anebo
    :class:`~epuck.comm.AsyncComm`. Také na této volbě závisí co budou
    jednotlivé příkazy vracet. V případě synchronní komunikace půjde rovnou o
    odpověď. V případě asynchronní komunikace vrátí
    :class:`~epuck.comm.RequestHandler`. Z něj se stejné informace
    dostanou metodou :meth:`~epuck.comm.RequestHandler.get_response`
    (další podrobnosti v dokumentaci třídy
    :class:`~epuck.comm.RequestHandler`).

    :param port: cesta k portu, kde je e-puck připojen (např. :file:`/dev/rfcomm2`)
    :type port: string
    :param asynchronous: zda-li má být použita asynchronní komunikace.
    :type asynchronous: bool
    :param timeout: čas v sekundách před dalším pokusem o zaslání příkazu (asynchronní komunikace)
    :type timeout: float
    :param max_tries: maximální počet pokusů o zaslání příkazu (asynchronní komunikace)
    :type max_tries: int
    :raise: :exc:`~epuck.ControllerError`

    .. note::

        V této dokumentaci jsou popsány návratové hodnoty tak, jak je vrátí
        přímo příkaz při synchronní komunikaci, anebo metoda
        :meth:`~epuck.comm.RequestHandler.get_response` třídy
        :class:`~epuck.comm.RequestHandler` při komunikaci asynchronní.

    .. method:: set_speed(left, right)

        Nastavit rychlost levého a pravého krokového motoru. Rychlost je měřena
        v krocích za sekundu a musí být v rozmezí [-1000, 1000].

        Pokud je rychlost mimo rozsah, tak vyvolá výjimku
        :exc:`~epuck.WrongCommand`. Při asynchronní komunikaci může
        dojít k vypršení limitu pokusů a pak dojde k vyvolání výjimky
        :exc:`~epuck.comm.CommError`.

        :param left: požadovaná rychlost levého kola
        :type left: int
        :param right: požadovaná rychlost pravého kola
        :type right: int
        :raise: :exc:`~epuck.WrongCommand`, :exc:`~epuck.comm.CommError`

    .. method:: get_speed()

        Získat rychlost levého a pravého krokového motoru. Rychlost je měřena
        v krocích za sekundu a je v rozmezí [-1000, 1000].

        :returns: dvojice obsahující rychlost levého a pravého motoru
        :rtype: (int, int)
        :raise: :exc:`~epuck.comm.CommError`

    .. method:: set_body_led(on)

        Zapnout nebo vypnout zelenou diodu v robotovi.

        :param on: zapnout nebo vypnout diodu
        :type on: bool
        :raise: :exc:`~epuck.comm.CommError`

    .. method:: set_front_led(on)

        Zapnout nebo vypnout jasnou červenou diodu v přední části robota (vedle
        kamery).

        :param on: zapnout nebo vypnout diodu
        :type on: bool
        :raise: :exc:`~epuck.comm.CommError`

    .. method:: set_leds(on)

        Zapnout nebo vypnout všechny diody naráz, které jsou na obvodu robota
        naráz.

        :param on: zapnout nebo vypnout diody
        :type on: bool
        :raise: :exc:`~epuck.comm.CommError`

    .. method:: set_led(led_no, on)

        Zapnout nebo vypnout jednu z osmi diod, které jsou na obvodu robota.

        Diody jsou očíslovány 0 až 7, po směru hodinových ručiček, dioda číslo
        0 je v přední části robot (neplést s jasnější diodou, která je vedle
        kamery).

        :param led_no: číslo diody, která má být ovládána (číslo z rozsahu [0, 7])
        :type led_no: int
        :param on: zapnout nebo vypnout diodu
        :type on: bool
        :raise: :exc:`~epuck.WrongCommand`, :exc:`~epuck.comm.CommError`

    .. method:: get_turning_switch()

        Získat pozici otáčivého přepínače.

        Otáčivý přepínač je na horní straně robota, jde o malou černou tyčinku,
        kterou je možné otočit do jedné z 16 pozic. Pozice jsou očíslovány 0 až
        15. Přepínač je v pozici 0 pokud šipka ukazuje směrem k černé tečce,
        která je nakreslená na plošném spoji. Pozice jsou číslovány ve směru
        hodinových ručiček.

        :returns: pozice přepínače
        :rtype: int
        :raise: :exc:`~epuck.comm.CommError`

    .. method:: get_proximity_sensors()

        Získat data o vzdálenosti překážek z 8 IR senzorů.

        Senzory vrací hodnotu z rozsahu [0, 4095]. Jsou rozmístěny po obvodu
        robota zrcadlově na pravé i levé straně. Pokud bereme směr pohybu jako
        úhel 0 stupňů, tak se senzory nachází na 10, 45 a 90 stupních a také
        jsou dva vlevo i vpravo na zadní části robota.

        Metoda vrací vždy hodnoty všech senzorů. Pro přehlednější zpracování
        jsou uloženy ve slovníku, klíč je vždy znak označující levou (L) nebo
        pravou (P) stranu a pak uhel v jakém se senzor nachází (senzory vzadu
        jsou označeny B). Seznam klíčů tedy je ``['R10', 'R45', 'R90', 'RB',
        'LB', 'L90', 'L45', 'L10']``.

        :returns: hodnoty IR senzorů překážek
        :rtype: dict
        :raise: :exc:`~epuck.comm.CommError`

    .. method:: get_ambient_sensors()

        Získat data o okolním světlu z 8 IR senzorů.

        Senzory vrací hodnotu z rozsahu [0, 4095]. Jsou rozmístěny po obvodu
        robota zrcadlově na pravé i levé straně. Pokud bereme směr pohybu jako
        úhel 0 stupňů, tak se senzory nachází na 10, 45 a 90 stupních a také
        jsou dva vlevo i vpravo na zadní části robota.

        Metoda vrací vždy hodnoty všech senzorů. Pro přehlednější zpracování
        jsou uloženy ve slovníku, klíč je vždy znak označující levou (L) nebo
        pravou (P) stranu a pak uhel v jakém se senzor nachází (senzory vzadu
        jsou označeny B). Seznam klíčů tedy je ``['R10', 'R45', 'R90', 'RB',
        'LB', 'L90', 'L45', 'L10']``.

        :returns: naměřené hodnoty okolního světla
        :rtype: dict
        :raise: :exc:`~epuck.comm.CommError`

    .. method:: set_camera(mode, width, height, zoom)

        Nastavit parametry kamery.

        E-puck obsahuje kameru o rozlišení 640x480, avšak není možné využít
        její plnou kapacitu z paměťových důvodů. Proto je třeba nastavit jak
        velký obrázek uživatel očekává a také jaké prokládání má být použito.
        Kamera je v robotovi umístěna otočená, ale uživatel dostane už obraz
        správně orotovaný. Je však dobré na tento fakt myslet při zadávání
        šířky a výšky. Pokud je zoom 2 nebo 4, tak se o prokládání stará přímo
        kamera a zrychlí se tak patřičně framerate.

        Například pro rozměry 40x40 a zoom 8 robot vezme ze senzorů kamery
        obdélník velikosti 320x320 a z něj každý 8. pixel.

        Na parametry jsou kladeny následující požadavky:
            * velikost * zoom nesmí překročit kapacitu kamery.
            * velikost dat je omezena velikostí bufferu, který je zhruba 4kB.
            * zoom by měl být z rychlostních důvodů mocninou dvojky.

        Na formát fotografie nejsou kladena žádná další omezení, co se poměru
        stran týče. Je tedy možné získat i lineární obraz 480x1.

        Kamera může fotit v režimu rgb565 anebo v režimu stupňů šedi. Pro každý
        pixel pak používá buď 16 anebo 8 bitů. V režimu šedi je pak framerate
        dvojnásobný.

        :param mode: mód kamery, buď :const:`Controller.RGB565_MODE`, anebo
            :const:`Controller.GREYSCALE_MODE`.
        :param width: šířka požadované fotografie
        :type width: int
        :param height: výška požadované fotografie
        :type height: int
        :param zoom: velikost prokládání fotografie
        :type zoom: int

    .. method:: get_camera()

        Získat nastavení kamery.

        Metoda vrací slovník s parametry odpovídajícími parametrům metody
        :func:`~Controller.set_camera`.

        :return: Slovník s nastavením kamery. Klíče jsou:

            * *mode* -- mód kamery, buď :const:`Controller.RGB565_MODE`, anebo :const:`Controller.GREYSCALE_MODE`.
            * *width* -- šířka získané fotografie
            * *height* -- výška získané fotografie
            * *zoom* -- prokládání fotky

        :rtype: dict

    .. method:: get_photo()

        Získat fotku z kamery.

        Fotka je ve formátu, jaký byl zadán metodou
        :meth:`~Controller.set_camera`. Pokud nebylo nastavení měněno, tak je
        získána barevná fotka 40x40 pixelů se zoomem 8.

        Pro ulehčení práce s fotkou je vrácena jako instance třídy
        :class:`Image` z `PIL (Python Imaging Library)
        <http://www.pythonware.com/products/pil/>`_.

        :return: Fotka z kamery
        :rtype: :class:`Image`

    .. method:: reset()

        Resetovat robota.

        Proběhne restart robota. Všechno nastavení se anuluje, robot se
        zastaví.

    .. method:: set_motor_pos(left, right)

        Nastavení čítačů pro krokové motory.

        U obou krokových motorů je možné aktuálnímu pozici kola přiřadit číslo,
        to pak bude s každým krokem motoru inkrementováno nebo dekrementováno.
        Pozice se počítají modulo 1000, což je jedna celá obrátka kola.

        Počet vykonaných kroků je možné zjistit odečtením nastavených hodnot od
        hodnot získaných metodou :meth:`get_motor_pos`.

        :param left: nová hodnota čítače pro levý motor
        :type left: int
        :param right: nová hodnota čítače pro levý motor
        :type right: int

    .. method:: get_motor_pos()

        Získat aktuální hodnotu čítačů krokových motorů.

        U obou krokových motorů je možné aktuálnímu pozici kola přiřadit číslo
        pomocí metody :meth:`set_motor_pos`, to pak bude s každým krokem motoru
        inkrementováno nebo dekrementováno. Pozice se počítají modulo 1000, což
        je jedna celá obrátka kola.

        :return: dvojice hodnot čítačů (levý motor, pravý motor)
        :rtype: (int, int)

Výjimky
-------

.. exception:: EPuckError

    Základní výjimka v :mod:`epuck`. Všechny ostatní od ní dědí.

.. exception:: ControllerError

    Chyba při práci s robotem. Například se nepovedlo k robotovi vůbec
    připojit.

.. exception:: WrongCommand

    Specializace výjimky :exc:`ControllerError`. Uživatel nejspíše zadal špatný
    příkaz, např. parametry, které jsou mimo povolené rozsahy.


