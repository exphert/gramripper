import re, sys, os, json
import datetime
import requests
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from colorama import Fore, Style

RST = Style.RESET_ALL
DIM = Style.DIM

RED = Fore.RED
GRN = Fore.GREEN
YLW = Fore.YELLOW
BLU = Fore.BLUE
MGA = Fore.MAGENTA
CYN = Fore.CYAN

ok = f"{RST}[{CYN}+{RST}]"
info = f"{RST}[{MGA}info{RST}]"
success = f"{RST}[{GRN}✓{RST}]"
warning = f"{RST}[{YLW}-{RST}]"
error = f"{RST}[{RED}!{RST}]"


# Load environment variables
load_dotenv()
TO_CHAT_ID = os.getenv("TO_CHAT_ID")
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

SRC_PATH = os.path.join(os.path.dirname(__file__), 'src')
SESSION_DIR = os.path.join(os.path.dirname(__file__), "session")

if not os.path.exists(SRC_PATH):
    os.makedirs(SRC_PATH)

if not os.path.exists(SESSION_DIR):
    os.makedirs(SESSION_DIR)

TELEGRAM_API_URL = "https://api.telegram.org/bot"
SESSION_FILE = os.path.join(SRC_PATH, "session.json")
ENV_FILE = os.path.join(os.path.dirname(__file__), ".env")
TELETHON_SESSION = os.path.join(SRC_PATH, "ripper_session")


def color(string, color, wrap=None):
    global RST
    return f"{RST}{color}{string}{RST}" if not wrap else wrap.replace("STR", f"{RST}{color}{string}{RST}")


def generate_box(lines, length=78, title="", titleclr=Fore.YELLOW, pos="center", loc="top"):
    output = []
    undefined = (length == -1)
    length = 40 if undefined else length  # Default to 40 if undefined
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

    # Helper function to generate the title bar
    def title_bar(start, end, title, length, titleclr, pos, undefined):
        title_length = len(title) + 2  # Account for brackets []
        content_length = length - 2
        wrap_left = color("[", RST) if title else color('─', DIM)
        wrap_right = color("]", RST) if title else color('─', DIM)

        if pos == "center":
            pad = (content_length - title_length) // 2
            return f"{start}{'─' * pad}{wrap_left}{color(title, titleclr)}{wrap_right}{color(f"{'─' * pad}{end if not undefined else '»'}", DIM)}"

        elif pos == "right":
            pad = (content_length - title_length) - 1
            return f"{start}{'─' * pad}{wrap_left}{color(title, titleclr)}{wrap_right}{color(f"{end if not undefined else '─»'}", DIM)}"

        else:  # Default to "left"
            return f"{start}{wrap_left}{color(title, titleclr)}{wrap_right}{color(f"{'─' * (content_length - title_length)}{end if not undefined else '»'}", DIM)}"

    # Top Border
    if loc == "top":
        output.append(color(title_bar("┌", "┐", title, length, titleclr, pos, undefined), DIM))
    else:
        output.append(color(f"┌{'─' * (length - 2)}{'┐' if not undefined else '»'}", DIM))

    # Content
    for line in lines:
        line_length = len(ansi_escape.sub('', line))  # Strip ANSI escape sequences
        padding = length - line_length - 3  # Adjust padding
        output.append(f"{color('│', DIM)} {line}{' ' * padding}{color('│' if not undefined else '', DIM)}")

    # Bottom Border
    if loc == "bottom":
        output.append(color(title_bar("└", "┘", title, length, titleclr, pos, undefined), DIM))
    else:
        output.append(color(f"└{'─' * (length - 2)}{'┘' if not undefined else '»'}", DIM))

    return "\n".join(output)

