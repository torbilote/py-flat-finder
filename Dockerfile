FROM python:3.11.6-slim-bullseye

RUN apt-get update

COPY . ./py-flat-finder

WORKDIR /py-flat-finder

ARG sender_email
ENV sender_email=${sender_email}

ARG sender_pwd
ENV sender_pwd=${sender_pwd}

RUN pip install pip --upgrade
RUN pip install -r ./requirements.txt

CMD ["python3", "-m", "app.main"]