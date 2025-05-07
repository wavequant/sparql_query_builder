
WIKIDATA_TEMPLATES = {
    "Празен": "",
    "Известни учени в сферата на компютърните науки": """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?scientist ?scientistLabel ?birthDate WHERE {
  ?scientist wdt:P106 wd:Q82594 . 
  ?scientist wdt:P31 wd:Q5 .    
  OPTIONAL { ?scientist wdt:P569 ?birthDate . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
ORDER BY DESC(xsd:integer(SUBSTR(STR(?birthDate), 1, 4)))
LIMIT 20
    """,
    "Столици": """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?country ?countryLabel ?capital ?capitalLabel WHERE {
  ?country wdt:P31 wd:Q6256 . 
  ?country wdt:P36 ?capital .  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],bg". }
}
ORDER BY ?countryLabel
LIMIT 25
    """,
    "Снимка на Дъглъс Адъмс": """
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?item ?itemLabel ?image WHERE {
  BIND(wd:Q42 AS ?item)
  OPTIONAL { ?item wdt:P18 ?image . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],bg". }
}
    """
}
