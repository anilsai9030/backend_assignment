import sys
from scripts.email_fetcher import fetch_emails, batch_request
from scripts.gmail_service import GmailService
from scripts.modify_emails import fetch_data_from_db, load_rules
from utils.logging_config import logger


def fetch_and_store():
    """ Fetch emails from Gmail and store them in the database. """
    try:
        service = GmailService.authenticate_email()
        messages = fetch_emails(service)
        batch_request(messages, service)
        logger.info("Emails fetched and stored successfully.")
    except Exception as error:
        logger.error(f"Error fetching and storing emails: {error}", exc_info=True)


def apply_rules():
    """ Load rules and apply them to the emails stored in the database. """
    try:
        rules = load_rules()
        service = GmailService.authenticate_email()  # Assuming service needed for some actions
        fetch_data_from_db(rules, service)
        logger.info("Rules applied successfully.")
    except Exception as error:
        logger.error(f"Error applying rules: {error}", exc_info=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--apply-rules':
        apply_rules()
    else:
        fetch_and_store()