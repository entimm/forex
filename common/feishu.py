import requests
from datetime import datetime

from common.config import config


class FeiShuRobot:
    BASE_URL = 'https://open.feishu.cn/open-apis/bot/v2/hook/'
    instances = {}

    def __init__(self, robot_id):
        self.robot_id = robot_id

    @classmethod
    def instance(cls, name):
        if name not in cls.instances:
            robot_id = config.get('feishu-webhook')[name]
            cls.instances[name] = cls(robot_id)
        return cls.instances[name]

    def send_emergency(self, title, contents):
        self.send('carmine', '【紧急】' + title, contents)

    def send_critical(self, title, contents):
        self.send('purple', '【严重】' + title, contents)

    def send_error(self, title, contents):
        self.send('red', '【错误】' + title, contents)

    def send_warning(self, title, contents):
        self.send('yellow', '【警告】' + title, contents)

    def send_notice(self, title, contents):
        self.send('blue', '【提示】' + title, contents)

    def send_info(self, title, contents):
        self.send('wathet', '【信息】' + title, contents)

    def send_ok(self, title, contents):
        self.send('green', '【成功】' + title, contents)

    def send(self, color, title, contents):
        if not isinstance(contents, list):
            contents = [contents]

        elements = [
            {
                "fields": [
                    {
                        "is_short": True,
                        "text": {
                            "content": f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                            "tag": "lark_md"
                        }
                    },
                ],
                "tag": "div"
            },
        ]
        for content in contents:
            if isinstance(content, str):
                content = PlainTextElement.make(content)
            elements.append(content.output())

        feishu_card_message = {
            "msg_type": "interactive",
            "card": {
                "config": {
                    "wide_screen_mode": True
                },
                "header": {
                    "template": color,
                    "title": {
                        "content": title,
                        "tag": "plain_text"
                    }
                },
                "elements": elements,
            }
        }

        self.base_send(feishu_card_message)

    def base_send(self, feishu_card_message):
        requests.post(self.BASE_URL + self.robot_id, json=feishu_card_message)


class PlainTextElement:
    def __init__(self, text):
        self.text = text

    @staticmethod
    def make(text):
        return PlainTextElement(text)

    def output(self):
        return {
            "tag": "div",
            "text": {
                "content": self.text,
                "tag": "plain_text"
            }
        }
class MarkdownElement:
    def __init__(self, text):
        self.text = text

    @staticmethod
    def make(text):
        return MarkdownElement(text)

    def output(self):
        return {
            "tag": "div",
            "text": {
                "content": self.text,
                "tag": "lark_md"
            }
        }
