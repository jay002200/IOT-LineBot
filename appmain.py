from flask import Flask, request, abort
from linebot import exceptions
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from imgurpython import ImgurClient

from urllib.request import urlretrieve

import configparser
import requests
import os
import random
import tempfile
import MySQLdb
import re
import time

app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

# The line bot access token and webhook id

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))

# The imgur client id, client secret, access token and refresh token
client_id = config.get('imgur', 'imgur_client_id')
client_secret = config.get('imgur', 'imgur_client_secret')
access_token = config.get('imgur', 'imgur_access_token')
refresh_token = config.get('imgur', 'imgur_refresh_token')


static_tmp_path = os.path.join(os.path.dirname(
    __file__), 'static', 'C:/Users/goldcity5/Desktop/pylinebot/pic')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=(TextMessage, ImageMessage))
def handle_message(event):
    # receive key word -> send message or do something
    if isinstance(event.message, TextMessage):
        user_id = event.source.user_id
# --------------Administrator--------------------------------
        if event.message.text == "help":
            if user_id == "U892b576cb7c0398b94208100d51c5c08":
                print(search_user(user_id))
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="房客資料登入 : 輸入新房客資料。\n查詢房客資訊 : 調出房客資訊\n")
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="房客註冊 : 新加入的房客輸入自己的資料，驗證過後即可使用功能。\n問題回報 : 宿舍各項問題及故障回報。\n開門 ： 打開宿舍大門\nXX關閉/開啟 : 控制自行設定的電器。")
                )

        if event.message.text == "用戶註冊列表":
            if user_id == "U892b576cb7c0398b94208100d51c5c08":
                try:
                    db = MySQLdb.connect(host='localhost', port=3306, user='root',
                                         passwd='123qwe', db='room_data', charset='utf8mb4')
                    cursor = db.cursor()
                    cursor.execute(
                        "SELECT id,name,phone,check_status FROM tenant_info WHERE check_status = 'n'")
                    tup = cursor.fetchall()
                    notice = "用戶註冊列表"
                    for i in range(len(tup)):
                        notice += '\n'
                        notice += str(tup[i])
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=notice)
                    )
                except Exception as e:
                    print(e)
                    db.rollback()
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你沒有權限")
                )

        if event.message.text == "用戶確認註冊":
            if user_id == "U892b576cb7c0398b94208100d51c5c08":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="先輸入關鍵字'OK'後接著輸入要確認的ID\n例:OK 1 2 3")
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="你沒有權限")
                )

        elif str(event.message.text).find("OK") != -1 or str(event.message.text).find("ok") != -1:
            if user_id == "U892b576cb7c0398b94208100d51c5c08":
                try:
                    data_1, data_2 = str(event.message.text).split('OK', 1)
                    check = str(data_2)
                except Exception as e:
                    pass

                try:
                    data_1, data_2 = str(event.message.text).split('ok', 1)
                    check = str(data_2)
                except Exception as e:
                    pass

                try:
                    db = MySQLdb.connect(host='localhost', port=3306, user='root',
                                         passwd='123qwe', db='room_data', charset='utf8mb4')
                    cursor = db.cursor()
                    sql = """UPDATE tenant_info SET check_status='Y' WHERE id='""" + \
                        str(check) + """'"""
                    print(sql)
                    cursor.execute(sql)
                    db.commit()
                    print("修改成功")
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="認證成功")
                    )
                except Exception as e:
                    db.rollback()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="認證失敗")
                    )
                    print(e)
                db.close()
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你沒有權限")
                )
# -----------------------------------------------
        if event.message.text == "開門":
            if search_user(user_id) == 'Y':
                client = mqtt.Client()
                client.username_pw_set("yujie", "12345")
                client.connect("192.168.1.112", 1883, 60)
                client.publish("esp8266/opendoorsub", "o")
                client.subscribe("esp8266/opendoorpub")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="門已開啟")
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你沒有權限")
                )

        elif event.message.text == "房客註冊":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="請先輸入關鍵字A，輸入姓名、房號和電話\n範例:A田聖潔 A1 0912345678")
            )

        elif str(event.message.text).find("A") != -1 or str(event.message.text).find("a") != -1:
            try:
                data_1, data_2 = str(event.message.text).split('A', 1)
                name, room_no, phone = str(data_2).split(' ', 2)
            except Exception as e:
                pass

            try:
                data_1, data_2 = str(event.message.text).split('a', 1)
                name, room_no, phone = str(data_2).split(' ', 2)
            except Exception as e:
                pass

            try:
                db = MySQLdb.connect(host='localhost', port=3306, user='root',
                                     passwd='123qwe', db='room_data', charset='utf8mb4')
                cursor = db.cursor()
                try:
                    sql = """INSERT INTO tenant_info(name, room_no, phone, lineid, check_status) VALUES('""" + name + \
                        """', '""" + room_no + """', '""" + phone + \
                        """', '""" + user_id + """', '""" + 'n' + """')"""
                    cursor.execute(sql)
                    db.commit()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="輸入成功，等待管理員驗證。")
                    )
                except Exception as e:
                    print(e)

                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="輸入失敗，請詢問管理員。")
                    )
            except:
                db.rollback()

            db.close()

        elif event.message.text == "故障回報":
            if search_user(user_id) == 'Y':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="上傳圖片並描述問題。")
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="非本棟用戶，拒絕使用。")
                )

    reply_arr = []
    reply_arr.append(TextSendMessage('上傳成功'))
    reply_arr.append(TextSendMessage('相簿網址:https://imgur.com/a/cvFJ6ib'))

    if isinstance(event.message, ImageMessage):
        ext = 'jpg'
        message_content = line_bot_api.get_message_content(event.message.id)
        with tempfile.NamedTemporaryFile(dir=static_tmp_path, prefix=ext + '-', delete=False) as tf:
            for chunk in message_content.iter_content():
                tf.write(chunk)
            tempfile_path = tf.name

        dist_path = tempfile_path + '.' + ext
        dist_name = os.path.basename(dist_path)
        os.rename(tempfile_path, dist_path)
        try:
            client = ImgurClient(client_id, client_secret,
                                 access_token, refresh_token)
            config = {
                'album': 'cvFJ6ib',
                'name': dist_name,
                'title': '',
                'description': ''
            }
            path = os.path.join(
                'static', 'C:/Users/goldcity5/Desktop/pylinebot/pic', dist_name)
            client.upload_from_path(path, config=config, anon=False)
            os.remove(path)
            print(path)
            line_bot_api.reply_message(
                event.reply_token,
                reply_arr)
        except:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage('上傳失敗'))
        return 0


def search_user(user_id):
    try:
        db = MySQLdb.connect(host='localhost', port=3306, user='root',
                             passwd='123qwe', db='room_data', charset='utf8mb4')
        cursor = db.cursor()
        cursor.execute(
            "SELECT check_status FROM tenant_info WHERE lineid = '%s'" % (user_id))
        checkcorrect = cursor.fetchone()
        return checkcorrect[0]
    except Exception as e:
        print(e)
    finally:
        db.close()


if __name__ == "__main__":
    app.run()
