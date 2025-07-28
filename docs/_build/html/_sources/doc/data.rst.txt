.. Data

Disease annotation data
************************

.. _data_sources:

Data sources
------------

We currently obtain disease annotation data from several data resources and
keep them up-to-date, so that you don't have to do it:

.. _CTD: http://ctdbase.org/
.. _MONDO: http://mondo.monarchinitiative.org/
.. _HPO: https://hpo.jax.org/
.. _UMLS: https://www.nlm.nih.gov/research/umls/index.html
.. _Disease_Ontology: https://disease-ontology.org/
.. _DisGeNET: https://www.disgenet.org/



.. raw:: html

    <div class='metadata-table'>

Total Diseases loaded: **N/A**

+--------------------------------+---------------+---------------------------+------------------+------------------------------------------+
| Source                         | version       | # of diseases             | key name*        |  data notes                              |
+================================+===============+===========================+==================+==========================================+
| `CTD`_                         | \-            | 0                         | ctd              |                                          |
+--------------------------------+---------------+---------------------------+------------------+------------------------------------------+
| `MONDO`_                       | \-            | 0                         | mondo            |                                          |
+--------------------------------+---------------+---------------------------+------------------+------------------------------------------+
| `HPO`_                         | \-            | 0                         | hpo              |                                          |
+--------------------------------+---------------+---------------------------+------------------+------------------------------------------+
| `UMLS`_                        | \-            | 0                         | umls             |                                          |
+--------------------------------+---------------+---------------------------+------------------+------------------------------------------+
| `Disease_Ontology`_            | \-            | 0                         | disease_ontology |                                          |
+--------------------------------+---------------+---------------------------+------------------+------------------------------------------+
|  DisGeNET                      | \-            | \-                        | \-               | Removed due to licensing changes         |
+--------------------------------+---------------+---------------------------+------------------+------------------------------------------+


.. raw:: html

    </div>

\* key name: this is the key for the specific annotation data in a disease object.

The most updated information can be accessed `here <http://mydisease.info/v1/metadata>`_.

.. note:: Each data source may have its own usage restrictions. Please refer to the data source pages above for their specific restrictions.


.. _disease_object:

Disease object
---------------

Disease annotation data are both stored and returned as a disease object, which
is essentially a collection of fields (attributes) and their values:

.. code-block:: json


    {
        "_id": "MONDO:0020753",
        "_version": 1,
        "disease_ontology": {
            "_license": "https://github.com/DiseaseOntology/HumanDiseaseOntology/blob/master/DO_LICENSE.txt",
            "ancestors": [
                "DOID:0050117",
                "DOID:4",
                "DOID:934"
            ],
            "children": [
                "DOID:0080600",
                "DOID:0080642",
                "DOID:2945"
            ],
            "def": "\"A viral infectious disease that has_material_basis_in Coronavirus.\" [url:https\\://www.cdc.gov/coronavirus/, url:https\\://www.ncbi.nlm.nih.gov/books/NBK7782/, url:https\\://www.who.int/health-topics/coronavirus]",
            "descendants": [
                "DOID:0080600",
                "DOID:0080642",
                "DOID:2945"
            ],
            "doid": "DOID:0080599",
            "name": "Coronavirus infectious disease",
            "parents": [
                "DOID:934"
            ],
            "synonyms": {},
            "xrefs": {}
        },
        "mondo": {
            "children": [
                "MONDO:0005091",
                "MONDO:0025404",
                "MONDO:0025420",
                "MONDO:0025491",
                "MONDO:0100096",
                "MONDO:0100116"
            ],
            "definition": "Infectious disease causes by viruses in the subfamily Orthocoronavirinae (coronaviruses). In humans, coronaviruses cause respiratory tract infections that can be mild, such as some cases of the common cold (among other possible causes, predominantly rhinoviruses), and others that can be lethal, such as SARS, MERS, and COVID-19.",
            "label": "Orthocoronavirinae infectious disease",
            "mondo": "MONDO:0020753",
            "parents": "MONDO:0005718",
            "synonyms": "coronavirus infectious disease",
            "xrefs": {
                "doid": "DOID:0080599"
            }
        }
    }


The example above omits many of the available fields.  For a full example,
check out `this example disease <http://mydisease.info/v1/disease/MONDO:0020753>`_, or try the `interactive API page <http://mydisease.info>`_.


_id field
---------

Each individual disease object contains an "**_id**" field as the primary key.  Where possible, MyDisease.info disease objects use `MONDO <https://mondo.monarchinitiative.org/>`_ as their "**_id**".  If a MONDO isn't available, any one of the following datasource IDs may be used:

    * `Disease_Ontology_ID <https://disease-ontology.org/>`_

_score field
------------

You will often see a “_score” field in the returned disease object, which is the internal score representing how well the query matches the returned disease object. It probably does not mean much in `disease annotation service <data.html>`_ when only one disease object is returned. In `disease query service <disease_query_service.html>`_, by default, the returned disease hits are sorted by the scores in descending order.


.. _available_fields:

Available fields
----------------

The table below lists all of the possible fields that could be in a disease object, as well as all of their parents (for nested fields).  If the field is indexed, it may also be directly queried.


.. raw:: html

    <table class='indexed-field-table stripe'>
        <thead>
            <tr>
                <th>Field</th>
                <th>Indexed</th>
                <th>Type</th>
                <th>Notes</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    </table>

    <div id="spacer" style="height:300px"></div>
