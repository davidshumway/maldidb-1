FROM python:3

RUN apt-get update && apt-get install -y \
        netcat graphviz

ENV PYTHONBUFFERED 1
ENV PYTHONWRITEBYTECODE 1

RUN useradd --user-group --create-home --no-log-init --shell /bin/bash app

ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME/static
WORKDIR $APP_HOME

COPY ./mdb/requirements.txt $APP_HOME
RUN chown -R app:app $APP_HOME
USER app:app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# "WARNING: The scripts ... are installed in '/home/app/.local/bin'
#   which is not on PATH."
ENV PATH /home/app/.local/bin:$PATH 

ENTRYPOINT ["/home/app/web/entrypoint.sh"]
