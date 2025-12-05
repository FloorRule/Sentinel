FROM python:3.10

WORKDIR /app
COPY traffic_generator.py /app

RUN pip install requests

CMD ["python", "-u","traffic_generator.py", "Attack"]