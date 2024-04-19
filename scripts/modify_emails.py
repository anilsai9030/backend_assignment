import json
import logging
import time
from sqlalchemy.orm import sessionmaker
from database.db_utils import engine, Email
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy import and_, or_
from utils.logging_config import logger

Session = sessionmaker(bind=engine)
session = Session()


def create_folder(service, folder_name):
    """
    Creates a new folder in the user's Gmail account.
    :param service: Authorized Gmail API service instance
    :param folder_name: Name of the folder to be created
    :return: id/lablel of the created folder
    """
    body = {
        "name": folder_name,
        "messageListVisibility": "show",
        "labelListVisibility": "labelShow"
    }
    folder_creation_response = service.users().labels().create(userId="me", body=body).execute()
    return folder_creation_response["id"]


def check_folder_exists(service, folder_name):
    """
    Checks if the folder exists in the user's Gmail account.
    :param service: Authorized Gmail API service instance
    :param folder_name: Name of the folder to be checked
    :return: id if present else None
    """
    folders = service.users().labels().list(userId="me").execute()
    print(folders)
    for folder in folders["labels"]:
        if folder["name"] == folder_name:
            return folder["id"]
    return None


def execute_actions(message_ids, actions, service):
    """
    Executes the actions on the emails.
    :param message_ids: List of message ids
    :param actions: List of actions to be performed
    :param service: Authorized Gmail API service instance
    :return: None
    """
    body = {
        "addLabelIds": [],
        "ids": [],
        "removeLabelIds": []
    }
    for action in actions:
        if action["action"] == "mark_as_read":
            body["removeLabelIds"] = ["UNREAD"]
        elif action["action"] == "mark_as_unread":
            body["addLabelIds"] = ["UNREAD"]
        elif action["action"] == "move_message":
            folder = action["folder_name"]
            if folder_id := check_folder_exists(service, folder):
                body["addLabelIds"].append(folder_id)
            else:
                new_folder_id = create_folder(service, folder)
                body["addLabelIds"].append(new_folder_id)
    batch_size = 999
    for start in range(0, len(message_ids), batch_size):
        batch_body = {**body, "ids": message_ids[start:start + batch_size]}
        service.users().messages().batchModify(userId="me", body=batch_body).execute()


def load_rules():
    with open('./config/rules.json', 'r') as file:
        return json.load(file)


def datetime_to_milliseconds(dt):
    """Converts a datetime object to Unix timestamp in milliseconds."""
    return int(time.mktime(dt.timetuple()) * 1000)


def fetch_data_from_db(rules, service):
    """
    Fetches the data from the database based on the rules and executes the actions further
    :param rules: List of rules to be applied
    :param service: Authorized Gmail API service instance
    :return: None
    """
    try:
        for rule in rules.get("rules"):
            query = session.query(Email.message_id)
            condition_list = []
            for condition in rule.get("conditions"):
                field = condition.get("field")
                predicate = condition.get("predicate")
                value = condition.get("value")
                column = getattr(Email, field)

                if predicate == "contains":
                    query = query.filter(column.like(f"%{value}%"))
                elif predicate == "does not contain":
                    query = query.filter(column.notlike(f"%{value}%"))
                elif predicate == "equals":
                    query = query.filter(column == value)
                elif predicate == "does not equal":
                    query = query.filter(column != value)
                elif "days" in predicate:
                    days = int(value)
                    date_threshold = datetime.now() - timedelta(days=days)
                    millis = datetime_to_milliseconds(date_threshold)
                    if "less than" in predicate:
                        query = query.filter(column < millis)
                    elif "greater than" in predicate:
                        query = query.filter(column > millis)
                elif "months" in predicate:
                    months = int(value)
                    date_threshold = datetime.now() - relativedelta(months=months)
                    millis = datetime_to_milliseconds(date_threshold)
                    if "less than" in predicate:
                        query = query.filter(column < millis)
                    elif "greater than" in predicate:
                        query = query.filter(column > millis)

            if rule['logic'] == "All":
                query = query.filter(and_(*condition_list))
            elif rule['logic'] == "Any":
                query = query.filter(or_(*condition_list))
            logger.info(f"Final Query: {str(query)}")
            message_ids = [email.message_id for email in query.all()]
            if message_ids:
                logger.info("Email IDs to modify: ", message_ids)
                execute_actions(message_ids, rule["actions"], service)
            else:
                logger.error("No emails found for the given conditions")
    except Exception as error:
        logger.error(f"Error occurred while fetching data from the database: {error}", exc_info=True)
