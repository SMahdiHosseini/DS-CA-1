FROM professormahi/shadow:master

COPY . /workspace
WORKDIR /workspace

RUN pip install -r requirements.txt

RUN apt-get update && apt-get upgrade -y
RUN apt-get install rabbitmq-server -y