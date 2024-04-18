import time

from database.db_utils import *
from utils.utils import chunker, extract_email
from utils import logging_config
import logging


Session = sessionmaker(bind=engine)


def fetch_emails(service):
    """
    Fetches all the emails from the user's inbox.
    :param service:
    :return: messages
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
        print(count)
    return messages


def batch_request(data, service):
    """
    Process the emails in batch requests.
    :param data:
    :param service:
    :return: None
    """
    emails_to_be_processed = []

    def process_email_metadata(request_id, response, exception):
        if exception:
            logging.error(f"An error occurred while processing the batch request {exception}", exc_info=True)
        else:
            try:
                headers = {header['name'].lower(): header['value'] for header in
                           response.get('payload', {}).get('headers', [])}
                email = Email(
                    id=response.get("id"),
                    from_email=extract_email(headers.get("from")),
                    subject=headers.get("subject"),
                    date_received=response.get("internalDate")
                )
                emails_to_be_processed.append(email)
            except Exception as e:
                logging.error(f"Error processing email data: {e}", exc_info=True)
    ids = [message["id"] for message in data]
    for chunk in chunker(ids, 100):
        batch = service.new_batch_http_request(callback=process_email_metadata)
        for message_id in chunk:
            batch.add(service.users().messages().get(userId="me", id=message_id, format="metadata"))
        time.sleep(5)
        batch.execute()

    # After all batches are processed, save the emails
    save_emails_to_database(emails_to_be_processed)


def save_emails_to_database(emails):
    """Save processed emails to the database in bulk."""
    session = Session()
    for chunk in chunker(emails, 100):
        try:
            session.bulk_save_objects(chunk)
            session.commit()
            logging.info(f"Successfully saved {len(chunk)} emails to the database.")
        except Exception as e:
            session.rollback()
            logging.error(f"Failed to save emails to the database: {e}")
        finally:
            session.close()


