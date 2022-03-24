# Nieuw in de Kamer

Een kleine selectie uit de [Nieuw in de Kamer](https://nieuwindekamer.nl) back-end. Nieuw in de Kamer is een Twitterbot die elke dag op zoek gaat naar woorden die voor het eerst in de plenaire zaal van de Tweede Kamer zijn gezegd, en deze vervolgens in de context en met een linkje naar de filmbeelden op `@nieuwindekamer` deelt. 

Een paar leuke voorbeelden:
* [Caroline van der Plas zegt memes](https://twitter.com/nieuwindekamer/status/1389656076744863751)
* [Esther Ouwehand zegt VVD-machinaties](https://twitter.com/nieuwindekamer/status/1381321153910870018)
* [Sylvana Simons zegt RuPaul's Drag Race](https://twitter.com/nieuwindekamer/status/1383133093666643970)

In `tweedekamer.py` wordt de live-transcriptieservice van de Tweede Kamer opgevraagd waar de woorden vergeleken worden met de database van de meer dan een miljoen unieke woorden sinds 1998, toen de transcriptie gedigitaliseerd werd. Daarna worden deze in `debatgemist.py` gekoppeld aan de officiële handelingen, waar ook een link naar de videobeelden wordt toegevoegd. In `scores.py` wordt beoordeeld welke woorden leuk zijn voor Twitter, waar naar dingen als lengte en politieke 'hot topics' gekeken wordt. Als laatst wordt in `twitter.py` de tweet van het leukst bevonden wordt opgemaakt, en verstuurd.

