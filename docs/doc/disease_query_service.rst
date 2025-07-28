Disease query service
******************************

.. role:: raw-html(raw)
   :format: html
.. |info| image:: /_static/information.png
             :alt: information!


This page describes the reference for MyDisease.info disease query web service. It's also recommended to try it live on our `interactive API page <http://mydisease.info/v1/api>`_.


Service endpoint
=================

::

    http://mydisease.info/v1/query

GET request
==================

Query parameters
-----------------

q
"""""
    Required, passing user query. The detailed query syntax for parameter "**q**" we explained `below <#query-syntax>`_.

fields
""""""
    Optional, a comma-separated string to limit the fields returned from the matching disease hits. The supported field names can be found from any disease object (e.g. `here <http://mydisease.info/v1/disease/MONDO:0016575>`_). Note that it supports dot notation, and wildcards as well, e.g., you can pass "mondo", "mondo.xrefs", or "ctd.chemical_related_to_disease.*". If "fields=all", all available fields will be returned. Default: "all".

size
""""
    Optional, the maximum number of matching disease hits to return (with a cap of 1000 at the moment). Default: 10.

from
""""
    Optional, the number of matching disease hits to skip, starting from 0. Default: 0

.. Hint:: The combination of "**size**" and "**from**" parameters can be used to get paging for large query:

::

    q=ctd.chemical_related_to_disease.chemical_name:zidovudine*&size=50                     first 50 hits
    q=ctd.chemical_related_to_disease.chemical_name:zidovudine*&size=50&from=50             the next 50 hits

fetch_all
"""""""""
    Optional, a boolean, which when TRUE, allows fast retrieval of all unsorted query hits.  The return object contains a **_scroll_id** field, which when passed as a parameter to the query endpoint, returns the next 1000 query results.  Setting **fetch_all** = TRUE causes the results to be inherently unsorted, therefore the **sort** parameter is ignored.  For more information see `examples using fetch_all here <#scrolling-queries>`_.  Default: FALSE.

scroll_id
"""""""""
    Optional, a string containing the **_scroll_id** returned from a query request with **fetch_all** = TRUE.  Supplying a valid **scroll_id** will return the next 1000 unordered results.  If the next results are not obtained within 1 minute of the previous set of results, the **scroll_id** becomes stale, and a new one must be obtained with another query request with **fetch_all** = TRUE.  All other parameters are ignored when the **scroll_id** parameter is supplied.  For more information see `examples using scroll_id here <#scrolling-queries>`_.

sort
""""
    Optional, the comma-separated fields to sort on. Prefix with "-" for descending order, otherwise in ascending order. Default: sort by matching scores in descending order.

facets
""""""
    Optional, a single field or comma-separated fields to return facets, can only be used on non-free text fields.  E.g. "facets=mondo.parents".  See `examples of faceted queries here <#faceted-queries>`_.

facet_size
""""""""""
    Optional, an integer (1 <= **facet_size** <= 1000) that specifies how many buckets to return in a faceted query.

callback
""""""""
    Optional, you can pass a "**callback**" parameter to make a `JSONP <http://ajaxian.com/archives/jsonp-json-with-padding>`_ call.

dotfield
""""""""
    Optional, can be used to control the format of the returned disease object.  If "dotfield" is true, the returned data object is returned flattened (no nested objects) using dotfield notation for key names.  Default: false.

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.


Query syntax
------------
Examples of query parameter "**q**":


Simple queries
""""""""""""""

search for everything::

    q=coronavirus                        # search all default fields for term


Fielded queries
"""""""""""""""
::

    q=mondo.synonyms:PCD               # for matching value on a specific field

    q=mondo.synonyms:(PCD)            # multiple values for a field
    q=mondo.synonyms:(PCD OR PIST)         # multiple values for a field using OR

    q=_exists_:ctd                        # having ctd field
    q=NOT _exists_:ctd                   # missing ctd field


.. Hint:: For a list of available fields, see :ref:`here <available_fields>`.


Range queries
"""""""""""""
::

    q=mondo.parents:[MONDO:0000001 TO MONDO:0000100]         # bounded range query


Wildcard queries
""""""""""""""""
Wildcard character "*" or "?" is supported in either simple queries or fielded queries::

    q=mondo.label:primary*

.. note:: Wildcard character can not be the first character. It will be ignored.


Scrolling queries
"""""""""""""""""
If you want to return ALL results of a very large query, sometimes the paging method described `above <#from>`_ can take too long.  In these cases, you can use a scrolling query.
This is a two-step process that turns off database sorting to allow very fast retrieval of all query results.  To begin a scrolling query, you first call the query
endpoint as you normally would, but with an extra parameter **fetch_all** = TRUE.  For example, a GET request to::

    http://mydisease.info/v1/query?q=_exists_:ctd&fields=ctd.mesh&fetch_all=TRUE

