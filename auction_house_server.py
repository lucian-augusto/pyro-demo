from auction import Auciton
from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Pyro5.api import behavior, expose, Proxy, Daemon, locate_ns
import base64
import time

@behavior(instance_mode = "single")
class AuctionHouse(object):
    def __init__(self):
        self.auctions = {}
        self.user_reference_list = {}
        self.user_keys = {}

    @expose
    def register_new_user(self, user_name, user_key, user_uri):
        new_user = Proxy(user_uri)
        if user_name in self.user_reference_list:
           new_user.publish_notification(f"Error: User {user_name} already exists.")
           return

        self.user_reference_list[user_name] = user_uri
        self.user_keys[user_name] = user_key
        new_user.publish_notification(f"User {user_name} created")

    @expose
    def create_new_auction(self, product_code, product_name, seller_name, seller_uri, initial_price, description, duration, signature):
        if not self.validate_signature(seller_name, self.user_keys[seller_name], signature):
            print("Invalid signature")
            return

        if product_code in self.auctions:
            print(f"Auction code {product_code} already exists")
            return

        self.auctions[product_code] = Auciton(product_code, product_name, seller_name, seller_uri, initial_price, description, duration, signature)
        self.auctions[product_code].watch_list[seller_name] = seller_uri
        for name in self.user_reference_list.keys():
            user = Proxy(self.user_reference_list[name])
            user.publish_notification(f"Auction {product_code} created. Product: {product_name}")

    @expose
    def list_auctions(self, username):
        user_uri = self.user_reference_list[username]
        user = Proxy(user_uri)
        message = ""
        for auction_code in self.auctions.keys():
            message += self.auctions[auction_code].get_auction_info()
            message += "\n"

        user.publish_notification(message)

    @expose
    def new_offer(self, product_code, amount, username, user_uri, signature):
        user = Proxy(user_uri)
        if not self.validate_signature(username, self.user_keys[username], signature):
            user.publish_notification("Invalid signature")
            return

        for auction_code in self.auctions.keys():
            if (product_code == auction_code):
                auction = self.auctions[auction_code]
                if (auction.add_offer(username, amount)):
                    interested_users = auction.watch_list
                    if username not in interested_users.keys():
                        interested_users[username] = user_uri

                    for interested_user_name in interested_users.keys():
                        interested_user_uri = interested_users[interested_user_name]
                        interested_user = Proxy(interested_user_uri)
                        interested_user.publish_notification(f"Auction {auction_code} updated.")

                    self.auctions[auction_code].watch_list = interested_users
                else:
                    user.publish_notification("Invalid offer")

            else:
                user.publish_notification(f"Auction {product_code} does not exist")

        return

        

    def validate_signature(self, message, user_public_key, signature):
        message_hash = SHA256.new(message.encode("utf-8"))
        decoded_signature = base64.b64decode(signature["data"])
        imported_key = RSA.import_key(user_public_key)
        try:
            pkcs1_15.new(imported_key).verify(message_hash, decoded_signature)
            return True
        except:
            return False

def main():
    print("Starting Acution House Server...")
    daemon = Daemon()
    name_server = locate_ns()
    uri = daemon.register(AuctionHouse)
    print(f"Registering AuctionHouse at: {uri}...")
    name_server.register("AuctionHouse", uri)
    print("AuctionHouse is up...")
    daemon.requestLoop()

main()
