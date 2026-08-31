import random
import datetime
import pytz
from models.option import Option
from models.poll import Poll
import connection_pool
import database


MENU_PROMPT = """ ------- Menu ------

1) Create a new poll
2) List open polls
3) Vote on a poll
4) Show poll votes
5) Select a random winner from a poll option

Press 'esc' to Exit.

Enter your choice: 
"""

NEW_OPTION_PROMPT = "Enter new option (or leave blank to stop adding options): "

def create_tables():
    with connection_pool.get_connection() as conn:
        database.create_tables(conn)

def prompt_create_poll():
    poll_title = input("Enter poll title: ")
    poll_author = input("Enter poll's author: ")

    poll = Poll(poll_title, poll_author)
    poll.save()

    while new_option := input(NEW_OPTION_PROMPT):
        poll.add_option(new_option)

def prompt_list_polls():
    print("List of polls:")
    for poll in Poll.get_all():
        print(f"{poll.id}: {poll.text} by {poll.owner}")

def _prompt_print_poll_options(options: list[Option]):
    print("Available options in the selected poll:")
    for option in options:
        print(f"{option.id}: {option.text}")

def prompt_add_poll_vote():
    username = input("Who would like to vote? ")
    poll_id = int(input("What poll would you to vote for: "))
    poll = Poll.get(poll_id)
    _prompt_print_poll_options(poll.options)

    option_id = int(input("What option would you like to vote? "))
    Option.get(option_id).vote(username)

def prompt_show_poll_votes():
    poll_id = int(input("For what poll would you like to see the votes? "))
    poll = Poll.get(poll_id)
    options = poll.options
    votes_per_option = [len(option.votes) for option in options]
    total_votes = sum(votes_per_option)

    try:
        for option, votes in zip(options, votes_per_option):
            percentage = votes / total_votes * 100
            print(f"Option: '{option.text}' has {votes} votes (percentage: {percentage:.2f}%)")

    except ZeroDivisionError:
        print("No votes yet in this poll")

    input_log = input("Would you like to see the logs for this option? (y/n): ").lower()
    if input_log == 'y':
        for option in options:
            print(f"------ {option.text} ------")
            for vote in option.votes:
                naive_time = datetime.datetime.fromtimestamp(vote[2])
                utc_date = pytz.utc.localize(naive_time)
                local_date = utc_date.astimezone(pytz.timezone('Europe/London')).strftime('%Y-%m-%d %H:%M')
                print(f"\t {vote[0]} voted on {local_date}")



def prompt_select_random_winner():
    poll_id = int(input("What poll would you like to select a voter from? "))
    poll = Poll.get(poll_id)
    _prompt_print_poll_options(poll.options)

    option_id = int(input("What option would you like to select a voter for? "))
    voters = Option.get(option_id).votes
    random_winner = random.choice(voters)
    print(f"Your random winner is {random_winner[0]}.")



MENU_OPTIONS = {
    '1' : prompt_create_poll,
    '2' : prompt_list_polls,
    '3' : prompt_add_poll_vote,
    '4' : prompt_show_poll_votes,
    '5' : prompt_select_random_winner
}

def menu():
    print("Welcome to the poll app!")
    create_tables()

    while (user_input := input(MENU_PROMPT).lower()) != 'esc':
        try:
            MENU_OPTIONS[user_input]()
            print("\n")
        except KeyError:
            print("Invalid choice, please try again.")

    print("Exiting app...")

menu()
