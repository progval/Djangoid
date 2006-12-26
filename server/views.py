from django.http import HttpResponse
from openid.server import server
from djangoid.server.djangoidstore import DjangoidStore
from django.conf import settings
from django.shortcuts import render_to_response

openidserver = server.Server(DjangoidStore())

def _convertOpenidServerResponse(response):
        try:
                webresponse = openidserver.encodeResponse(response)
        except server.EncodingError, why:
                raise

        r = HttpResponse(webresponse.body)
        for header, value in webresponse.headers.iteritems():
                r[header] = value
        r.status_code = webresponse.code

        return r

def endpoint(request):
        query = {}
        for i in request.REQUEST.items():
                query[i[0]] = i[1]
        try:
                r = openidserver.decodeRequest(query)
        except server.ProtocolError, why:
                raise

        if r is None:
                return HttpResponse("about")

        if r.mode in ["checkid_immediate", "checkid_setup"]:
                if True: #user logged in
                        response = r.answer(True)
        else:
                response = openidserver.handleRequest(r)

        return _convertOpenidServerResponse(response)

def serveryadis(request):
        res = render_to_response("server/yadis.xrds", {"server_url": settings.BASE_URL})
        res["Content-Type"] = "application/xrds+xml; charset=%s" % settings.DEFAULT_CHARSET
        return res