def prompt(title, titleclr=Fore.CYAN, pos='left', before=""):
    lgth = (18 - (len(title) // 2))  # Adjusted calculation
    contentLen = (38 - len(f"[{title}]"))
    match (pos):
        case 'center':
            return f"{color(f'{before}┌{'─' * lgth}', DIM)}[{color(title, titleclr)}]{color(f"{'─' * lgth}»", DIM)}\n{color('└──', DIM)}{Fore.YELLOW}» "

        case 'rigth':
            return f"{color(f'{before}┌{'─' * (contentLen - 1)}', DIM)}[{color(title, titleclr)}]{color('─»', DIM)}\n{color('└──', DIM)}{Fore.YELLOW}» "

        case 'left' | _:
            return f"{color(f'{before}┌─', DIM)}[{color(title, titleclr)}]{color(f"{'─' * (contentLen - 1)}»", DIM)}\n{color('└──', DIM)}{Fore.YELLOW}» "

# Function to check if Telethon is authenticated
def is_telethon_authenticated():
    return os.path.exists(f"{TELETHON_SESSION}.session")


def get_session_filepath(bot_token, from_chat_id):
    """Returns the session file path for a specific bot session."""
    bot_token = parse_bot_token(bot_token)
    return os.path.join(SESSION_DIR, f"{bot_token.replace(':', '+')}_{from_chat_id}.json")


def load_sessions():
    """Loads all available session files from the 'sessions' directory."""
    sessions = {}
    for filename in os.listdir(SESSION_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(SESSION_DIR, filename)
            with open(filepath, "r") as f:
                session_data = json.load(f)
                sessions[filename] = session_data
    return sessions


def load_single_session(bot_token, from_chat_id):
    """Loads a single session file."""
    filepath = get_session_filepath(bot_token, from_chat_id)
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return None  # Return None if session file doesn't exist


def save_sessions(bot_token, from_chat_id, session_data):
    """Saves the session data to its corresponding file."""
    filepath = get_session_filepath(bot_token, from_chat_id)
    with open(filepath, "w") as f:
        json.dump(session_data, f, indent=4)


def init():
    global TO_CHAT_ID, API_ID, API_HASH

    # Function to log in to Telethon
    def telethon_login():
        global API_ID, API_HASH
        if not API_ID or not API_HASH:
            print(f"{warning} Please set API_ID and API_HASH in the .env file first.")
            return

        print(f"{info} Logging in to Telegram...")
        client = TelegramClient(TELETHON_SESSION, API_ID, API_HASH)

        with client:
            client.connect()
            if not client.is_user_authorized():
                phone = input(
                    f"{ok} Enter your phone number (with country code): ")
                try:
                    client.send_code_request(phone)
                    code = input(f"{ok} Enter the confirmation code: ")
                    try:
                        client.sign_in(phone, code)
                    except SessionPasswordNeededError:
                        password = input(f"{ok} Enter your 2FA password: ")
                        client.sign_in(password=password)

                    print(f"{success} Login successful! Telethon session saved.")
                except Exception as e:
                    print(f"{error} Login failed: {e}")

    if not os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "w") as f:
            f.write("{}")
            f.close()

    if not os.path.exists(ENV_FILE):
        envs = []
        inputs = input("Enter Telegram API_ID: ")
        envs.append(f"API_ID = {inputs}")
        inputs = input("Enter Telegram API_HASH: ")
        envs.append(f"API_HASH = {inputs}")
        inputs = input("Enter The Receiver Chat ID: ")
        envs.append(f"TO_CHAT_ID = {inputs}")

        with open(ENV_FILE, "w") as f:
            f.write("\n".join(envs))
            f.close()

        load_dotenv()
        TO_CHAT_ID = os.getenv("TO_CHAT_ID")
        API_ID = os.getenv("API_ID")
        API_HASH = os.getenv("API_HASH")

    # check env first
    if not TO_CHAT_ID or not API_ID or not API_HASH:
        print(
            f"{error} Please set the environment variables TO_CHAT_ID, API_ID, API_HASH")
        exit()

    # Ensure Telethon login before anything else
    if not is_telethon_authenticated():
        telethon_login()
        if not is_telethon_authenticated():
            print(f"{warning} Login failed. Exiting...")
            exit()


def parse_bot_token(raw_token):
    raw_token = raw_token.strip()
    if raw_token.lower().startswith("bot"):
        raw_token = raw_token[3:]
    return raw_token


def telethon_send_start(bot_token):
    global TELETHON_SESSION, API_ID, API_HASH
    bot_token = parse_bot_token(bot_token)

    with TelegramClient(TELETHON_SESSION, API_ID, API_HASH) as client:
        client.connect()

        bot_info = is_bot_online(parse_bot_token(bot_token))
        if not bot_info:
            print(f"{warning} Bot is offline. Try again.")
            return

        bot_username = bot_info.get("username", "Unknown")
        print(f"{success} [Telethon] Logged in with your account.")

        try:
            if not bot_username.startswith("@"):
                bot_username = "@" + bot_username
            # ✅ Ensure all async calls are d
            client.send_message(bot_username, "/start")
            print(f"{success} [Telethon] '/start' sent to {bot_username}.")
        except Exception as e:
            print(f"{error} [Telethon] Send error: {e}")
        finally:
            client.disconnect()  # ✅ Await disconnect properly


# Function to check if bot is online using /getMe
def is_bot_online(bot_token, returnType='filter'):
    bot_token = parse_bot_token(bot_token)
    url = f"{TELEGRAM_API_URL}{bot_token}/getMe"
    try:
        r = requests.get(url)
        data = r.json()
        if returnType == 'raw':
            return data
        if data.get("ok", False):
            return data["result"]
        else:
            print(f"{warning} Bot is offline or invalid token: {data}")
            return None
    except Exception as e:
        print(f"{error} Error checking bot status: {e}")
        return None

def get_bot_owner(bot_token, chat_id, returnType='filter'):
    bot_token = parse_bot_token(bot_token)
    url = f"{TELEGRAM_API_URL}{bot_token}/getChat?chat_id={chat_id}"
    r = requests.get(url)
    data = r.json()

    if returnType == 'raw':
        return data

    if data.get("ok", False):
        return {
            "first": data["result"].get("first_name", "Unknown"),
            "last": data["result"].get("last_name", ""),
            "type": data["result"].get("type", "Unknown")
        }
    else:
        return {
            "first": "Unknown",
            "last": "",
            "type": "Unknown"
        }


def checkbot():
    banner()
    print(generate_box([], -1, "Check Bot Status", titleclr=GRN))
    bot_token = ""
    try:
        while not bot_token:
            bot_token = input(prompt('Bot Token'))
        print("")
    except KeyboardInterrupt:
        return

    data = is_bot_online(bot_token, returnType='raw')
    print(f"\n{Style.RESET_ALL}{json.dumps(data, indent=4)}")
    input("\nPress ENTER to continue...")

def checkbot_chatid():
    banner()
    print(generate_box([], -1, "Check Bot Chat ID Status", titleclr=GRN))
    bot_token = ""
    from_chat_id = ""
    try:
        while not bot_token:
            bot_token = input(prompt('Bot Token'))
        print("")
        while not from_chat_id:
            from_chat_id = input(prompt('Bot Chat ID'))
        print("")
    except KeyboardInterrupt:
        return

    data = get_bot_owner(bot_token, from_chat_id, returnType='raw')
    print(f"\n{Style.RESET_ALL}{json.dumps(data, indent=4)}")
    input("\nPress ENTER to continue...")

def show_sessions():
    """Displays available session files."""
    banner()
    sessions = load_sessions()
    available_sessions = [
        k for k in sessions.keys() if not sessions[k].get("is_done")]

    if not available_sessions:
        input(f"{warning} No active sessions found.")
        return

    print(generate_box(
        [f"{ok} Available Sessions: {color(len(available_sessions), YLW)}"], -1, title='Info', titleclr=MGA, pos='left'))
    lists = []
    for idx, filename in enumerate(available_sessions, start=1):
        session_data = sessions[filename]
        lists.append(f"{color(idx, YLW, f"{DIM}[STR{DIM}]{RST}")} {session_data['first_name']} ({color(
            f"@{session_data['username']}", CYN)}) [Dumped: {color(session_data['last_message_id'], YLW)}/{color(session_data['last_updated_message_id'], GRN)}]")
    lists.append(f"{color("U", GRN, f"{DIM}[STR{DIM}]{RST}")} Update Session")
    lists.append(f"{color("ENTER", CYN, f"{DIM}[STR{DIM}]{RST}")} Back/Cancel")
    print(generate_box(lists, -1, title='List Session', pos='left'))
    choice = input(prompt('Select Session'))
    print("")
    if choice.isdigit():
        choice = int(choice) - 1
        if 0 <= choice < len(available_sessions):
            selected_session_file = available_sessions[choice]
            selected_session = sessions[selected_session_file]
            print(
                f"{info} Resuming session for {selected_session['first_name']} ({color(f"@{selected_session['username']}", CYN)})")
            continue_dumper(selected_session)
        else:
            print(f"{warning} Invalid choice.")
    if str(choice).lower() == "u":
        for ses in sessions:
            sessions[ses]['is_done'] = False
            sessions[ses]["last_updated_message_id"] = get_last_message_id(
                sessions[ses]['bot_token'])
            print(
                f"\n{ok} Sessions for {sessions[ses]['first_name']} ({color(f"@{sessions[ses]['username']}", CYN)}) updated.")
            save_sessions(sessions[ses]['bot_token'],
                          sessions[ses]['from_chat_id'], sessions[ses])
        input("\nAll Session Updated!. Press ENTER to continue...")
        show_sessions()

