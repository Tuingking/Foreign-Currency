FROM python:3.6

ENV FLASK_APP wsgi.py
ENV FLASK_CONFIG docker

RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/

RUN chmod +x postactivate-docker.sh
ENTRYPOINT ["./postactivate-docker.sh"]