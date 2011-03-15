:mod:`epuck.controller` --- Ovládání robota
===========================================

.. module:: epuck.controller

Ovládání robota je velmi jednoduché a přímočaré. V první řadě je potřeba mít
robota již připojeného. Návod je k nalezení v sekci :ref:`vytvoreni-spojeni-s-robotem`.
Celá komunikace probíhá přes třídu :class:`Controller`.

Příklad::

    #!/usr/bin/env python
    # -*- coding: utf-8 -*-

    """Go forward, stop in front of an obstacle."""

    import time

    from epuck.controller import Controller

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


:class:`Controller`
-------------------

.. class:: Controller(port [, asynchronous=False [, timeout=0.5 [, max_tries=10]]])

    Ovládání e-puck robota přes bluetooth z počítače.

    Při vytváření objektu je možné rozhodnout, zda-li má komunikace probíhat
    synchronně, anebo asynchronně. Tato volba ovlivňuje zda-li se pro
    komunikaci použije třída :class:`~epuck.comm.sync.SyncComm` anebo
    :class:`~epuck.comm.async.AsyncComm`. Také na této volbě závisí co budou
    jednotlivé příkazy vracet. V případě synchronní komunikace půjde rovnou o
    odpověď. V případě asynchronní komunikace vrátí
    :class:`~epuck.comm.async.RequestHandler`. Z něj se stejné informace
    dostanou metodou :meth:`~epuck.comm.async.RequestHandler.get_response`
    (další podrobnosti v dokumentaci třídy
    :class:`~epuck.comm.async.RequestHandler`).

    :param port: cesta k portu, kde je e-puck připojen (např. :file:`/dev/rfcomm2`)
    :type port: string
    :param asynchronous: zda-li má být použita asynchronní komunikace.
    :type asynchronous: bool
    :param timeout: čas v sekundách před dalším pokusem o zaslání příkazu (asynchronní komunikace)
    :type timeout: float
    :param max_tries: maximální počet pokusů o zaslání příkazu (asynchronní komunikace)
    :type max_tries: int
    :raise: :exc:`~epuck.controller.ControllerError`

    .. note::

        V této dokumentaci jsou popsány návratové hodnoty tak, jak je vrátí
        přímo příkaz při synchronní komunikaci, anebo metoda
        :meth:`~epuck.comm.async.RequestHandler.get_response` třídy
        :class:`~epuck.comm.async.RequestHandler` při komunikaci asynchronní.

    .. method:: set_speed(left, right)

        Nastavit rychlost levého a pravého krokového motoru. Rychlost je měřena
        v krocích za sekundu a musí být v rozmezí [-1000, 1000].

        Pokud je rychlost mimo rozsah, tak vyvolá výjimku
        :exc:`~epuck.controller.WrongCommand`. Při asynchronní komunikaci může
        dojít k vypršení limitu pokusů a pak dojde k vyvolání výjimky
        :exc:`~epuck.comm.CommError`.

        :param left: požadovaná rychlost levého kola
        :type left: int
        :param right: požadovaná rychlost pravého kola
        :type right: int
        :raise: :exc:`~epuck.controller.WrongCommand`, :exc:`~epuck.comm.CommError`

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
        :raise: :exc:`~epuck.controller.WrongCommand`, :exc:`~epuck.comm.CommError`

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
