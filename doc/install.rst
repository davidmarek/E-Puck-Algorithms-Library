Připojení a instalace
=====================

.. _vytvoreni-spojeni-s-robotem:

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

