from worker.celery import celery



@celery.task(name="process_message_task")
def process_new_message_task(user_id: int, message: str):
    ...