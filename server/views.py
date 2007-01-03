from django.http import HttpResponse, HttpResponseRedirect
from openid.server import server
from djangoid.server.djangoidstore import DjangoidStore
from django.conf import settings
from django.shortcuts import render_to_response
from djangoid.users.models import DjangoidUser
import re

#Regex to extract username out of identity delegate URI, like
#       http://id.nicolast.be/nicolas/
#                             ^^^^^^^
#Watch the trailing /
_identityRe = re.compile(settings.BASE_URL + "(?P<uid>[^/]+)/$")

#Global OpenID server instance, using a DjangoidStore object as container
openidserver = server.Server(DjangoidStore())

#Convert an OpenID server response to a Django-compatible HttpResponse:
#copy HTTP headers, and payload
def convertOpenidServerResponse(response):
        try:
                webresponse = openidserver.encodeResponse(response)
        except server.EncodingError, why:
                raise

        r = HttpResponse(webresponse.body)
        for header, value in webresponse.headers.iteritems():
                r[header] = value
        r.status_code = webresponse.code

        return r

#Get a DjangoidUser object, based on a delegate URI
def getDjangoidUserFromIdentity(identity):
        uid = _identityRe.match(identity).groupdict()["uid"]
        user = DjangoidUser.objects.filter(djangouser = uid)
        if not len(user) == 0:
                return user[0]
        else:
                raise Exception, "User " + uid + " unknown"

#Server endpoint. URI: http://id.nicolast.be/
def endpoint(request):
        #If this is (most likely) a YADIS request, handle it using the YADIS view function
        if request.META.has_key("HTTP_ACCEPT"):
                ct = request.META["HTTP_ACCEPT"]
                if ct.startswith("application/xrds+xml"):
                        return serveryadis(request)

        #Copy over all query (GET and POST) key-value pairs, so we can pass them to out OpenID server.
        #request.REQUEST.copy() seems not to work, as openidserver.decodeRequest seems to use some function
        #on the passed object that's not implemented in the copied object.
        query = {}
        for i in request.REQUEST.items():
                query[i[0]] = i[1]
        try:
                r = openidserver.decodeRequest(query)
        except server.ProtocolError, why:
                raise

        #If the request wasnt a valid OpenID server request, render some static page.
        #TODO: use render_to_response("about.html")
        if r is None:
                return HttpResponse("about")

        #Check whether we got to do anything...
        if r.mode in ["checkid_immediate", "checkid_setup"]:
                #Get a DjangoidUser, based on the identity URI
                user = getDjangoidUserFromIdentity(r.identity)
                #If the user is not in our database yet, or he's not authenticated (or authenticated using some other
                #username), redirect to the login page. This is part of the "users" application.
                #Make sure we pass all OpenID related information in the URL
                if not request.user or request.user.is_authenticated() == False:
                        return HttpResponseRedirect(r.encodeToURL(settings.BASE_URL + "login/"))
                if not request.user.username == user.djangouser:
                        raise Exception, "Logged in as " + request.user.username + " while expecting " + user.djangouser

                #Is the user authenticated, and does he trust this trust_root?
                if user.authenticate(r.trust_root): #user logged in (using r.identity and r.trust_root)
                        response = r.answer(True)
                #User is logged in, but hasnt added this trust_root to his list of permanently trusted roots.
                #If this is an immediate request, we can't ask the user now though. Reply with a failure, passing the
                #URI to which a second request (non-immediate) should be made. This is this same view.
                elif r.immediate:
                        response = r.answer(False, settings.BASE_URL)
                #Right, we got to ask the user whether he trusts this trust_root, and whether he wants to add it to his
                #list of permanently trusted roots. This is handled in the "users" application.
                else:
                        return HttpResponseRedirect(r.encodeToURL(settings.BASE_URL + "accept/"))
        #If not, let the OpenID server do everything for us :-)
        else:
                response = openidserver.handleRequest(r)

        return convertOpenidServerResponse(response)

#A server YADIS document is requested. I don't think this is widely used yet, but well... Let's just return it.
def serveryadis(request):
        res = render_to_response("server/yadis.xrds", {"server_url": settings.BASE_URL})
        res["Content-Type"] = "application/xrds+xml; charset=%s" % settings.DEFAULT_CHARSET
        return res