def new_dumper():
    banner()
    print(generate_box([], -1, "New Ripper", titleclr=GRN))
    bot_token = ""
    from_chat_id = ""

    try:
        while not bot_token:
            bot_token = input(prompt('Bot Token'))
        print("")
        while not from_chat_id:
            from_chat_id = input(prompt('Bot Chat ID'))
        print("")
    except KeyboardInterrupt:
        return

    bot_info = is_bot_online(parse_bot_token(bot_token))
    if not bot_info:
        print(f"{warning} Bot is offline. Try again.")
        return

    bot_username = bot_info.get("username", "Unknown")
    bot_first_name = bot_info.get("first_name", "Unknown")

    session = load_single_session(bot_token, from_chat_id)

    # If session exists, continue from last message ID
    if session:
        print(
            f"{info} Resuming session for {bot_first_name} ({color(f"@{bot_username}", CYN)})")
        session['last_updated_message_id'] = get_last_message_id(bot_token)
        continue_dumper(session)
        return

    # If no session, start fresh
    print(f"{info} Creating a new session...")
    last_message_id = 1
    last_updated_message_id = get_last_message_id(bot_token)

    session = {
        "bot_token": parse_bot_token(bot_token),
        "from_chat_id": from_chat_id,
        "bot_owner": get_bot_owner(bot_token, from_chat_id),
        "last_message_id": last_message_id,
        "last_updated_message_id": last_updated_message_id,
        "username": bot_username,
        "first_name": bot_first_name,
        "is_done": False
    }
    save_sessions(bot_token, from_chat_id, session)

    continue_dumper(session)

