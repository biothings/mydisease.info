def get_release(self):
    import requests

    res = requests.get(
        "https://www.disgenet.org/static/disgenet_ap1/files/downloads/readme.txt"
    )
    try:
        last_modified = res.headers.get(
            "Last-Modified", "Thu, 07 May 2020 13:40:12 GMT"
        )
        return last_modified.split(",")[-1].split(":")[0][:-2].strip()
    except:
        return "07 May 2020"