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

Asynchronní
^^^^^^^^^^^
::

    >>> from epuck import Controller
    >>> controller = Controller('/dev/rfcomm0', asynchronous=True)
    >>> request = controller.get_speed()
    >>> request.get_response()
    (0,0)

Vykonání příkazu vypadá velmi podobně, avšak důležitá změna je, že metody
nevrací výsledek (protože možná ještě žádný není), ale pouze
:class:`RequestHandler`. Metoda :meth:`~RequestHandler.get_response` se chová v podstatě dost
podobně jako synchronní komunikace. Protože vždy zaručuje, že vrátí výsledek,
tak se nejprve podívá, zda-li už byl přijat, pokud ne, tak na něj počká.

Pokud není výsledek příkazu potřeba, například po volání metody
:meth:`~epuck.Controller.set_speed`, tak je možné návratovou hodnotu ignorovat.

Dalším případem je volání příkazů v aplikaci, která provádí i něco jiného, než
jen ovládání robota (např. GUI). Pak je možné metodou
:meth:`~epuck.comm.RequestHandler.response_received` pouze zkontrolat, zda odpověď už přišla. A
případně ji zpracovat::

    >>> request = controller.get_speed()
    >>> if request.response_received():
    ...     value = request.get_response()
    ...

Občas chceme zavolat nějakou funkci v odpovědi na přišlá data. V takovém
případě není nutnost kontrolovat, zda-li už přišla odpověď, až tak elegantní.
Příkazy ovšem umožňují i nastavit tzv. callback, funkci, která se zavolá, po
získání odpovědi na příkaz, sama a jako parametr dostane data tak, jak by je
vrátila metoda :meth:`~RequestHandler.get_response`::

    >>> request = controller.get_speed(callback=fce_zpracujici_odpoved)

Odpověd u asynchronní komunikace
--------------------------------

.. class:: RequestHandler

    Jedná se o objekt reprezentující odpověď na příkaz zaslaný robotovi při
    asynchronní komunikaci. U asynchronní komunikace je důležité, aby poslání
    příkazu nezablokovalo vlákno, v kterém byl příkaz poslán. Proto není možné
    čekat na odpověď. Uživatel ovšem nezůstane bez odpovědi. Příkaz mu vrátí
    právě tento handler, pomocí kterého dokáže zjistit, zda-li už odpověď došla
    a případně i získat onu odpověď.

    .. method:: response_received()

        Slouží ke kontrole, zda-li už došla odpověď od robota. Neblokuje vlákno
        a nevrací odpověď. K jejímu získání slouží metoda :meth:`get_response`.

        :returns: zda-li došla odpověď od robota
        :rtype: bool

    .. method:: get_response()

        Zkontroluje, zda-li došla odpověď, pokud ano, tak ji vrátí, v opačném
        případě počká dokud nedorazí a pak ji vrátí. Z toho důvodu
        zablokuje vlákno, pokud ještě odpověď nedošla.

        Pokud je možné pokračovat ve vykonávání program bez této odpovědi, tak
        se doporučuje nejprve kontrolovat přítomnost odpovědi pomocí metody
        :meth:`response_received`.

        :returns: odpověď od robota, přesný druh odpovědi k nalezení v
            dokumentaci třídy :class:`~epuck.Controller`
        :rtype: závisí na zaslaném příkazu

    .. method:: error_raised()

        Kontrola, zda-li při vykonání příkazu nevznikla výjimka.

        Výjimka je uložena v atributu `error`. Bude vyhozena pokud se uživatel
        pokusí přistoupit k odpovědi, anebo zavolá metodu :meth:`join`.

        :returns: zda-li byla vyhozena výjimka
        :rtype: bool

    .. method:: join()

        Vyčkání na provedení příkazu.

        Zablokuje vykonávání programu dokud nepřijde odpověď na příkaz.


Výjimky
-------

.. exception:: CommError

    Chyba při komunikaci s robotem. Nejčastější příčinou je, že robot
    neodpovídá.

.. exception:: SyncCommError

    Chyba při synchronní komunikaci s robotem.

.. exception:: AsyncCommError

    Chyba při asynchronní komunikaci s robotem.
