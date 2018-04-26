import pika


def grade_quiz_submission_task(question_submission_pk):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    channel.basic_publish(exchange='', routing_key='task_queue', body=question_submission_pk, properties=pika.BasicProperties(delivery_mode=2))

    print('[x] Sent question submission with pk: ' + question_submission_pk)
    connection.close()
