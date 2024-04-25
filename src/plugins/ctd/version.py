def get_release(self):
    import datetime

    import requests

    res = requests.get(
        "http://ctdbase.org/reports/CTD_chemicals_diseases.csv.gz")
    try:
        last_modified = res.headers.get(
            "Last-Modified", "Thu, 01 Oct 2020 20:17:32 GMT"
        )
        return datetime.datetime.strptime(
            last_modified, "%a, %d %b %Y %H:%M:%S %Z"
        ).strftime("%Y-%m-%d")
    except:
        return "Thu, 01 Oct 2020 20:17:32 GMT"
