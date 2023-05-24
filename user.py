from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Pyro5.api import expose, callback

class User(object):
    def __init__(self, name):
        self.name = name
        self.key = RSA.generate(2048)
        self.reference_uri = ""

    def set_reference_uri(self, uri):
        self.reference_uri = uri

    @expose
    @callback
    def publish_notification(self, message):
        print(message, flush=True)

    def get_name(self):
        return self.name

    def get_reference_uri(self):
        return self.reference_uri

    def get_public_key(self):
        return self.key.publickey().export_key().decode("utf-8")

    def sign_message(self, message):
        message_hash = SHA256.new(message.encode("utf-8"))
        return pkcs1_15.new(self.key).sign(message_hash)

    def thread_loop(daemon):
        daemon.requestLoop()
