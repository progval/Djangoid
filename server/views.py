from django.http import HttpResponse, HttpResponseRedirect
from openid.server import server
from djangoid.server.djangoidstore import DjangoidStore
from django.conf import settings
from django.shortcuts import render_to_response
from users.models import DjangoidUser
import re

_identityRe = re.compile(settings.BASE_URL + "(?P<uid>[^/]+)/$")

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

def _getDjangoidUserFromIdentity(identity):
        uid = _identityRe.match(identity).groupdict()["uid"]
        print "Found uid: ", uid
        user = DjangoidUser.objects.filter(djangouser = uid)
        if not len(user) == 0:
                return user[0]
        return None

def endpoint(request):
        if request.META.has_key("HTTP_ACCEPT"):
                ct = request.META["HTTP_ACCEPT"]
                if ct.startswith("application/xrds+xml"):
                        return serveryadis(request)

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
                user = _getDjangoidUserFromIdentity(r.identity)
                if not user == None:
                        if user.authenticate(r.trust_root): #user logged in (using r.identity and r.trust_root)
                                response = r.answer(True)
                        elif r.immediate:
                                response = r.answer(False, settings.BASE_URL)
                else:
                        return HttpResponseRedirect(r.encodeToURL(settings.BASE_URL + "login/"))
        else:
                response = openidserver.handleRequest(r)

        return _convertOpenidServerResponse(response)

def serveryadis(request):
        res = render_to_response("server/yadis.xrds", {"server_url": settings.BASE_URL})
        res["Content-Type"] = "application/xrds+xml; charset=%s" % settings.DEFAULT_CHARSET
        return res
