from datetime import datetime
from optparse import make_option
from distutils.version import StrictVersion
import os
import ssl
import sys

from django.core.servers.basehttp import WSGIRequestHandler
from django.core.servers.basehttp import WSGIServer
from django.core.management.base import CommandError
from django.core.management.commands import runserver
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.utils.importlib import import_module
from django import get_version

try:
    from django.core.servers.basehttp import WSGIServerException
except ImportError:
    from socket import error as WSGIServerException

if StrictVersion(get_version()) >= StrictVersion('1.5'):
    from django.utils._os import upath
else:
    upath = unicode


class HTTPSServer(WSGIServer):
    def __init__(self, address, handler_cls, certificate, key):
        super(HTTPSServer, self).__init__(address, handler_cls)

        # otvorim novi soket, ondnosno prosledim mu sve sertifikate i kljuceve
        self.socket = ssl.wrap_socket(self.socket, certfile=certificate,
                                      keyfile=key, server_side=True,
                                      ssl_version=ssl.PROTOCOL_SSLv3,
                                      cert_reqs=ssl.CERT_NONE)


def daj_kljuc_i_sertifikate():
    """
    :return:
    """
    # importujem modul i vratim direktorijum
    app_module = import_module("servssl")
    # putanja do projekta
    mod_path = os.path.dirname(upath(app_module.__file__))
    #putanji dodam folder za sertifikatima
    ssl_dir = os.path.join(mod_path, "certs")
    return ssl_dir


# komanda za pokretanje treba da izgleda runserver --certificate /path --key /path
#da bi se klasa ponasala kao komanda mora da prima runserver.Command
class Command(runserver.Command):
    # prima sve opcije za odredjenu komandu
    # treba da izgleda runserver --certificate /path --key /path

    #pokrenem standardnu runserver i dodam --certificate /path --key /path

    option_list = runserver.Command.option_list + (
        make_option("--certificate",
                    default=os.path.join(daj_kljuc_i_sertifikate(),
                                         "server.crt"),
                    help="Putanja do sertifikata"),
        make_option("--key",
                    default=os.path.join(daj_kljuc_i_sertifikate(),
                                         "server.key"),
                    help="Putanja do kljuca")
    )


    #OVERRIDE
    def get_handler(self, *args, **options):
        """
        Proverim podesavanja u settings za handlere, ako je u settings podeseno
        use_static_handler=True vracam staticki u suprotnom default
        """
        handler = super(Command, self).get_handler(*args, **options)
        use_static_handler = options.get('use_static_handler', True)
        insecure_serving = options.get('insecure_serving', False)
        if use_static_handler:
            return StaticFilesHandler(handler)
        return handler

    def proveri_sertifikate(self, key_file, cert_file):

        if not os.path.exists(key_file):
            raise CommandError("Ne postoji sertifikat u : %s" % key_file)
        if not os.path.exists(cert_file):
            raise CommandError("Ne postoji sertifikat u %s" %
                               cert_file)

    #OVERRIDE
    def inner_run(self, *args, **options):

        key_file = options.get("key")
        cert_file = options.get("certificate")
        self.proveri_sertifikate(key_file, cert_file)

        from django.conf import settings
        from django.utils import translation

        #podzava nit za svakog klijenta
        threading = options.get('use_threading')
        shutdown_message = options.get('shutdown_message', '')
        #razlicite su comande za win i ostale
        quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'

        self.stdout.write("Proveravam modele..\n\n")
        self.validate(display_num_errors=True)
        self.stdout.write((
                              "%(started_at)s\n"
                              "Django verzija koja se koristi je : %(version)s, koriscenja podesavanja su u : %(settings)r\n"
                              "Startuje se SSL server na : https://%(addr)s:%(port)s/\n"
                              "SSL sertifikat %(cert)s\n"
                              "SSL kljuc: %(key)s\n"
                              "Za izlazak otkucajte sledecu komandu : %(quit_command)s.\n"
                          ) % {
                              "started_at": datetime.now().strftime('%B %d, %Y - %X'),
                              "version": self.get_version(),
                              "settings": settings.SETTINGS_MODULE,
                              "addr": self._raw_ipv6 and '[%s]' % self.addr or self.addr,
                              "port": self.port,
                              "quit_command": quit_command,
                              "cert": cert_file,
                              "key": key_file
                          })
        #proveri u settings podesavanja za jezik
        translation.activate(settings.LANGUAGE_CODE)

        #ako ne baci do ovde izuzetak startujem hendlere i server, i dodeljujem mu aplikaciju
        try:

            handler = self.get_handler(*args, **options)
            server = HTTPSServer((self.addr, int(self.port)),
                                 WSGIRequestHandler,
                                 cert_file, key_file)
            server.set_app(handler)
            server.serve_forever()

        except WSGIServerException, e:
            #specificiram greske moguce
            errors = {
                13: "Nemate pristup portu.",
                98: "Port je zauzet.",
                99: "That IP address can't be assigned-to.",
            }
            try:
                error_text = errors[e.args[0].args[0]]
            except (AttributeError, KeyError):
                error_text = str(e)
            self.stderr.write("Greska: %s" % error_text)
            #izadjem iz niti
            os._exit(1)
        except KeyboardInterrupt:
            if shutdown_message:
                self.stdout.write(shutdown_message)
            sys.exit(0)

