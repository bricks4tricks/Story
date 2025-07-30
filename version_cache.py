import datetime

# Timestamp to track last modification time for certain datasets
users_version = datetime.datetime.utcnow()


def update_users_version():
    global users_version
    users_version = datetime.datetime.utcnow()
