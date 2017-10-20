#!/usr/bin/env python3

"""Python Gmail thread-warning module based on Google quickstart guide."""

import os
import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    FLAGS = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    FLAGS = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail Fear of Missing Address (FOMA)'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if FLAGS:
            credentials = tools.run_flow(flow, store, FLAGS)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def get_thread(service):
    """
    Get a specified thread.
    TODO: Get the thread_id from the URL Load.
    """
    thread_id = '15f3625d1fec23a4'
    return service.users().threads().get(
        userId='me',
        id=thread_id,
        format='metadata',
        metadataHeaders=['To', 'From', 'Cc', 'Bcc'],
    ).execute()

def get_record(thread, position):
    """
    Get a historical record from a thread object.
    """
    return [
        {
            'headers': record.get('payload', {}).get('headers', []),
            'historyId': record.get('historyId')
        }
        for record in thread.get('messages')
        if record.get('historyId') == position
    ][0]

def get_first_message(thread):
    """Retrieve the first record from a thread."""
    return ''.join(str(x) for x in
                   min([[int(historyId) for historyId in messages.get('historyId')]
                        for messages in thread.get('messages')]))

def get_email_addresses(record):
    """Get the email addresses in a given thread record."""
    emails = set()
    for field in record.get('headers'):
        emails.update(field.get('value').split(','))
    return emails

def compare_records(first, latest):
    """
    Tell the difference between 2 sets of records' email addresses.
    """
    emails_missing = get_email_addresses(first) - get_email_addresses(latest)
    if emails_missing:
        print(emails_missing)

def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    thread = get_thread(service)
    first = get_record(thread, get_first_message(thread))
    latest = get_record(thread, thread.get('historyId'))
    compare_records(first, latest)


if __name__ == '__main__':
    main()
