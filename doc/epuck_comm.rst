:mod:`epuck.comm` --- Sériová komunikace s robotem
==================================================

.. module:: epuck.comm

Při komunikaci s robotem si uživatel může vybrat mezi synchronní anebo
asynchronní komunikací. Jeho rozhodnutí při vytváření instance třídy
:class:`~epuck.Controller` rozhodne o tom, zda-li se pro komunikaci s robotem
využije třída :class:`~epuck.comm.SyncComm` anebo
:class:`~epuck.comm.AsyncComm`. Přesný popis těchto tříd je k nalezení v
programátorské dokumentaci, uživatel je využívá pouze prostřednictvím třídy
:class:`~epuck.Controller`.

Důležité je ovšem vědět jaké výjimky můžou vzniknout při komunikaci s robotem.
Všechny výjimky samozřejmě dědí od :exc:`~epuck.EPuckError`. Obecně pro chybu
při komunikaci slouží výjimka :exc:`~epuck.comm.CommError`. Od ní pak dědí
výjimky pro jednotlivé druhy komunikace: :exc:`~epuck.comm.SyncCommError` a
:exc:`~epuck.comm.AsyncCommError`.

Další důležitý rozdíl mezi sériovou a asynchronní komunikací je ve vrácené
hodnotě z metod třídy :class:`~epuck.Controller`. Pro synchronní komunikaci
jsou vrácena přímo odpověď. Pro asynchronní komunikaci je ovšem vrácen pouze
:class:`~epuck.comm.RequestHandler`, pomocí kterého uživatel může zjistit
zda-li už byla přijata odpověď a posléze ji získat.

Příklad komunikace
------------------

Synchronní
^^^^^^^^^^
::

    >>> from epuck import Controller
    >>> controller = Controller('/dev/rfcomm0')
    >>> controller.get_speed()
    (0,0)

Důležité je si uvědomit, že při synchronní komunikaci se nebudou provádět další
příkazy dokud nebude získána odpověď od právě odeslaného. Tedy po zavolání
metody :meth:`~epuck.Controller.get_speed` bude zablokováno vykonávání dalších
příkazů dokud robot nepošle svou rychlost. Běh programu tedy je přerušován při
každém poslání příkazu, navíc se může stát, že robot na příkaz neodpoví a pak
je třeba čekat než vyprší timeout a postarat se o nové zaslání příkazu.
