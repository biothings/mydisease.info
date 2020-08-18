Disease annotation service
*************************************

This page describes the reference for the MyDisease.info disease annotation web
service.  It's also recommended to try it live on our `interactive API page <http://mydisease.info/v1/api>`_.


Service endpoint
=================
::

    http://mydisease.info/v1/disease


GET request
==================

Obtaining the disease annotation via our web service is as simple as calling this URL::

    http://mydisease.info/v1/disease/<diseaseid>

**diseaseid** above is any one of several common disease identifiers: `MONDO <https://mondo.monarchinitiative.org/>`_.

By default, this will return the complete disease annotation object in JSON format. See `here <#returned-object>`_ for an example and :ref:`here <disease_object>` for more details. If the input **diseaseid** is not valid, 404 (NOT FOUND) will be returned.

Optionally, you can pass a "**fields**" parameter to return only the annotation you want (by filtering returned object fields)::

    http://mydisease.info/v1/disease/MONDO:0016575?fields=mondo

"**fields**" accepts any attributes (a.k.a fields) available from the disease object. Multiple attributes should be separated by commas. If an attribute is not available for a specific disease object, it will be ignored. Note that the attribute names are case-sensitive.

Just like the `disease query service <disease_query_service.html>`_, you can also pass a "**callback**" parameter to make a `JSONP <http://ajaxian.com/archives/jsonp-json-with-padding>`_ call.


Query parameters
-----------------

fields
""""""""
    Optional, can be a comma-separated fields to limit the fields returned from the disease object. If "fields=all", all available fields will be returned. Note that it supports dot notation as well, e.g., you can pass "mondo.label". Default: "fields=all".

callback
"""""""""
    Optional, you can pass a "**callback**" parameter to make a `JSONP <http://ajaxian.com/archives/jsonp-json-with-padding>`_ call.

filter
"""""""
    Alias for "fields" parameter.

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.

-----------------

Returned object
---------------

A GET request like this::

    http://mydisease.info/v1/disease/MONDO:0016575?fields=mondo

should return a disease object below:

.. container :: disease-object-container

    .. include :: disease_object.json


Batch queries via POST
======================

Although making simple GET requests above to our disease query service is sufficient in most use cases,
there are some times you might find it's easier to batch query (e.g., retrieving disease
annotations for multiple diseases). Fortunately, you can also make batch queries via POST requests when you
need::


    URL: http://mydisease.info/v1/disease
    HTTP method:  POST


Query parameters
----------------

ids
"""""
    Required. Accept multiple disease ids separated by comma, e.g., "ids=SDUQYLNIPVEERB-QPPQHZFASA-N,SESFRYSPDFLNCH-UHFFFAOYSA-N,SHGAZHPCJJPHSC-ZVCIMWCZSA-N". Note that currently we only take the input ids up to **1000** maximum, the rest will be omitted.

fields
"""""""
    Optional, can be a comma-separated fields to limit the fields returned from the matching hits.
    If “fields=all”, all available fields will be returned. Note that it supports dot notation as well, e.g., you can pass "ctd" or "mondo.label". Default: "all".

email
""""""
    Optional, if you are regular users of our services, we encourage you to provide us an email, so that we can better track the usage or follow up with you.

Example code
------------

Unlike GET requests, you can easily test them from browser, make a POST request is often done via a
piece of code, still trivial of course. Here is a sample python snippe using `httplib2 <https://pypi.org/project/httplib2/>`_ modulet::

    import httplib2
    h = httplib2.Http()
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    params = 'ids=MONDO:0016575,MONDO:0020753,MONDO:0011996&fields=mondo.xrefs.doid'
    res, con = h.request('http://mydisease.info/v1/disease', 'POST', params, headers=headers)

or this example using `requests <http://docs.python-requests.org>`_ module::

    import requests
    params = {'ids': 'MONDO:0016575,MONDO:0020753,MONDO:0011996', 'fields': 'mondo.xrefs.doid'}
    res = requests.post('http://mydisease.info/v1/disease', params)
    con = res.json()


Returned object
---------------

Returned result (the value of "con" variable above) from above example code should look like this:


.. code-block :: json

    [
        {
            'query': 'MONDO:0016575',
            '_id': 'MONDO:0016575',
            '_version': 1,
            'mondo': {
                'xrefs': {
                    'doid': 'DOID:0050144'
                }
            }
        },
        {
            'query': 'MONDO:0020753',
            '_id': 'MONDO:0020753',
            '_version': 1,
            'mondo': {
                'xrefs': {
                    'doid': 'DOID:0080599'
                }
            }
        },
        {
            'query': 'MONDO:0011996',
            '_id': 'MONDO:0011996',
            '_version': 1,
            'mondo': {
                'xrefs': {
                    'doid': 'DOID:8552'
                }
            }
        }
    ]

.. raw:: html

    <div id="spacer" style="height:300px"></div>
