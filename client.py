from time import sleep
from Pyro5.api import expose, callback, Daemon, locate_ns, Proxy
from user import User
import threading

def print_welcome_message():
    print('''Welcome to the Auction House
Please, follow the instrucitons, have fun and good luck!!!
    ''')

def show_menu():
    print('''Please select one of the following options:
    1 - Check active auctions
    2 - Create new auction
    3 - Make an offer for an auction
    0 - Exit''')

def capture_input_selection():
    option = input("Option: ")
    return int(option)

def create_new_user(server, daemon):
    name = input("Please, enter your username: ")
    user = User(name)
    user_reference = daemon.register(user)
    user.set_reference_uri(user_reference)

    thread = threading.Thread(target=User.thread_loop, args=(daemon, ))
    thread.daemon = True
    thread.start()

    server.register_new_user(user.get_name(), user.get_public_key(), user.get_reference_uri())
    return user

def list_active_auctions(user, server):
    server.list_auctions(user.get_name())

def register_new_auction(user, server):
    product_code = input("Please enter the product code: ")
    product_name = input("Please enter the product name: " )
    descprition = input("Please enter a description for the product: ")
    initial_offer = float(input("Please enter an initial offer: "))
    duration = int(input("Please enter a duration for your auction (in seconds): "))

    server.create_new_auction(product_code, product_name, user.get_name(), user.get_reference_uri(), initial_offer, descprition, duration, user.sign_message(user.get_name()))

def create_new_offer(user, server):
    product_code = input("Please enter the product code: ")
    amount = float(input("Please enter your offer: "))

    server.new_offer(product_code, amount, user.get_name(), user.get_reference_uri(), user.sign_message(user.get_name()))

def main():
    name_server = locate_ns()
    auction_house_server_uri = name_server.lookup("AuctionHouse")
    auction_house_server = Proxy(auction_house_server_uri)
    daemon = Daemon()

    print_welcome_message()
    user = create_new_user(auction_house_server, daemon)
    option = -1
    while (option != 0):
        show_menu()
        option = capture_input_selection()
        if (option == 1):
            list_active_auctions(user, auction_house_server)

        elif option == 2:
            register_new_auction(user, auction_house_server)

        elif option == 3:
            create_new_offer(user, auction_house_server)

        elif option == 0:
            print("Bye!")

main()
