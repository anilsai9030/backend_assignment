from scripts.email_fetcher import fetch_emails, batch_request
from scripts.gmail_service import GmailService
from scripts.modify_emails import fetch_data_from_db, load_rules
from utils.logging_config import logger

if __name__ == "__main__":
    """
    Main function to handle the workflow of authenticating to the Gmail API,
    fetching emails, processing them in batches, applying rules, and handling exceptions.
    """
    try:
        service = GmailService.authenticate_email()
        messages = fetch_emails(service)
        batch_request(messages, service)
        rules = load_rules()
        fetch_data_from_db(rules, service)
    except Exception as error:
        logger.error(f"Error occurred: {error}", exc_info=True)

