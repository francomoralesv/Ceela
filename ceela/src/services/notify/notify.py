import json
from typing import Dict, Optional
from pydantic import BaseModel
from redis import Redis


class NotificationRequest(BaseModel):
    message: str
    notification_type: str = "info"
    payload: Optional[Dict] = None

class Notify:
    """
    Notify service for sending notifications.
    """

    def __init__(self, redis_client:Redis,user_id: str):
        self.redis_client = redis_client
        self.user_id = user_id
    
    async def send_notification(self, message):
        """
        Send a notification with the given message.
        """
        # Implementation for sending notification
        notification = {
            "type": "notification",
            "message": message,
            "notificationType": "info",
            "payload": None
        }
        
        notification_json = json.dumps(notification)
        print(f"Sending notification to user:{self.user_id}: {notification_json}")
        self.redis_client.publish(f"user:{self.user_id}", notification_json)
        print(f"Notification sent: {message}")
    async def send_result(self, message,payload: Optional[Dict] = None):
        """
        Send a result notification.
        """

        notification = {
            "type": "notification",
            "message": message,
            "notificationType": 'result',
            "payload": payload
        }
        notification_json = json.dumps(notification)
        self.redis_client.publish(f"user:{self.user_id}", notification_json)