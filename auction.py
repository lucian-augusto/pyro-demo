import datetime

class Auciton(object):
    def __init__(self, product_code, product_name, seller_name, seller_uri, initial_price, description, duration, signature):
        self.product_code = product_code
        self.product_name = product_name
        self.seller_name = seller_name
        self.seller_uri = seller_uri
        self.price = initial_price
        self.start_date_time = datetime.datetime.now()
        self.end_date_time = self.start_date_time + datetime.timedelta(seconds=duration)
        self.duration = duration
        self.description = description
        self.signature = signature
        self.watch_list = {}
        self.current_buyer = ""

    def get_auction_info(self):
        return (
            f"Product code: {self.product_code}\n"
            f"Item: {self.product_name}\n"
            f"Seller Name: {self.seller_name}\n"
            f"Price: {self.price}\n"
            f"Time left: {self.end_date_time - datetime.datetime.now()}\n"
            f"Description: {self.description}\n"
            f"Current Buyer: {self.current_buyer}"
        )

    def validate_offer(self, amount):
        if (datetime.datetime.now() > self.end_date_time):
            return False

        current_price = self.price[0] if type(self.price) is tuple else self.price
        return amount > current_price

    def add_offer(self, buyer_name, amount):
        if self.validate_offer(amount):
            self.current_buyer = buyer_name
            self.price = amount
            return True

        return False
