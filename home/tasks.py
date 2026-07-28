from bucket import bucket
from celery import shared_task

def get_all_bucket_objects():
    results = bucket.get_objects()
    return results

@shared_task
def delete_object_task(key):
    bucket.delete_object(key)