# Football Team Telegram Bot

This bot is created mainly to help football team administrators to keep track of polls and notify team members to vote polls if they haven't yet

## Getting started

A Docker image is provided to run the Telegram bot:

```sh
docker build -t footballteambot .
```

Once it is build, the telegram bot can be started like this:

```sh
docker run -d --name footballteambot --restart always -v ${PWD}:/footballteambot -w /footballteam footballteambot <telegram-bot-token>
```