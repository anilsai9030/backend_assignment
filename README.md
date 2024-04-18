# Gmail API
1) To use gmail API via python , you need to a google account and create a project in google cloud console. https://developers.google.com/workspace/guides/get-started
2) Enable the Gmail API for the project and download the credentials.json file.
3) Install the required libraries for working with gmail API. Link: https://developers.google.com/gmail/api/quickstart/python
4) For the project assign the required scopes (Modify) in our app case as , we need to move messages from one folder to another.
5) you need to download the credentials created for your project and save it in the same directory as the script.
6) If you want to test the app with another email(other than account used to create the project), you need to add those emails in the project configuration on console.
7) As our requiremnt was to work on the messages and on labels , we need to use the methods mentioned in the following links
   1) Link: https://googleapis.github.io/google-api-python-client/docs/dyn/gmail_v1.users.labels.html --> Label API Methods
   2) Link: https://googleapis.github.io/google-api-python-client/docs/dyn/gmail_v1.users.messages.html --> Message API Methods


# working
1) The script will read the credentials.json file and authenticate the user.
2) The script will read the messages from the Inbox folder and laters reads the metadata of each message.
3) As our requirement or aim is to only move the messages from Inbox to another folder, we will only store the 
messages IDS , from_email, subject, dateReceived in DB.
4) Remaining all other fields we are ignoring as we are not using them.
5) Now based on the rules configured in the rules.json file, we will perform the respective actions accordingly.

# Rules.json
1) Each rule will have a logic, conditions and actions.
2) The values accepted in the logic field are as follows:
    1) All --> Means all the conditions given in the conditions should be satisfied.
    2) Any --> Means any of the conditions given in the conditions should be satisfied.
3) The conditions field will have the conditions based on which the actions will be performed.
   1) The conditions will have the following fields:
        1) field --> The field on which the condition is to be applied (from_email, subject, date_received).
        2) predicate --> The operator to be used for the condition
           1) for from_email and subject fields, the accepted values are as follows:
                1) contains --> The field should contain the value.
                2) equals --> The field should be equal to the value.
                3) does not contain --> The field should not contain the value.
                4) does not equal --> The field should not be equal to the value.
           2) for date_received field, the accepted values are as follows:
              1) less than days --> The date should be less than the value in days.
              2) greater than days --> The date should be greater than the value in days.
              3) less than months --> The date should be less than the value in months.
              4) greater than months --> The date should be greater than the value in months.
        3) value --> The value to be compared with the field.
4) The actions field will have the actions to be performed based on the conditions.
   1) The actions will have the following fields:
        1) action --> The action to be performed.
           1) mark_as_read --> The message will be marked as read.
           2) mark_as_unread --> The message will be marked as unread.
           3) move_message --> The message will be moved to the folder mentioned in the following value.
              1) folder_name --> The folder name to which the message is to be moved.