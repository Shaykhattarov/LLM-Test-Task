from worker.celery import celery
from api.dependencies import get_sync_session

from sqlalchemy.orm import Session

@celery.task(name="process_message_task")
def process_new_message_task(message_id: int):
    session: Session = get_sync_session()

    