Returns the following object:

.. code-block:: json


    {
    "_scroll_id": "FGluY2x1ZGVfY29udGV4dF91dWlkDXF1ZXJ5QW5kRmV0Y2gBFklwVTV4UlU1U0YtcDhiQUhJdlNZSlEAAAAAS_3keRZuWFQtN1VRRlFQT2F5U2c0cjVrYmln",
    "took": 519,
    "total": 4876,
    "max_score": 1,
    "hits": [
        {
        "_id": "MONDO:0001913",
        "_score": 1,
        "ctd": {
            "mesh": "D009845"
        }
        },
        {
        "_id": "MONDO:0001926",
        "_score": 1,
        "ctd": {
            "mesh": "D014515"
        }
        },
        .
        .
        .
      ],
    }

At this point, the first 1000 hits have been returned (of ~11,000 total), and a scroll has been set up for your query.  To get the next batch of 1000 unordered results, simply execute a GET request to the following address, supplying the _scroll_id from the first step into the **scroll_id** parameter in the second step::

    http://mydisease.info/v1/query?scroll_id=cXVlcnlUaGVuRmV0Y2g7MTA7Njg4ODAwOTI6SmU0ck9oMTZUUHFyRXlYSTNPS2pMZzs2ODg4MDA5MTpKZTRyT2gxNlRQcXJFeVhJM09LakxnOzY4ODgwMDkzOkplNHJPaDE2VFBxckV5WEkzT0tqTGc7Njg4ODAwOTQ6SmU0ck9oMTZUUHFyRXlYSTNPS2pMZzs2ODg4MDEwMDpKZTRyT2gxNlRQcXJFeVhJM09LakxnOzY4ODgwMDk2OkplNHJPaDE2VFBxckV5WEkzT0tqTGc7Njg4ODAwOTg6SmU0ck9oMTZUUHFyRXlYSTNPS2pMZzs2ODg4MDA5NzpKZTRyT2gxNlRQcXJFeVhJM09LakxnOzY4ODgwMDk5OkplNHJPaDE2VFBxckV5WEkzT0tqTGc7Njg4ODAwOTU6SmU0ck9oMTZUUHFyRXlYSTNPS2pMZzswOw==

.. Hint:: Your scroll will remain active for 1 minute from the last time you requested results from it.  If your scroll expires before you get the last batch of results, you must re-request the scroll_id by setting **fetch_all** = TRUE as in step 1.

.. Hint:: When you need to use this "scrolling query" feature via "fetch_all" parameter, we recommend you to use our Python client "`biothings_client <packages.html>`_".

Boolean operators and grouping
""""""""""""""""""""""""""""""

You can use **AND**/**OR**/**NOT** boolean operators and grouping to form complicated queries::

    q=_exists_:ctd AND _exists_:mondo                                AND operator
    q=_exists_:ctd AND NOT _exists_:mondo                           NOT operator
    q=_exists_:ctd OR (_exists_:mondo AND _exists_:hpo)             grouping with ()


