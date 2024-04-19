import time

from database.db_utils import *
from utils.utils import chunker, extract_email
from utils.logging_config import logger


Session = sessionmaker(bind=engine)


def fetch_emails(service):
    """
    Fetches all emails from the user's Gmail inbox using the Gmail API service.
    :param service: Authorized Gmail API service instance.
    :return: A list of message dictionaries containing message details.
    """
    messages = []
    count = 0
    results = service.users().messages().list(userId="me", labelIds=["INBOX"]).execute()
    messages.extend(results.get("messages", []))

    while "nextPageToken" in results:
        page_token = results["nextPageToken"]
        results = service.users().messages().list(userId="me", labelIds=["INBOX"], pageToken=page_token).execute()
        messages.extend(results.get("messages", []))
        count += len(results.get("messages", []))
        logger.info(f"count of messages fetched {count}")
    return messages


def batch_request(data, service):
    """
    Processes emails in batches, fetching metadata for each email, and then storing the processed emails into a database.

    :param data: List of message IDs to process.
    :param service: Authorized Gmail API service instance.
    :return: None
    """

    emails_to_be_processed = []

    def process_email_metadata(request_id, response, exception):
        if exception:
            logger.error(f"An error occurred while processing the batch request {exception}", exc_info=True)
        else:
            try:
                headers = {header['name'].lower(): header['value'] for header in
                           response.get('payload', {}).get('headers', [])}
                email = Email(
                    message_id=response.get("id"),
                    from_email=extract_email(headers.get("from")),
                    subject=headers.get("subject"),
                    date_received=response.get("internalDate")
                )
                emails_to_be_processed.append(email)
            except Exception as e:
                logger.error(f"Error processing email data: {e}", exc_info=True)
    ids = [message["id"] for message in data]
    for chunk in chunker(ids, 50):
        batch = service.new_batch_http_request(callback=process_email_metadata)
        for message_id in chunk:
            batch.add(service.users().messages().get(userId="me", id=message_id, format="metadata"))
        time.sleep(5)
        batch.execute()

    # After all batches are processed, save the emails
    save_emails_to_database(emails_to_be_processed)


def save_emails_to_database(emails):
    """
    Saves a list of processed emails into the database in bulk.

    :param emails: List of Email objects to be saved.
    """
    session = Session()
    for chunk in chunker(emails, 100):
        try:
            session.bulk_save_objects(chunk)
            session.commit()
            logger.info(f"Successfully saved {len(chunk)} emails to the database.")
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save emails to the database: {e}")
        finally:
            session.close()


