<p align="center">
  <a href="" rel="noopener">
 <img height=200px src="/img/grimripper.png" alt="GrimRipper"></a>
</p>

---

<p align="center"> 
GramRipper is a Python-based tool designed to dump chat messages from Telegram bots using the forward method. It leverages the <b>Telegram Bot API</b> and <b>Telethon</b> to automate the process of capturing messages from malicious bots and forwarding them to your own Telegram account. This tool is particularly useful for analyzing or archiving bot interactions.
    </br> </br> 
    <img src="https://img.shields.io/badge/Python-3.x-ebcb8b?style=flat-square"/>  <img src="https://img.shields.io/badge/LICENSE-MIT-blue?style=flat-square"/> <img src="https://img.shields.io/badge/VERSION-1.1-a3be8c?style=flat-square"/><br/>
</p>

<p align='center'>
<a href="#features"><img src="https://img.shields.io/badge/features-2e3440?style=for-the-badge"/></a> <a href="#getting_started"><img src="https://img.shields.io/badge/Getting Started-2e3440?style=for-the-badge"/></a> <a href="#usage"><img src="https://img.shields.io/badge/Usage-2e3440?style=for-the-badge"/></a>
</p>  
      
## Features <a name = "features"></a>
- **Automated Message Forwarding**: Forwards messages from a target bot to your specified chat ID.
- **Session Management**: Saves and resumes sessions for ongoing message dumping.
- **Bot Status Check**: Verifies if a bot is online and retrieves its information.
- **User-Friendly Interface**: Provides a clear menu-driven interface for ease of use.
- **Customizable**: Supports multiple sessions and allows starting from a specific message ID.
- 
![screenshot](/img/poc.png)

## Disclaimer (Legal & Ethical Use)
This tool is intended for **educational and research purposes only**. The author is not responsible for any misuse of this tool. Use it at your own risk and ensure you have proper authorization before interacting with any Telegram bot or account. Unauthorized use of this tool may violate Telegram's terms of service and a

## Getting Started <a name = "getting_started"></a>
Before using GramRipper, ensure you have the following:

### Prerequisites
1. **Python 3.8 or higher** installed on your system.
2. A **Telegram account** with a phone number for authentication.
3. **API_ID** and **API_HASH** from [my.telegram.org](https://my.telegram.org/apps).
4. A **Telegram bot token** (optional, if you want to interact with bots).
5. A **chat ID** where forwarded messages will be sent.

### Installation <a name = "installation"></a>
1. Clone the repository:
```bash
$ git clone https://github.com/exphert/gramripper.git
$ cd gramripper
```

2. Install the required dependencies:
```bash
$ pip install -r requirements.txt
```

3. Setup (First-Time Setup):
  1. Run the script:
```bash
$ python GramRipper.py
```
  2. Follow the prompts to enter your:
    - API_ID and API_HASH (obtained from my.telegram.org).
    - Receiver Chat ID (the chat ID where forwarded messages will be sent).
  3. Authenticate with your Telegram account:
    - Enter your phone number when prompted.
    - Provide the OTP code sent to your Telegram account.
    - If 2FA is enabled, enter your 2FA password.
  4. The script will generate the following files:
    - .env: Stores your API_ID, API_HASH, and TO_CHAT_ID.
    - src/ripper_session.session: Telethon session file for authentication.
    - session/: Directory to store bot session data.

## Usage <a name="usage"></a>
1. Launch the script:
```bash
$ python GramRipper.py
```
2. Use the main menu to:
- New Ripper: Start a new message dump from a bot.
- Saved Session: Resume an existing session.
- Check Bot: Verify if a bot is online and retrieve its information.
- Check Bot Chat ID: Retrieve information about a bot's chat.
- Exit: Close the program.
3. Follow the on-screen prompts to configure and start the message dump.

## File Structure
```bash
GramRipper/
│   .env                     # Stores API_ID, API_HASH, and TO_CHAT_ID
│   GramRipper.py            # Main script
│
├───session/                 # Directory to store bot session data
│       (saved session files)
│
└───src/
        ripper_session.session  # Telethon session file for authentication
```
## Contributing
Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](https://license/) file for details.

## Reference
[matkap](https://github.com/0x6rss/matkap) GUI Version

## Acknowledgments
[Telethon](https://docs.telethon.dev/) for the Telegram client library.
[python-dotenv](https://pypi.org/project/python-dotenv/) for managing environment variables.

## Support
If you find this tool useful, consider giving it a ⭐ on GitHub. For questions or issues, please open an issue on the repository.

## Authors
- [@exphert](https://github.com/exphert) - Just Coding
