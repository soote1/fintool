"""
This module provides classes to fetch emails from email service
providers and to parse such emails into objects that can be
managed by the sync module. Supported clients and parsers are
defined in SUPPORTED_CLIENTS and SUPPORTED_PARSERS respectively.
The user of this module can use the build_client and build_parser
functions to create the corresponding instances.
"""
import os.path
import base64
import time
import html.parser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from fintool.logging import LoggingHelper


class Error(Exception):
    """
    Base class for errors in this module.
    """


class UnsupportedEmailProviderError(Error):
    """
    Raised when the user requested a client for an unsupported email provider.
    """


class UnsupportedEmailType(Error):
    """
    Raised when the client requested a parser for an unsupported email type.
    """


class MissingFieldError(Error):
    """
    Raised when the input object to create a type instance is missing a
    required field.
    """


class InvalidDateStringError(Error):
    """
    Raised when the user provides a date string with invalid format.
    """


class Email:
    """
    A type to define an email from a service provider.
    """
    UID = 'uid'
    CONTENT = 'content'

    def __init__(self, uid, content):
        """
        Initialize instance.
        """
        self.uid = uid
        self.content = content

    @classmethod
    def from_dict(cls, data):
        """
        Create an instance of Email class from a dict object.
        """
        try:
            return Email(data[cls.UID], data[cls.CONTENT])
        except KeyError as e:
            raise MissingFieldError(f'missing {e} field')


class GmailClient:
    """
    An implementation of a gmail client.
    """
    def __init__(self):
        """
        Initialize instance.
        """
        # If modifying these scopes, delete the file token.json.
        self._scopes = ['https://www.googleapis.com/auth/gmail.readonly']
        self._creds = self.load_credentials()
        self._service = build('gmail', 'v1', credentials=self._creds)
        self._logger = LoggingHelper.get_logger(self.__class__.__name__)

    def load_credentials(self):
        """
        Load token and credentials from json file.
        """
        credentials = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            credentials = Credentials.from_authorized_user_file(
                'token.json',
                self._scopes
            )
        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json',
                    self._scopes
                )
                credentials = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(credentials.to_json())

        return creds

    @staticmethod
    def base64_url_decode(inp):
        """
        Convert a set of bytes in base64 url format into a utf-8 string.
        """
        padding_factor = (4 - len(inp) % 4) % 4
        inp += "="*padding_factor
        return base64.b64decode(
            inp.translate(dict(zip(map(ord, u'-_'), u'+/')))
        ).decode()

    @staticmethod
    def create_date_filter(timestamp):
        """
        Create a date filter from a timestamp.
        """
        return f'after:{timestamp}' if timestamp else None

    def get_label_ids(self, lbl_names):
        """
        Return label ids matching with label_names.
        """
        results = self._service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        result = [lbl['id'] for lbl in labels if lbl['name'] in lbl_names]
        return result

    def list_messages(self, labels, after=None):
        """
        List messages from the given labels and filter them by date.
        """
        date_filter = self.create_date_filter(after)
        results = self._service.users().messages().list(
            userId='me',
            labelIds=labels,
            maxResults=500,  # TODO: need to load this from config
            q=date_filter
        ).execute()
        messages = results.get('messages', [])
        while 'nextPageToken' in results:
            results = self._service.users().messages().list(
                userId='me',
                labelIds=labels,
                pageToken=results['nextPageToken'],
                maxResults=500  # TODO: need to load this from config
            ).execute()

            messages += results.get('messages', [])

        return messages

    def get_message(self, message_id):
        """
        Get the contents of a message using the given message id.
        """
        return self._service.users().messages().get(
            userId='me',
            id=message_id,
        ).execute()

    def get_messages(self, labels, from_date):
        """
        List messages from labels. mime type should be passed as parameter
        """
        messages_html = []
        messages = self.list_messages(labels, after=from_date)

        if not messages:
            print('No messages found.')
            return messages_html

        for msg in messages:
            content = self.get_message(msg['id'])

            if content['payload']['mimeType'] == 'multipart/related':
                for part in content['payload']['parts']:
                    if part['mimeType'] == 'text/html':
                        data = self.base64_url_decode(
                            part['body']['data']
                        )
                        messages_html.append(
                            {'uid': msg['id'], 'content': data}
                        )
            elif content['payload']['mimeType'] == 'text/html':
                data = self.base64_url_decode(
                    content['payload']['body']['data']
                )
                messages_html.append({'uid': msg['id'], 'content': data})

            time.sleep(0.02)  # limit to 50 req/s to avoid rate limit TODO: load from config

        return messages_html

    def fetch_emails(self, mail_boxes, from_date):
        """
        Fetch the emails from given mail_boxes and convert them into a list of
        Email instances. Return the list.
        """
        emails = []
        label_ids = self.get_label_ids(mail_boxes)
        messages = self.get_messages(label_ids, from_date)
        for message in messages:
            emails.append(Email.from_dict(message))

        return emails


