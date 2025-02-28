import smtplib
from datetime import datetime
from email.mime.text import MIMEText

import requests


class NotificationSystem:
    def __init__(self, config):
        self.config = config
        self.slack_webhook = config.get('slack_webhook')
        self.email_settings = config.get('email_settings')
        
    def check_thresholds(self, metrics):
        alerts = []
        if metrics['cpu'] > self.config['thresholds']['cpu']:
            alerts.append({
                'type': 'cpu',
                'level': 'warning',
                'message': f"CPU usage is high: {metrics['cpu']}%"
            })
        # ... memory, disk checks ...
        return alerts

    def send_slack_alert(self, alert):
        if self.slack_webhook:
            requests.post(self.slack_webhook, json={
                'text': f"🚨 Alert: {alert['message']}"
            })

    def send_email_alert(self, alert):
        if self.email_settings:
            msg = MIMEText(alert['message'])
            msg['Subject'] = f"System Alert: {alert['type']}"
            # ... email sending logic ... 