# Twitter video downloader
Script to download videos from twitter integrated with telegram to used as a bot.
## Setup
1) Clone the repository

```
$ git clone https://github.com/Almadih/twitter-videos-downloader-bot.git
```

2) Create telegram bot
  create telegram bot with botFather and get the http token


3) Deploy to cloud function

```
gcloud functions deploy download_twitter_video --runtime python37 --trigger-http --memory=1024MB --timeout=200 --set-env-vars TELEGRAM_BOT_TOKEN=<token>
```   
make sure billing is enabled in your google cloud project.

4) update bot webhook url

```
https://api.telegram.org/bot<token>/setWebhook?url=<cloud function url>
```

#credit 
most of the code from this [repo](https://github.com/hohohoesmad/twitter2mp4.git) all credit goes to the author.