Quick start
-----------

`MyDisease.info <http://mydisease.info>`_ provides two simple web services: one for querying disease objects and the other for disease annotation retrieval by common IDs (e.g. mondo, doid, etc.). Both return results in `JSON <http://json.org>`_ format.

Disease query service
^^^^^^^^^^^^^^^^^^^^^^^

URL
"""""
::

    http://mydisease.info/v1/query

Examples
""""""""
::

    http://mydisease.info/v1/query?q=GIST
    http://mydisease.info/v1/query?q=_exists_:ctd
    http://mydisease.info/v1/query?q=disease_ontology.doid:DOID\:0110340&fields=disease_ontology


.. Hint:: View nicely formatted JSON result in your browser with this handy add-on: `JSON formatter <https://chrome.google.com/webstore/detail/bcjindcccaagfpapjjmafapmmgkkhgoa>`_ for Chrome or `JSONView <https://addons.mozilla.org/en-US/firefox/addon/jsonview/>`_ for Firefox.


To learn more
"""""""""""""

* You can read `the full description of our query syntax here <doc/disease_query_service.html>`__.
* Try it live on `interactive API page <http://mydisease.info/v1/api>`_.
* Batch queries? Yes, you can. do it with `a POST request <doc/disease_query_service.html#batch-queries-via-post>`__.


Disease annotation service
^^^^^^^^^^^^^^^^^^^^^^^^^^^

URL
"""""
::

    http://mydisease.info/v1/disease/<disease_id>

``<disease_id>`` can be any one of the following common disease identifiers:

    * `MONDO <https://mondo.monarchinitiative.org/>`_,
    * `Disease Ontology ID <https://disease-ontology.org/>`.


Examples
""""""""
::

    http://mydisease.info/v1/disease/MONDO:0016575
    http://mydisease.info/v1/disease/MONDO:0020753?fields=mondo
    http://mydisease.info/v1/disease/MONDO:0011996?fields=disease_ontology


To learn more
"""""""""""""

* You can read `the full description of our query syntax here <doc/disease_annotation_service.html>`__.
* Try it live on `interactive API page <http://mydisease.info/v1/api>`_.
* Yes, batch queries via `POST request <doc/disease_annotation_service.html#batch-queries-via-post>`__ as well.
