:mod:`epuck.controller` -- Knihovna pro ovládání robota z počítače
==================================================================

.. module:: epuck.controller
   :synopsis: Ovládání robota z počítače
.. moduleauthor:: David Marek <davidm@atrey.karlin.mff.cuni.cz>

.. exception:: ControllerError
    
   Výjimka upozorňující na chybu, která nastala při komunikaci s E-puck
   robotem. Robot dostal špatné parametry, anebo zaslal špatnou odpověď.

.. class:: Controller(port)

   Třída sloužící ke komunikaci s E-puck robotem.

   Třída nevytváří samotné spojení s robotem, to je třeba mít již hotové (viz
   :ref:`připojení <pripojeni>`). Pro připojení k robotovi pak stačí jen zadat
   port, na kterém je připojen.

   Třída využívá protokol knihovny `BTcom
   <http://www.e-puck.org/index.php?option=com_remository&Itemid=71&func=fileinfo&id=59>`_,
   snaží se zprostředkovat všechny schopnosti, které robot má.

   :param port: Port, na kterém je robot připojen (např. ``'/dev/rfcomm0'``)
   :type port: str

   .. method:: set_motor_speed(left, right)

      Nastavení rychlosti motorů.

      :param left: Nová rychlost levého motoru.
      :type left: int
      :param right: Nová rychlost pravého motoru.
      :type right: int
      
      :note: Rychlost je v rozmezi [0...1000].

   .. method:: get_motor_speed

      Získání rychlosti motorů.

      :return: Rychlost levého a pravého motoru.
      :rtype: (int, int)

   .. attribute:: left_motor_speed

      Property sloužící k získání nebo změně rychlosti levého motoru.

      :warning: Nepracuje se přímo s robotem, ale s interní reprezentací, která
       nemusí odpovídat skutečnosti, pokud robotu byly dávány příkazy mimo
       dosah této aplikace.

   .. attribute:: right_motor_speed

      Property sloužící k získání nebo změně rychlosti pravého motoru.

      :warning: Nepracuje se přímo s robotem, ale s interní reprezentací, která
       nemusí odpovídat skutečnosti, pokud robotu byly dávány příkazy mimo
       dosah této aplikace.

   .. attribute:: body_led

      Property zapínající/vypínající zelenou LED uvnitř těla robota. Hodnota je
      True/False.


