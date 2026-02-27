"""
Lippert_Email Version: 1.2

Function to email any errors from a Python script as well as writing them to a local logfile.txt.
This Script requires an active gmail user that has an App Password set up.
The default is the old lippert.lvlsvn@gmail.com address.
                    ____________________ DEV Notes _______________________

    - Credentials need to be encrypted and imported at some point, as to not have them hard coded in script.
                    ________________________________________________________

Requirements:
    - Execute the following lines in the terminal before attempting to run the code: 
        - pip freeze > requirements.txt
        - pip install -r requirements.txt
    - Script was built in and for Python 3.14.1, all errors on other versions are not accounted for.

Uses:
    - Put in Python packages and set variables in __init__.py for importing into any scripts.

"""

import smtplib
from datetime import date
import os
# Define config for logging email


def email_errors(send_to, subject, error_msg, script_name, log_path):

    # Set variables
    importDate = str(date.today())

    print(os.getcwd())

    gmail_user = "lippert.lvlsvn@gmail.com"
    gmail_pass = "cotddyatovchjpup"

    sent_from = gmail_user
    send_to = send_to.split(',')
    body = "AUTOMATED MESSAGE - DO NOT REPLY \n\n" + "An error in the " + script_name + " Script has caused it to exit.\n\n" + error_msg + "\n\n" + \
        r"Please correct the issue ASAP to allow the script to run to completion.  Refer to log file in " + \
        log_path.replace('.', '') + " for more information.\n\n\n"

# Check if single or multiple recipients
    if isinstance(send_to, list):
        msg_vars = (sent_from, ", ".join(send_to), subject, body)
    else:
        msg_vars = (sent_from, send_to, subject, body)

    email_text = """\
    From: %s
    To: %s
    Subject: %s
        
    Message: %s
    """ % msg_vars
    # For multiple recipients -  % (sent_from, ", ".join(to), subject, body)
    # For single recipient - % (sent_from, to, subject, body)
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_pass)
        server.sendmail(sent_from, send_to,
                        f"Subject: {subject}\n{email_text}")
        server.close()
        os.chdir(log_path)
        email_log = 'logfile.txt'
        print(email_log)
        logfile = open(email_log, 'a')
        logRow = str("\n\nERROR - SCRIPT FAILURE - There was an exception caught during " +
                     script_name + "- \n\t- " + importDate + " - \n\t- " + str(email_text)) + ' - \n'
        logfile.write(str(logRow))

        print('Email Sent!')
    except Exception as emailArgs:
        os.chdir(log_path)
        exception_log = 'script_logs.txt'
        logfile = open(exception_log, 'a')
        logRow = str("\n\nERROR - SCRIPT FAILURE - There was an exception caught during the email process for " +
                     script_name + "- \n\t- " + importDate + " - \n\t- " + str(emailArgs)) + ' - \n'
        logfile.write(str(logRow))
        print('Email FAILED')
