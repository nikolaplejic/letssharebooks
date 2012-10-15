#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python2 ## fucking arch

import ConfigParser, os, getpass, time, signal, logging, sys
import subprocess, time
import webbrowser
from lsboo import tunnelmanager as tunnelmanager

#imports so pyinstaller can pick dependency

#import dns
#from dns.rdtypes.IN import *
#from dns.rdtypes.ANY import *

logging.basicConfig(filename = 'lsbcli.log', level = logging.DEBUG, format ='%(asctime)s: %(filename)s >> %(levelname)s - %(message)s')

lsb_version = open("lsb_version", "r").read()

lsb_ascii = """
.        .             .                   .              .
|       _|_ |          |                   |              |
|    .-. |   .--.  .--.|--. .-.  .--..-.   |.-.  .-.  .-. |.-. .--.
|   (.-' |   `--.  `--.|  |(   | |  (.-'   |   )(   )(   )|-.' `--.
'---'`--'`-' `--'  `--''  `-`-'`-'   `--'  '`-'  `-'  `-' '  `-`--'
"""

def capture_control_c(signal, frame):
    logging.debug("Got Control+C signal!")
    lsb.xmpp.kill_the_tunnel()
    lsb.xmpp.disconnect()
    killing_calibre = subprocess.Popen(['kill', open("calibre.pid").read()], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    logging.debug("Killing calibre after shutting down: %s" % str(killing_calibre.communicate()))
    deleting_calibre = subprocess.Popen(['rm', 'calibre.pid'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    logging.debug("Deleting calibre.pid: %s" % str(deleting_calibre.communicate()))
    sys.exit(0)

def update_status(signal, frame):
    global lsb_version
    logging.debug("Got signal: %s" % signal)
    subprocess.call(['clear'])
    print lsb_ascii
    print "version: %s\n" % lsb_version
    print lsb.xmpp.get_status_message()
    print "To open URL in browser type 1, 2 or 3 and then [Enter] or 4 to exit: ",

if __name__=='__main__':
    lsbcli_pid = open("lsbcli.pid","w")
    lsbcli_pid.write(str(os.getpid()))
    lsbcli_pid.close()

    signal.signal(signal.SIGINT, capture_control_c)
    signal.signal(signal.SIGUSR1, update_status)

    lsb_config = ConfigParser.SafeConfigParser()

    if os.path.exists("lsbcli.conf"):
        lsb_config.read("lsbcli.conf")
    else:
        lsb_config.add_section('letsshareconfig')
        lsb_config.set('letsshareconfig', 'jid', raw_input("Username: "))
        lsb_config.set('letsshareconfig', 'password', getpass.getpass("Password: "))
        lsb_config.set('letsshareconfig', 'nick', raw_input("Nick: "))
        lsb_config.set('letsshareconfig', 'room', "letssharebooks@conference.jabber.snipdom.net")
        with open("lsbcli.conf", 'w') as fp:
            lsb_config.write(fp)

    lsb = tunnelmanager.LSBooks()
    lsb.setup_mucbot(lsb_config.get("letsshareconfig", "jid"), lsb_config.get("letsshareconfig", "password"), lsb_config.get("letsshareconfig", "room"), lsb_config.get("letsshareconfig","nick"))

    if lsb.jabber_connect():
        lsb.xmpp.start_calibre_server(3000)
        time.sleep(2)
        lsb.xmpp.ask_for_slot()
    else:
        print "Didn't connect..."
        sys.exit(0)

    while True:
        def check_your_browser():
            print '\033[2A'
            print "Check your browser!\033[0K"
            time.sleep(2)
            print '\033[2A'
            os.kill(int(open("lsbcli.pid").read()), signal.SIGUSR1)

        def open_in_browser(url):
            try:
                webbrowser.open(url)
            except:
                logging.debug("Strange webbrowser GConf Error")

        try:
            user_input = raw_input()
            #user_input = raw_input("To open URL in browser type 1, 2, 3 or 4 and then [Enter] or 5 to exit: ")
        except EOFError as err:
            logging.debug("Strange raw_input bug saying: %s" % err)
            user_input = "ut98awr"
        if user_input == "1":
            open_in_browser("https://%s" % lsb.xmpp.url)
            check_your_browser()
        elif user_input == "2":
            open_in_browser(lsb.xmpp.local_url)
            check_your_browser()
        elif user_input == "3":
            open_in_browser(lsb.xmpp.chat_url)
            check_your_browser()
        elif user_input == "4":
            os.kill(int(open("lsbcli.pid").read()), signal.SIGINT)
        elif user_input == "ut98awr":
            pass
        else:
            print '\033[2A'
            print "Type only 1, 2, 3 or 4 and then [Enter]\033[0K"
            print '\033[2A'
            time.sleep(2)
        time.sleep(.1)