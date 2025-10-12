FROM python

RUN pip install python-telegram-bot python-telegram-bot[job-queue] gitpython

# Set the timezone environment variable
ENV TZ=Europe/Madrid

# Install tzdata to apply timezone properly
RUN apt-get update && apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /tst

CMD [ "python", "src/main.py" ]

ENTRYPOINT [ "python", "src/main.py" ]