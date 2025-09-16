import boto3

ses_client = boto3.client('ses') #, region_name='us-east-1')

def send_email(from_email: str, to_email: str, subject: str, body_text: str, body_html: str = None):
    destination = {
        "ToAddresses": [to_email]
    }

    body = {
        "Text": {"Data": body_text}
    }

    if body_html:
        body["Html"] = {"Data": body_html}

    response = ses_client.send_email(
        Source=from_email,
        Destination=destination,
        Message={
            "Subject": {"Data": subject},
            "Body": body
        }
    )

    return response
