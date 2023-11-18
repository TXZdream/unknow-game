from unknown.service import UnknownService

GAME_PATH = "data/"


def main():
    unknown_name = input("Your unknown game name is: ")
    unknown_srv = UnknownService(f"{GAME_PATH}{unknown_name}")
    last_operation = None
    while True:
        operation = input("""Available Operations are(* means use of gpt):
    - iter(n): iter to the next turn.
    - *update(u): update the unknown game with your sentence.
    - *describe(t): describe current unknown game.
    - show(v): show current unknown game data and iterators.
Your operation: """)
        operation = operation.strip()
        if not operation:
            operation = last_operation
        else:
            last_operation = operation
        if operation =='n' or operation == "iter":
            unknown_srv.iter()
        elif operation =='u' or operation == "update":
            word = input("Update sentence: ")
            unknown_srv.update_data_and_iterator(word)
        elif operation =='t' or operation == "describe":
            unknown_srv.describe()
        elif operation =='v' or operation == "show":
            unknown_srv.show()
        else:
            print("invalid operation")


if __name__ == "__main__":
    main()
