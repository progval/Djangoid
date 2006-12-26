from django.shortcuts import render_to_response
from django.conf import settings

def useryadis(request, uid):
        res = render_to_response("users/yadis.xrds", {"server_url": settings.BASE_URL, "uid": uid})
        mimetype = "application/xrds+xml; charset=%s" % settings.DEFAULT_CHARSET
        res["Content-Type"] = mimetype
        return res

def userpage(request, uid):
        res = render_to_response("users/userpage.html", {"server_url": settings.BASE_URL, "uid": uid})
        res["X-XRDS-Location"] = settings.BASE_URL + uid + "/yadis/"
        return res
