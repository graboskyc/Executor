FROM python:3.13-bookworm

WORKDIR /usr/src/app

COPY backend/requirements.txt ./
RUN rm -rf ./venv activate.sh sample.env
RUN pip install --no-cache-dir -r requirements.txt

COPY ./backend .
# Copy entrypoint script
COPY backend/app/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
RUN touch /var/log/cron.log
EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]