def get_release(self):
    import requests

    res = requests.get("http://ctdbase.org/reports/CTD_chemicals_diseases.csv.gz")
    try:
        last_modified = res.headers.get(
            "Last-Modified", "Thu, 01 Oct 2020 20:17:32 GMT"
        )
        return last_modified
    except:
        return "Thu, 01 Oct 2020 20:17:32 GMT"