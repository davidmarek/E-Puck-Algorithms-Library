.. E-Puck Algorithms Library documentation master file, created by
   sphinx-quickstart on Tue Jun 22 16:33:23 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

E-Puck Algorithms Library
=========================

Abstrakt
--------

E-puck robot je malý robot navrhnutý pro výukové účely. Smyslem této práce bude
vytvořit knihovnu pro ovládání robota z počítače a také stvořit sbírku
ukázkových algoritmů, kterými se mohou uživatelé knihovny inspirovat. Vše bude
napsáno v jazyku python. Důraz bude kladen na čitelnost a pochopitelnost kódu.
Ke kódu bude také bohatá dokumentace popisující použité algoritmy.

Knihovna je primárně vyvíjena pro operační systém Linux. Použité knihovny jsou
multiplatformní, avšak popisované nástroje pro instalaci firmware na robota
jsou pouze pro Linux. Pro adaptaci na jiné OS bude potřeba trocha invence.

.. _pripojeni:

Připojení
---------

1. Je třeba mít nainstalované: ``bluez-firmware`` ``bluez-utils`` (``bluez-pin`` nebo něco
   jiného co se zeptá na heslo, např ``bluez-gnome`` a jeho ``bluetooth-applet``)

2. Zjištění adresy robota::

    $ hcitool scan

3. Nastavení sériového portu ``/etc/bluetooth/rfcomm.conf``::

    rfcomm0 {
        bind yes;
        device 08:00:17:2C:E0:88; # Dopsat vlastní adresu
        channel 1;
        comment "e-puck_0006";    # Vlastní komentář
    }

4. Vlastní připojení::

    $ rfcomm bind rfcomm0
    $ rfcomm connect rfcomm0

   Po druhém příkazu by se mělo něco zeptat na heslo, to je stejné s číslem
   robota (je na něm napsané). 

   Možné chyby: 

    *Can't connect RFCOMM socket: Connection refused*
        Nejspíše neběží žádná aplikace, která by se na heslo zeptala. Je třeba spustit např.
        bluetooth-applet.

    *Can't create RFCOMM TTY: Address already in use*
        Možná příčína je už připojené zařízení. Buď už běží rfcomm, anebo si
        někdo robota přivlastnil. Občas pomůže::

        $ rfcomm release rfcomm0
        $ rfcomm connect rfcomm0

5. Pokud se robot chová podivně (např. nereaguje na nějaké příkazy) tak je to
   nejspíše tím, že mu dochází baterka! Není dobré ladit kód na robotovi, který
   mele z posledního :-(

Instalace firmware
------------------

Knihovna komunikuje s E-puck robotem pomocí posílání textových příkazů. V
robotovi je nahrána knihovna `BTcom
<http://www.e-puck.org/index.php?option=com_remository&Itemid=71&func=fileinfo&id=59>`_.

K jejímu nahrání stačí použít `epuckupload
<http://svn.gna.org/viewcvs/e-puck/trunk/tool/bootloader/computer_side/multi_platform/>`_.
Stačí se řídit pomocí ``README`` a na E-puck nahrát soubor ``BTcom.hex``.

Knihovny
--------

.. toctree::
   :hidden:

   epuck_controller.rst

:mod:`epuck.controller`
   Ovládání robota z počítače.

:mod:`epuck.touch`
   Algoritmy využivající IR senzory.

:mod:`epuck.vision`
   Algoritmy využivající kameru.

:mod:`epuck.hearing`
   Algoritmy využívající mikrofon.
    
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

