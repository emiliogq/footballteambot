FROM python

RUN pip install python-telegram-bot python-telegram-bot[job-queue]

WORKDIR /tst

CMD [ "python", "src/main.py" ]

ENTRYPOINT [ "python", "src/main.py" ]