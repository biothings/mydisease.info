# Disease Ontology Plugin for MyDisease.info

Standardized ontology for human disease procured by [Disease Ontology](https://disease-ontology.org/) and available on [GitHub](https://github.com/DiseaseOntology/HumanDiseaseOntology/tree/master/src/ontology).

Used [obonet](https://pypi.org/project/obonet/) and [networkx](https://pypi.org/project/networkx/) python packages to read and query .obo data file.  

Individual formatted entries have the final dictionary format, where _id is based off of DOID, but changed to MONDO if available on MyDisease.info (retrieved via batch queries):  

        entry = {
            "_id": <MONDO:ID> or <DOID>,
            "disease_ontology" : {
              "doid": <DOID>,
              "name": <disease name>,
              "def": <disease definition>,
              "synonyms": <dictionary of "exact" or "related" synonyms>,
              "xrefs": <dictionary of xrefs>,
              "children": <list of children>,
              "descendants": <list of descendants>,
              "parents": <list of parents>,   
              "ancestors": <list of ancestors>
            }
        }

