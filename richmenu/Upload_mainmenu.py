import requests
import json
from linebot import (
    LineBotApi, WebhookHandler
)

headers = {"Authorization":"Bearer channel_access_token","Content-Type":"application/json"}

body = {
    "size": {"width": 1200, "height": 810},
    "selected": "true",
    "name": "menu",
    "chatBarText": "選單",
    "areas":[
        {
          "bounds": {"x": 0, "y": 0, "width": 400, "height": 405},
          "action": {"type": "message", "text": "開門"}
        },
        {
          "bounds": {"x": 401, "y": 0, "width": 400, "height": 405},
          "action": {"type": "message", "text": "房間資訊"}
        },
        {
          "bounds": {"x": 801, "y": 0, "width": 400, "height": 405},
          "action": {"type": "message", "text": "故障回報"}
        },
        {
          "bounds": {"x": 0, "y": 401, "width": 400, "height": 405},
          "action": {"type": "message", "text": "電燈"}
        },
        {
          "bounds": {"x": 402, "y": 402, "width": 400, "height": 405},
          "action": {"type": "message", "text": "插座"}
        },
        {
          "bounds": {"x": 800, "y": 408, "width": 400, "height": 405},
          "action": {"type": "message", "text": "個人資訊"}
        },
    ]
  }

req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu', 
                       headers=headers,data=json.dumps(body).encode('utf-8'))

menuid = {}
menuid = json.loads(req.text)
richmenuid = menuid['richMenuId']
print(richmenuid)
line_bot_api = LineBotApi('channel_access_token')

with open("menu.png", 'rb') as f:
    line_bot_api.set_rich_menu_image(richmenuid, "image/jpeg", f)
    
headers = {"Authorization":"Bearer channel_access_token","Content-Type":"application/json"}

uploadmenu = "https://api.line.me/v2/bot/user/all/richmenu/" + richmenuid

req = requests.request('POST', uploadmenu, 
                       headers=headers)

print(req.text)