# Function to get the last message ID using Telegram's HTTP API


def get_last_message_id(bot_token):
    bot_token = parse_bot_token(bot_token)
    telethon_send_start(bot_token)  # dont remove this !!!
    url = f"{TELEGRAM_API_URL}{bot_token}/getUpdates"
    response = requests.get(url)

    if response.status_code == 200:
        updates = response.json()
        if updates.get("ok") and updates.get("result"):
            messages = [update["message"]
                        for update in updates["result"] if "message" in update]
            if messages:
                return messages[-1]["message_id"]  # Get the last message ID

    return 1  # Default if no valid messages found


def continue_dumper(session):
    print("")
    print(generate_box(
        [f"{ok} Bot Name: {color(session["first_name"], YLW)}", f"{ok} Username: {color(f"@{session["username"]}", CYN)}", f"{ok} Message : {color(session["last_updated_message_id"], GRN)} - Available messages detected"], -1, title='Bot Info', titleclr=MGA, pos='left'))

    start_from_message_id = input(prompt("Start From Message ID (Default if empty)", before="\n"))
    print("")
    if not start_from_message_id.isdigit() or not start_from_message_id:
        print(f"{info} Skipped. Defaulting to {session["last_message_id"]}.")
        start_from_message_id = session["last_message_id"]
    else:
        start_from_message_id = int(start_from_message_id)

    bot_token = session["bot_token"]
    from_chat_id = session["from_chat_id"]
    last_message_id = start_from_message_id
    last_updated_message_id = session["last_updated_message_id"]
    bot_owner = f"User: {color(" ".join([session["bot_owner"]["first"], session["bot_owner"]["last"]]), CYN)} Type: {color(session["bot_owner"]["type"], RED if session["bot_owner"]["type"].lower() == 'private' else GRN)}"

    print(f"{info} Dumping messages from {color(from_chat_id, GRN)} ({bot_owner})")
    print(f"{info} Dumping (starting at {color(last_message_id, YLW)})...\n")

    forward_success = 0
    forward_failed = 0

    try:
        while last_message_id <= last_updated_message_id:
            forward = forward_msg(bot_token, from_chat_id, TO_CHAT_ID, last_message_id)
            success = forward.get("ok", False)
            current_time = datetime.datetime.now().strftime("%H:%M:%S")  # Get current time

            if success:
                forward_success += 1
            else:
                forward_failed += 1

            last_message_id += 1
            session["last_message_id"] = last_message_id
            # Update only this session file
            save_sessions(bot_token, from_chat_id, session)

            sys.stdout.write(
                f"\r[{color(current_time, CYN)}] "  # Add timestamp
                # Message progress
                f"[ID: {color(last_message_id, YLW)}/{color(last_updated_message_id, GRN)}] "
                f"[Forwarded: {color(forward_success, GRN)}] "  # Success count
                f"[Failed: {color(forward_failed, RED)}]\r"  # Failed count
            )
            sys.stdout.flush()

        session["is_done"] = True
        save_sessions(bot_token, from_chat_id, session)  # Mark session as done
        print(f"{success} Dump completed!")

    except KeyboardInterrupt:
        session["is_done"] = False
        # Mark session as not completed
        save_sessions(bot_token, from_chat_id, session)

        print(f"\n\n{info} Stopping...")
        input(f"{info} Session Saved, press ENTER to continue...")


