import os
import boto3
import json
import mysql.connector
import amqp_setup
from os import environ
from urllib.parse import urlparse


db_url = urlparse(environ.get('db_conn'))


def send_email(email, body):
    # time.sleep(10)  # simulate long-running process
    ses = boto3.client(
        'ses',
        region_name=os.getenv('SES_REGION'),
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID_SES'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY_SES')
    )
    ses.send_email(
        Source=os.getenv('SES_EMAIL_SOURCE'),
        Destination={'ToAddresses': [email]},
        Message={
            'Subject': {'Data': 'Order Status Updated'},
            'Body': {
                'Text': {'Data': body}
            }
        }
    )
    return True


def callback(channel, method, properties, body):
    message_body = json.loads(body)
    email = message_body['email']
    data = json.dumps(message_body['data'])
    log_data = data.replace("\n", "")

    try:
        send_email(email, data)
        cnx = mysql.connector.connect(
            user=db_url.username,
            password=db_url.password,
            host=db_url.hostname,
            port=db_url.port,
            database='notification'
            )

        cursor = cnx.cursor()

        cursor.execute('''
            INSERT INTO `notification` (`email`, `data`)
            VALUES (%s, %s);
            ''', (email, data))

        cnx.commit()
        cnx.close()

        print(f"SUCCESS,{email},{log_data}\n")

    except mysql.connector.Error as err:
        print(f"FAIL,{email},{log_data},{err}\n")

    except Exception:
        print("Error sending email!")


amqp_setup.channel.basic_consume(
    queue=amqp_setup.queue_name, on_message_callback=callback, auto_ack=True)
amqp_setup.channel.start_consuming()