class TransactionEmail:
    """
    A type to represent the values from a transaction's email.
    """
    CONCEPT = 'concept'
    DATE = 'date'
    AMOUNT = 'amount'
    EMAIL_ID = 'email_id'
    TAGS = 'tags'

    def __init__(self, concept, date, amount, email_id, tags=None):
        """
        Initialize instance.
        """
        self.concept = concept
        self.date = date
        self.amount = amount
        self.email_id = email_id
        self.tags = tags

    @classmethod
    def from_dict(cls, data):
        """
        Create a TransactionEmail instance from a dictionary.
        """
        try:
            transaction_email = TransactionEmail(
                data[cls.CONCEPT],
                data[cls.DATE],
                data[cls.AMOUNT],
                data[cls.EMAIL_ID]
            )
            return transaction_email
        except KeyError as e:
            raise MissingFieldError(f'{e} is missing')

    def serialize(self):
        """
        "Convert the transaction email instance into a dictionary.
        """
        return {
            self.CONCEPT: self.concept,
            self.DATE: self.date,
            self.AMOUNT: self.amount,
            self.EMAIL_ID: self.email_id,
            self.TAGS: self.tags
        }


class BaseHtmlEmailParser(html.parser.HTMLParser):
    """
    A class to define the behavior of objects that know how to parse emails in
    html format.
    """
    def __init__(self):
        """
        Just call super's init method.
        """
        super().__init__()

    def get_data(self):
        """
        Return a dictionary with the values that are required to build a
        transaction object. Must be implemented by concrete classes
        """

    def parse_email(self, html_email):
        """
        Convert an email into a transaction object.
        """
        self.feed(html_email.content)
        parsed_data = self.get_data()
        parsed_data[TransactionEmail.EMAIL_ID] = html_email.uid
        return TransactionEmail.from_dict(parsed_data)


class BanamexEmailParser(BaseHtmlEmailParser):
    CONCEPT_STR = 'Establecimiento'
    AMOUNT_STR = '$'
    DATE_STR = 'Fecha y hora'
    TRANSACTION_TYPE = 'Retiro/Compra'

    def __init__(self):
        self._data_strs = []
        super().__init__()

    def handle_data(self, data):
        self._data_strs.append(data)

    def get_data(self):
        i = 0
        data = {}
        expected_transaction = False
        while i < len(self._data_strs):
            if self.CONCEPT_STR in self._data_strs[i]:
                if 'concept' not in data:
                    data['concept'] = self._data_strs[i+1]
                i += 2
            elif self.AMOUNT_STR in self._data_strs[i]:
                if 'amount' not in data:
                    data['amount'] = self.parse_amount(self._data_strs[i])
                i += 1
            elif self.DATE_STR in self._data_strs[i]:
                if 'date' not in data:
                    data['date'] = self.parse_date(self._data_strs[i+1])
                i += 2
            elif self.TRANSACTION_TYPE in self._data_strs[i]:
                expected_transaction = True
                i += 1
            else:
                i += 1

        return data if expected_transaction else {}

    def parse_date(self, date_str):
        date_parts = date_str.split(' ')[0].split('/')

        if len(date_parts) < 3:
            return date_str

        # support old date format
        if len(date_parts[0]) == 2 and len(date_parts[2]) == 2:
            return '-'.join([
                '20' + date_parts[2],
                date_parts[1],
                date_parts[0]
            ])
        else:
            return '-'.join([date_parts[0], date_parts[1], date_parts[2]])

    def parse_amount(self, amount_str):
        amount_parts = amount_str.split(' ')
        # support old amount format
        if len(amount_parts) == 1:
            return amount_parts[0][1:].replace(',', '')
        else:
            return amount_parts[1].replace(',', '')


class HeyBancoEmailParser(BaseHtmlEmailParser):
    CONCEPT_STR = 'Comercio en donde se hizo la compra '
    AMOUNT_STR = 'Monto de compra '
    DATE_STR = 'Fecha y hora de la transacción'

    def __init__(self):
        self._data_strs = []
        self._start_tag = None
        super().__init__()

    def handle_starttag(self, tag, attrs):
        self._start_tag = tag

    def handle_data(self, data):
        if self._start_tag == 'h4':
            self._data_strs.append(data)

    def get_data(self):
        i = 0
        data = {}
        while i < len(self._data_strs):
            if self._data_strs[i] == self.CONCEPT_STR:
                data['concept'] = self._data_strs[i+2]
                i += 3
            elif self._data_strs[i] == self.AMOUNT_STR:
                data['amount'] = self.parse_amount(self._data_strs[i+2])
                i += 3
            elif self._data_strs[i] == self.DATE_STR:
                data['date'] = self.parse_date(self._data_strs[i+2])
                i += 3
            else:
                i += 1

        return data

    def parse_date(self, date_str):
        """
        Example input date str = 01/07/2021 - 20:29 hrs
        Example output date str = 2021-07-01
        """
        date_parts = date_str.split(' ')[0].split('/')
        return '-'.join([date_parts[2], date_parts[1], date_parts[0]])

    def parse_amount(self, amount_str):
        """
        Remove $ symbol at the begining of the string and any , symbol
        """
        return amount_str[1:].replace(',', '')


SUPPORTED_CLIENTS = {'gmail': GmailClient}
SUPPORTED_PARSERS = {
    'heybanco': HeyBancoEmailParser,
    'banamex': BanamexEmailParser
}


def build_client(email_provider):
    """
    Build the corresponding client instance based on email_provider. Raise
    UnsupportedEmailProviderError if email_provider is not supported.
    """
    try:
        client_class = SUPPORTED_CLIENTS[email_provider]
        return client_class()
    except KeyError:
        raise UnsupportedEmailProviderError(f'{email_provider} not supported')


def build_parser(email_type):
    """
    Build the corresponding parser instance based on email_type. Raise
    UnsupportedEmailType if email_type is not supported.
    """
    try:
        parser_class = SUPPORTED_PARSERS[email_type]
        return parser_class()
    except KeyError:
        raise UnsupportedEmailType(f'{email_type} not supported')