# Function to forward messages
def forward_msg(bot_token, from_chat_id, to_chat_id, message_id):
    url = f"{TELEGRAM_API_URL}{bot_token}/forwardMessage"
    payload = {
        "from_chat_id": from_chat_id,
        "chat_id": to_chat_id,
        "message_id": message_id
    }
    try:
        r = requests.post(url, json=payload)
        data = r.json()
        return data
    except Exception as e:
        print(f"{error} Forward error: {e}")
        return False


def banner():
    os.system("clear" if os.name == "nt" else "cls")
    print(f"""
{color(".|'''''|", CYN)}                           {color("'||'''|,", RED)}
{color("|| .", CYN)}                               {color(" ||   ||  ''", RED)}
{color("|| |''|| '||''|  '''|.  '||),,(||'", CYN)} {color(" ||...|'  ||  '||''|, '||''|, .|''|, '||''|", RED)}
{color("||    ||  ||    .|''||   || || ||", CYN)}  {color(" || \\\\    ||   ||  ||  ||  || ||..||  ||", RED)}
{color("`|....|' .||.   `|..||. .||    ||.", CYN)} {color(".||  \\\\. .||.  ||..|'  ||..|' `|...  .||.", RED)}
    {color("By @Exphert", RED)}                                   {color("||      ||", RED)}
            {color("github.com/exphert/gramripper", YLW)}        {color(".||     .||", RED)}      {color("v1.1", CYN)}
""")

def main_menu():
    init()
    try:
        while True:
            banner()
            status = "Authenticated" if is_telethon_authenticated() else "Not Logged In"
            print(f"""{generate_box([f"Status: {color(status, GRN if status.lower().startswith('auth') else RED)}"], -1)}
{generate_box([f"{color("1", YLW, f"{DIM}[STR{DIM}]{RST}")} New Ripper", f"{color("2", YLW, f"{DIM}[STR{DIM}]{RST}")} Saved Session", f"{color("3", YLW, f"{DIM}[STR{DIM}]{RST}")} Check Bot", f"{color("4", YLW, f"{DIM}[STR{DIM}]{RST}")} Check Bot Chat ID", f"{color("0", RED, f"{DIM}[STR{DIM}]{RST}")} Exit"], -1, title="Main Menus", titleclr=YLW)}""")

            choice = input(prompt('Select Menu'))
            if choice == "1":
                new_dumper()
            elif choice == "2":
                show_sessions()
            elif choice == "3":
                checkbot()
            elif choice == "4":
                checkbot_chatid()
            elif choice == "0":
                exit()
            else:
                print("{error} Invalid choice, try again.")

    except KeyboardInterrupt:
        print("\n{info} Exiting...".format(info=info))


if __name__ == "__main__":
    main_menu()
