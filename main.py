import logging

from scripts.email_fetcher import fetch_emails, batch_request
from scripts.gmail_service import GmailService
from scripts.modify_emails import fetch_data_from_db, load_rules
from utils import logging_config

if __name__ == "__main__":
    try:
        service = GmailService.authenticate_email()
        messages = fetch_emails(service)
        batch_request(messages, service)
        rules = load_rules()
        fetch_data_from_db(rules, service)
    except Exception as error:
        logging.error(f"Error occurred: {error}", exc_info=True)

