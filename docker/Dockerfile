FROM python:3.11

WORKDIR /app
COPY . .

RUN cp cron /etc/cron.d/cron
RUN pip install -r requirements.txt

RUN chmod 0644 /etc/cron.d/cron

RUN touch log.log
RUN touch /var/log/cron.log

RUN apt-get update && apt-get -y install cron
RUN crontab -u root /etc/cron.d/cron

#RUN sleep 10

#RUN cp /etc/cron.d/cron /var/spool/cron/crontabs/root
CMD touch output.txt && cron && tail -f /var/log/cron.log

#CMD /bin/sh
