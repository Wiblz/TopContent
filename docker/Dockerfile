FROM python:3.11

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
COPY cron /etc/cron.d/cron

RUN chmod 0644 /etc/cron.d/cron
RUN touch log.log

CMD cron && tail -f /var/log/cron.log
