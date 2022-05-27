import requests
import re,json,os
import telebot

tb = telebot.TeleBot(os.environ['TELEGRAM_BOT_TOKEN'])

class Downloader:
    def __init__(self, url,chat_id):
        self.headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0','accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'accept-language': 'es-419,es;q=0.9,es-ES;q=0.8,en;q=0.7,en-GB;q=0.6,en-US;q=0.5'}
        self.url = url
        self.session = requests.Session()
        self.download_url = None
        self.downloaded_file_name = None
        self.chat_id = chat_id

    def get_video_url(self):
        if not self.is_valid_url():
            self.notify_user("Invalid URL")
            return
        video_id = self.url.split(
            '/')[5].split('?')[0] if 's?=' in self.url else self.url.split('/')[5]
        sources = {
            "video_url": "https://twitter.com/i/videos/tweet/"+video_id,
            "activation_ep": 'https://api.twitter.com/1.1/guest/activate.json',
            "api_ep": "https://api.twitter.com/1.1/statuses/show.json?id="+video_id
        }

        self.notify_user("Downloading video...")


        token_request = self.send_request(sources["video_url"],"GET")
        bearer_file = re.findall('src="(.*js)',token_request)
        file_content = self.send_request(str(bearer_file[0]),'GET')
        bearer_token_pattern = re.compile('Bearer ([a-zA-Z0-9%-])+')
        bearer_token = bearer_token_pattern.search(file_content)
        self.headers['authorization'] = bearer_token.group(0)
        req2 = self.send_request(sources['activation_ep'],'post')
        self.headers['x-guest-token'] = json.loads(req2)['guest_token']
        api_request = self.send_request(sources["api_ep"],"GET")
        try:
            videos = json.loads(api_request)['extended_entities']['media'][0]['video_info']['variants']
            bitrate = 0
            for vid in videos:
                if vid['content_type'] == 'video/mp4':
                    if vid['bitrate'] > bitrate:
                        bitrate = vid['bitrate']
                        hq_video_url = vid['url'] 
            self.download_url = hq_video_url
        except:
            self.notify_user("An error occurred, please try again")


    def send_request(self, url, method):
        request = self.session.get(url, headers=self.headers) if method == "GET" else self.session.post(url, headers=self.headers)
        if request.status_code == 200:
            return request.text
        else:
            self.notify_user("An error occurred, please try again")

    def save_video_file(self):
        self.get_video_url()
        if not self.download_url:
            return
        file_name = self.download_url.split('/')[8].split('?')[0]
        path = os.path.join('/tmp',file_name)
        with open(path,'wb') as f:
            f.write(self.session.get(self.download_url,headers=self.headers).content)
        self.downloaded_file_name = file_name
    def send_video_via_telegram(self):
        if not self.downloaded_file_name:
            return
        tb.send_video(self.chat_id,open(os.path.join('/tmp',self.downloaded_file_name),'rb'))
    def notify_user(self,message):
        tb.send_message(self.chat_id,message)
    def is_valid_url(self):
        if not re.match(r'https:\/\/twitter.com\/\w{1,15}\/status\/(\d{15,25})',self.url):
            return False
        return True


def send_welcome_message(chat_id):
    tb.send_message(chat_id, "Welcome to Twitter Video Downloader Bot")


def download_twitter_video(request):
    request_json = request.get_json()
    if not request_json:
        return {'error': 'Invalid request'}
    
    chat_id = request_json['message']['chat']['id']
    if request_json['message']['text'] == '/start':
        send_welcome_message(chat_id)
        return {'success': True}
    url = request_json['message']['text']
    d = Downloader(url,chat_id)
    d.save_video_file()
    d.send_video_via_telegram()
    return {'success': 'Video sent'}
