//fix naming - hl mesto praha, ()
//city and muni part hiarchy, frequency..
// missing uzemi hl mesta prahy population size (district)

//short
//detail

// halvni mesto praha - region, okres... => praha?
// uzemí
// multisearch for regions like praha-vychod, brno-venkov
// uzemi hl mesta prahy missing weigth, others missing weigth
// check for missing or ecess ones
// check all data is what it should be
// look at the resulting data, some labels, detail etc are to be adjusted
// numbers
// repeated names in parts

kraj vysočina, okresy

// praha vinohrady == čast obce 
// leží na uzemí několika obvodů => cela čast nespadá pod žádný

//reconsider the munipart filtering?

entirely missing even large (vinohrady praha) munipart population weitghs

do a lot more testing to make sure things are actually correct

----------------------

1. locations.json creation
2. search algorithm
---

diacritics - done? (ignoring, not ignoring, sorting)
ch - done?
spaces and dashes - (equal)

praha 1
roman numbers
plzen 2-slovany
something-something
1. díl

ignoring space?
normalize dashes, spaces, other characters (), manual fix

sorting numbers, sorting by other things like distance, frequency of selection, user specific

even fuzzier search (at least when theres no results?)

//fix multistart implementation (slovany)
//missing detail, missing okresy, kraje

----

test cases:

c => česke budejovice, chomutov, česká lipa
ř => řicany, řevnice, ričany 
ů => udraž, ujezd, ustecký kraj
dú =>

-----

missing weigts on some locations? (ujezd, Úherce)
incorrect weigths on some locations? (ujezd, Údraž)
add the detail to make it easier to understand




