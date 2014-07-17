from django.conf import settings
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.http import HttpResponsePermanentRedirect, Http404
from django.contrib.auth import authenticate, login
import re


class SSLRedirect(object):
    """
    Ova metoda treba da se override, cim se navede u setting kao midd.
    ovoj metodi najpre prosledim svaki zahtev kao request
    """

    def process_request(self, request):

        change_user = re.compile('.+/user/[1-9]+/$')

        # proveriti prvo da li je iskljucen u Setting,
        # ako jeste nista ne radi

        """

        :param request:
        :return:
        """

        if request.method == "POST":
            print(request.path)
            if request.path == "/admin/":
                if getattr(settings, 'SSL_ISKLJUCEN', False):
                    return None

                    # ako nema nijedna greska i ako vec nije https
                if not any((settings.DEBUG, request.is_secure())):
                    # uzmem URL iz request
                    url = request.build_absolute_uri(request.get_full_path())

                    username = request.POST['username']
                    password = request.POST['password']
                    user = authenticate(username=username, password=password)
                    if user is not None:
                        if user.is_active:
                            login(request, user)
                            # Redirect to a success page.
                            # change path
                            secure_url = url.replace('http://', 'https://')
                            # HttpResponsePermanentRedirect(url)
                            print(secure_url)

                            return HttpResponsePermanentRedirect(secure_url)
                        else:

                            pass

            elif change_user.search(request.path):
                try:
                    d = request.POST

                    print("last name  " + request.POST['last_name'])
                    username = request.POST['username']
                    user = None
                    try:
                        user = User.objects.get(username=username)
                    except user.DoesNotExist:
                        #vraca None, ako ga uhvati
                        return user

                    for attr, value in d.iteritems():

                        try:
                            if attr == 'is_staff':
                                if value == 'on':
                                    setattr(request.user, attr, True)
                                    request.user.save()
                                    continue
                                else:
                                    setattr(request.user, attr, False)
                                    request.user.save()
                                    continue

                            #print value
                            #konvertujem iz uString u String
                            attr = attr.decode('unicode-escape')
                            value = value.decode('unicode-escape')
                            setattr(request.user, attr, value)
                            request.user.save()
                            # ne postoji korisnik pa hvatam izuzetak
                        except Exception:
                            print attr + "greska"
                            # uhavatim izuzetak, django sam vrati da ne postoji
                            # middleware ne treba da radi nista u tom slucaju
                            return None

                    #provera da li je uradio nesto
                    print User.objects.get(username=username).last_name

                    return HttpResponsePermanentRedirect('https://127.0.0.1:8000/admin/auth/user/')
                except Http404:
                    pass

            else:
                return None