Escaping reserved characters
""""""""""""""""""""""""""""
If you need to use these reserved characters in your query, make sure to escape them using a back slash ("\\")::

    + - = && || > < ! ( ) { } [ ] ^ " ~ * ? : \ /



Returned object
---------------

A GET request like this::

    http://mydisease.info/v1/query?q=mondo.label:cardiomyopathy&fields=mondo.label

should return hits as:

.. code-block:: json

    {
        'took': 4,
        'total': 14,
        'max_score': 6.271054,
        'hits': [
            {
                '_id': 'C4277690',
                '_score': 6.271054
            },
            {
                '_id': 'MONDO:0017892',
                '_score': 6.271054,
                'mondo': {
                    'label': 'autosomal recessive myogenic arthrogryposis multiplex congenita'
                }
            },
            {
                '_id': 'MONDO:0009360',
                '_score': 6.271054,
                'mondo': {
                    'label': 'hydrocephalus, nonsyndromic, autosomal recessive 1'
                }
            },
            {
                '_id': 'MONDO:0010702',
                '_score': 6.271054,
                'mondo': {
                    'label': 'orofaciodigital syndrome I'
                }
            },
            {
                '_id': 'MONDO:0010704',
                '_score': 6.271054,
                'mondo': {
                    'label': 'otopalatodigital syndrome type 1'
                }
            },
            {
                '_id': 'MONDO:0016023',
                '_score': 6.271054,
                'mondo': {
                    'label': 'ocular coloboma'
                }
            },
            {
                '_id': 'MONDO:0010176',
                '_score': 6.271054,
                'mondo': {
                    'label': 'orofaciodigital syndrome type 6'
                }
            },
            {
                '_id': 'MONDO:0010265',
                '_score': 6.271054,
                'mondo': {
                    'label': 'Simpson-Golabi-Behmel syndrome type 2'
                }
            },
            {
                '_id': 'MONDO:0010320',
                '_score': 6.271054,
                'mondo': {
                    'label': 'retinitis pigmentosa 23'
                }
            },
            {
                '_id': 'MONDO:0010431',
                '_score': 6.271054,
                'mondo': {
                    'label': 'Joubert syndrome 10'
                }
            }
        ]
    }

"**total**" in the output gives the total number of matching hits, while the actual hits are returned under "**hits**" field. "**size**" parameter controls how many hits will be returned in one request (default is 10). Adjust "**size**" parameter and "**from**" parameter to retrieve the additional hits.

Faceted queries
----------------
If you need to perform a faceted query, you can pass an optional "`facets <#facets>`_" parameter.

A GET request like this::

    http://mydisease.info/v1/query?q=mondo.label:cardiomyopathy&facets=mondo.parents&size=0

should return hits as:

.. code-block:: json

    {
        "took": 531,
        "total": 189,
        "max_score": null,
        "facets": {
            "mondo.parents": {
            "_type": "terms",
            "terms": [
                {
                "count": 42,
                "term": "mondo:0700335"
                },
                {
                "count": 30,
                "term": "mondo:0024573"
                },
                {
                "count": 11,
                "term": "mondo:0016333"
                },
                {
                "count": 11,
                "term": "mondo:1010010"
                },
                {
                "count": 10,
                "term": "mondo:0004994"
                },
                {
                "count": 9,
                "term": "mondo:1010015"
                },
                {
                "count": 9,
                "term": "mondo:1011321"
                },
                {
                "count": 8,
                "term": "mondo:0002254"
                },
                {
                "count": 8,
                "term": "mondo:1010011"
                },
                {
                "count": 5,
                "term": "mondo:0003847"
                }
            ],
            "other": 107,
            "missing": 0,
            "total": 143
            }
        }
    }


Batch queries via POST
======================

Although making simple GET requests above to our disease query service is sufficient for most use cases,
there are times you might find it more efficient to make batch queries (e.g., retrieving disease
annotation for multiple diseases). Fortunately, you can also make batch queries via POST requests when you
need::


    URL: http://mydisease.info/v1/query
    HTTP method:  POST


Query parameters
----------------

q
"""
    Required, multiple query terms seperated by comma (also support "+" or white space), but no wildcard, e.g., 'q=SDUQYLNIPVEERB-QPPQHZFASA-N,SESFRYSPDFLNCH-UHFFFAOYSA-N'

scopes
""""""
    Optional, specify one or more fields (separated by comma) as the search "scopes", e.g., "scopes=ctd".  The available "fields" can be passed to "**scopes**" parameter are
    :ref:`listed here <available_fields>`. Default:

fields
""""""
    Optional, a comma-separated string to limit the fields returned from the matching disease hits. The supported field names can be found from any disease object. Note that it supports dot notation, and wildcards as well, e.g., you can pass "ctd", "mondo.label", or "mondo.xrefs.*". If "fields=all", all available fields will be returned. Default: "all".

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.

Example code
------------

Unlike GET requests, you can easily test them from browser, make a POST request is often done via a
piece of code. Here is a sample python snippet using `httplib2 <https://pypi.org/project/httplib2/>`_ module::

    import httplib2
    h = httplib2.Http()
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    params = 'q=DOID:14566,DOID:1240&scopes=disease_ontology.doid&fields=disease_ontology.name'
    res, con = h.request('http://mydisease.info/v1/query', 'POST', params, headers=headers)

or this example using `requests <http://docs.python-requests.org>`_ module::

    import requests
    params = {'q': 'DOID:14566,DOID:1240', 'scopes': 'disease_ontology.doid', 'fields': 'disease_ontology.name'}
    res = requests.post('http://mydisease.info/v1/query', params)
    con = res.json()

Returned object
---------------

Returned result (the value of "con" variable above) from above example code should look like this:

.. code-block:: json


    [
        {
            'query': 'DOID:14566',
            '_id': 'MONDO:0005070',
            '_score': 8.824187,
            'disease_ontology': {
                '_license': 'https://github.com/DiseaseOntology/HumanDiseaseOntology/blob/master/DO_LICENSE.txt',
                'name': 'disease of cellular proliferation'
            }
        },
        {
            'query': 'DOID:1240',
            '_id': 'MONDO:0005059',
            '_score': 8.824187,
            'disease_ontology': {
                '_license': 'https://github.com/DiseaseOntology/HumanDiseaseOntology/blob/master/DO_LICENSE.txt',
                'name': 'leukemia'
            }
        }
    ]

.. Tip:: "query" field in returned object indicates the matching query term.

If a query term has no match, it will return with "**notfound**" field as "**true**":

.. code-block:: json

      [
        ...,
        {'query': '...',
         'notfound': true},
        ...
      ]


.. raw:: html

    <div id="spacer" style="height:300px"></div>
