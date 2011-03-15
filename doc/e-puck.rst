E-puck robot
============

.. image:: http://www.e-puck.org/images/stories/epuck-look.jpg
    :scale: 50 %
    :width: 400px
    :height: 300px
    :alt: e-puck robot
    :class: float-right

E-puck je miniaturní robot vytvořený pro výukové účely na akademické
úrovni. Vytvořen byl v Ecole Polytechnique Fédérale de Laussanne. Celý
projekt je založen na konceptu otevřeného hardware, což znamená, že všechny
dokumenty a schémata jsou dostupná pod svobodnou licencí umožňující
komukoli využívat e-puck robota na maximum a vyvýjet pro něj ať už
software, anebo např. hardwarové nádstavby. Vše je dostupné na `stránkách
výrobce <http://www.e-puck.org>`_.

E-puck robot byl vytvořen s několika kritérii:

*   *Stolní velikost* -- možnost experimentovat s robotem přímo u
    počítače je velmi výhodná pro studenty. Pokud se za optimální velikost
    pracovní plochy považuje 10-ti násobek velikosti robota, tak e-puck se
    svým průměrem 75mm je ideální pro použití na stole.

*   *Široké spektrum použití* -- robota je možné použít nejen pro výuku
    robotiky, ale také například pro výuku zpracování obrazu nebo zvuku,
    programování vestavěných systémů, automatizace atd. Toho je docíleno
    velkým spektrem sensorů.

*   *Uživatelská přívětivost* -- při vytváření rozhraní by vždy měl být
    kladen důraz na jednoduchost. Rozhraní by mělo být intuitivní a
    důkladně zdokumentované, aby se zrychlil proces učení.

Součástí robota je velká škála sensorů a akčních členů. Srdcem robota je
mikrokontroler s obvodem dsPIC. Skládá se z 16bitového procesoru a jednotky
pro zpracování signálu. Procesor má frekvenci 64 MHz, 8 kB RAM a 144 kB
flash paměti. Robot obsahuje následující sensory:

*   *Infračervené sensory* -- po obvodu robota je 8 IR sensorů. Měří
    buď vzdálenost od překážek, anebo intenzitu okolního světla. Jedná se o
    základní sensory využívané pro pohyb mezi překážkami.

*   *Akcelerometr* -- 3D akcelerometr slouží k získání vektoru
    zrychlení robota. Může být použit pro spoustu experimentů (měření
    náklonu, zrychlení, detekce nárazu, pádu, \ldots).

*   *3 mikrofony* -- více mikrofonů slouží k triangulaci zdroje zvuku,
    velikost dat získaných z mikrofonů je ovšem na kapacity robota příliš a
    proto je nutné použít jednotku pro zpracování signálu (DSP).

*   *Barevná kamera* -- v přední části robota je kamera s rozlišením
    640x480, bohužel kvůli paměťovým omezením robota je možné získat pouze
    část obrazu. I tak je ale možné ji použít pro experimenty s počítačovým
    viděním.

Samotné sensory by samozřejmě byly bez užitku, kdyby robot neměl žádné
akční členy. Studenti mohou využít následujících komponent:

*   *2 krokové motory* -- slouží pro pohyb robota, mají rozlišení 1000
    kroků za jedno otočení kola.

*   *Speaker* -- ve spojení s mikrofony může sloužit pro dorozumívání s
    jinými roboty, také jde o výhodný způsob interakce s uživatelem.

*   *8 LED* -- diody jsou rozmístěné po obvodu robota. Slouží jako
    vizuální rozhraní pro uživatele, anebo pro jiného robota.

*   *Zelená dioda uvnitř robota* -- hlavním jejím posláním je vypadat
    dobře, ale také může být použita pro interakci s jinými objekty.

*   *Přední dioda u kamery* -- tato LED nevytváří rozptýlené světlo,
    ale paprsek, který je možné použít s kamerou pro odhadování vzdálenosti
    k vzdálenějším překážkám.

Ovládání e-puck robota je možné řešit několika způsoby. V první řadě
existuje kompatibilní GCC kompilátor, takže je možné psát řídící program,
který bude vykonáván přímo uvnitř robota, v programovacím jazyku C. Výrobce
navíc dodává knihovnu s intuitivním rozhraním pro ovládání všech součástí.
Tento přístup má ovšem několik nevýhod. Cyklus vývoje programu je pomalý,
kvůli každé změně v programu je třeba spustit kompilaci na počítači, dále
nahrát program do robota a teprve pak je možné změnu vyzkoušet. Dalším
problémem je výkon robota, který nemusí stačit pro složitější výpočty.

Lepším způsobem se tedy zdá využívat program v robotovi pouze pro
vykonávání příkazů, které jsou naplánovány v počítači. To je přístup,
kterým se zabývá má práce.

Knihovna je primárně vyvíjena pro operační systém Linux. Použité knihovny jsou
multiplatformní, avšak popisované nástroje pro instalaci firmware na robota
jsou pouze pro Linux. Pro adaptaci na jiné OS bude potřeba trocha invence.

