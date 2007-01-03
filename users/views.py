#Djangoid - Django-based OpenID server/provider
#Copyright (C) 2006  Nicolas Trangez <ikke nicolast be>
#
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; either version 2 of the License.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
#EOL
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.conf import settings
from openid.server import server

from djangoid.server.views import openidserver, convertOpenidServerResponse, getDjangoidUserFromIdentity
from djangoid.users.models import TrustedRoot

def useryadis(request, uid):
        res = render_to_response("users/yadis.xrds", {"server_url": settings.BASE_URL, "uid": uid})
        mimetype = "application/xrds+xml; charset=%s" % settings.DEFAULT_CHARSET
        res["Content-Type"] = mimetype
        return res

def userpage(request, uid):
        #Check whether this is a YADIS request
        if request.META.has_key("HTTP_ACCEPT"):
                ct = request.META["HTTP_ACCEPT"]
                if ct.startswith("application/xrds+xml"):
                        return useryadis(request, uid)

        res = render_to_response("users/userpage.html", {"server_url": settings.BASE_URL, "uid": uid})
        res["X-XRDS-Location"] = settings.BASE_URL + uid + "/yadis/"
        return res

def testid(request):
        return userpage(request, "nicolas")

def accept(request):
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

        if r is None:
                return HttpResponse("Nothing here")

        if request.method == "GET":
                return render_to_response("users/accept_root.html", {"openid_request": r})

        if request.method == "POST":
                if request.POST.has_key("cancel"):
                        return convertOpenidServerResponse(r.answer(False))
                if request.POST.has_key("remember"):
                        user = getDjangoidUserFromIdentity(r.identity)
                        root = TrustedRoot.objects.get(root = r.trust_root)
                        user.trusted_roots.add(root)
                return convertOpenidServerResponse(r.answer(True))

