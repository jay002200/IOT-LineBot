from email.mime import text
from typing_extensions import final
from flask import Flask, request, abort
from linebot import exceptions
import paho.mqtt.client as mqtt
import paho.mqtt.subscribe as subscribe
from linebot import (
    LineBotApi, WebhookHandler
)
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from imgurpython import ImgurClient

from urllib.request import urlretrieve
import re
import random
import time
import configparser
import requests
import os
import tempfile
import MySQLdb
import serial
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import string
import pyimgur
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

mqtt_address = config.get('mqtt','mqtt_ip')

static_tmp_path = os.path.join(os.path.dirname(
    __file__), 'static', 'C:/Users/goldcity5/Desktop/project/pylinebot/pic')


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
    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    # receive key word -> send message or do something
    if isinstance(event.message, TextMessage):
        user_id = event.source.user_id
        replymessage = event.message.text
        echeckcode = re.split(r'[\s]\s*', replymessage)
        
        light_poweronoffmenu = ImagemapSendMessage(
        base_url='https://imgur.com/PwD2PiS.jpg',
        alt_text='??????',
        base_size=BaseSize(height=720, width=1280),     
        actions=[
            MessageImagemapAction(
                text='????????????',
                area=ImagemapArea(
                    x=224, y=13, width=400, height=380
                )
            ),
            MessageImagemapAction(
                text='????????????',
                area=ImagemapArea(
                    x=699, y=16, width=400, height=380
                )
            )
        ]
        )
        
        home_poweronoffmenu = ImagemapSendMessage(
        base_url='https://imgur.com/PwD2PiS.jpg',
        alt_text='??????',
        base_size=BaseSize(height=720, width=1280),     
        actions=[
            MessageImagemapAction(
                text='??????????????????',
                area=ImagemapArea(
                    x=224, y=13, width=400, height=380
                )
            ),
            MessageImagemapAction(
                text='??????????????????',
                area=ImagemapArea(
                    x=699, y=16, width=400, height=380
                )
            )
        ]
        )

# --------------Administrator--------------------------------
        
        if event.message.text == "help" or event.message.text == "Help":
            if search_user(user_id) == "Administrator":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="?????????????????? : ?????????????????????????????????\n???????????? : ??????????????????\n???????????????????????????????????????????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="??????????????????", text="??????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????????????????", text="????????????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help")),
                                            QuickReplyButton(action=MessageAction(
                                                label="???????????????", text="???????????????"))
                                        ])))
            else:
                if(search_user(user_id) == 'Y'):
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text="???????????? : ????????????????????????????????????\n?????? ??? ??????????????????\n????????????/?????? : ?????????????????????????????????",
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(action=MessageAction(
                                        label="??????", text="help")),
                                    QuickReplyButton(action=MessageAction(
                                        label="????????????", text="????????????")),
                                    QuickReplyButton(action=MessageAction(
                                        label="??????", text="??????")),
                                    QuickReplyButton(action=MessageAction(
                                        label="??????????????????", text="??????????????????")),
                                    QuickReplyButton(action=MessageAction(
                                        label="??????????????????", text="??????????????????")),
                                    QuickReplyButton(action=MessageAction(
                                        label="????????????", text="????????????")),
                                    QuickReplyButton(action=MessageAction(
                                        label="????????????", text="????????????"))                                    
                                ])))
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text="???????????? : ???????????????????????????????????????????????????????????????????????????\n(???????????????)",
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(action=MessageAction(
                                        label="????????????", text="????????????")),
                                    QuickReplyButton(action=MessageAction(
                                        label="??????", text="help"))
                                ])))

        elif event.message.text == "??????????????????":
            if search_user(user_id) == "Administrator":
                notice = search_user_register_list()
                array = []
                array.append(TextSendMessage(notice))
                array.append(TextSendMessage('?????????OK????????????ID???????????????ok 3'))
                line_bot_api.reply_message(
                    event.reply_token,
                    array 
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="???????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help"))
                                    ])
                                    )
                    )

        elif str(event.message.text).find("ok") != -1:
            if search_user(user_id) == "Administrator":
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
                    cursor.execute(
                        "UPDATE tenant_info SET check_status='Y' WHERE id='%s'" % (check))
                    cursor.execute(
                        "SELECT email FROM tenant_info WHERE id='%s'" % (check))
                    db.commit()
                    tup = cursor.fetchone()
                    subject = "??????????????????!"
                    sendsuccess(subject, tup[0])
                    print("????????????")
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="????????????")
                    )
                except Exception as e:
                    db.rollback()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="????????????")
                    )
                    print(e)
                db.close()
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="???????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help"))
                                    ])
                                    )
                    )

        elif event.message.text == "????????????????????????":
            if search_user(user_id) == "Administrator":
                notice = search_user_report_list()
                array = []
                array.append(TextSendMessage(notice))
                array.append(TextSendMessage('???????????????????????????ch???\n??????ch 2 ?????????'))
                line_bot_api.reply_message(
                    event.reply_token,
                    array
                )
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="???????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help"))
                                    ])
                                    )
                    )

        elif str(event.message.text).find("ch") != -1 or str(event.message.text).find("Ch") != -1:
            if search_user(user_id) == "Administrator":
                try:
                    data_1, data_2 = str(event.message.text).split('Ch ', 1)
                    id, schedule = str(data_2).split(' ', 1)
                except Exception as e:
                    pass

                try:
                    data_1, data_2 = str(event.message.text).split('ch ', 1)
                    id, schedule = str(data_2).split(' ', 1)
                except Exception as e:
                    pass

                try:
                    db = MySQLdb.connect(host='localhost', port=3306, user='root',
                                         passwd='123qwe', db='room_data', charset='utf8mb4')
                    cursor = db.cursor()
                    cursor.execute(
                        "UPDATE failure_report SET schedule='{0}' WHERE id='{1}'".format(
                            schedule, id))
                    db.commit()
                    print("????????????")
                    subject = "?????????????????????!"
                    useremail = find_user_email(id)
                    attach = "{0}".format(schedule)
                    sendchange(useremail, attach)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="??????????????????")
                    )
                except Exception as e:
                    db.rollback()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="??????????????????")
                    )
                    print(e)
                db.close()
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="???????????????",
                                    items=[
                                        QuickReplyButton(action=MessageAction(
                                            label="????????????", text="????????????")),
                                        QuickReplyButton(action=MessageAction(
                                            label="??????", text="help"))
                                    ])
                )

        elif event.message.text == "????????????":
            if search_user(user_id) == "Administrator":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="?????????find+???????????????find a2",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="??????????????????", text="??????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????????????????", text="????????????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help")),
                                            QuickReplyButton(action=MessageAction(
                                                label="???????????????", text="???????????????"))
                                        ])
                                    ))
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="???????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help"))
                                    ])
                                    )
                    )

        elif str(event.message.text).find("find") != -1 or str(event.message.text).find("Find") != -1:
            if search_user(user_id) == "Administrator":
                try:
                    data_1, data_2 = str(event.message.text).split('find ', 1)
                    check = str(data_2)
                except Exception as e:
                    pass

                try:
                    data_1, data_2 = str(event.message.text).split('Find ', 1)
                    check = str(data_2)
                except Exception as e:
                    pass

                try:
                    db = MySQLdb.connect(host='localhost', port=3306, user='root',
                                         passwd='123qwe', db='room_data', charset='utf8mb4')
                    cursor = db.cursor()
                    cursor.execute(
                        "SELECT room_no,name,phone FROM tenant_info WHERE room_no = '%s'" % (check))
                    db.commit()
                    print(check)
                    output = '???????????????????????????\n'
                    tup = cursor.fetchone()
                    output = output + \
                        str(tup[0]) + ' ' + str(tup[1]) + ' ' + str(tup[2])
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=output,
                                        quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="??????????????????", text="??????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????????????????", text="????????????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help")),
                                            QuickReplyButton(action=MessageAction(
                                                label="???????????????", text="???????????????"))
                                        ])
                                        )
                        )
                    
                except Exception as e:
                    db.rollback()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="??????????????????????????????")
                    )
                    print(e)
                db.close()
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="???????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help"))
                                    ])
                                    )
                    )
        
        elif event.message.text == "???????????????":
            if search_user(user_id) == "Administrator":
                line_bot_api.link_rich_menu_to_user(user_id, "richmenu-a7ce27412aa6f157e8bb3b08d6949579")
                
#------------------mysqlcommand--------------------------
        elif event.message.text == "???????????????????????????":
                    line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=mysql_printalldata())
                    )
        
        elif event.message.text == "?????????????????????":
                    line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="?????? update id ?????? ??????????????????")
                    )

        elif str(event.message.text).find("update") != -1 or str(event.message.text).find("Update") != -1:
            if search_user(user_id) == "Administrator":
                try:
                    data_1, data_2 = str(event.message.text).split('update ', 1)
                    id, title, data, = str(data_2).split(' ', 2)
                    check = str(data_2)
                except Exception as e:
                    pass

                try:
                    data_1, data_2 = str(event.message.text).split('Update ', 1)
                    id, title, data, = str(data_2).split(' ', 2)
                    check = str(data_2)
                except Exception as e:
                    pass
                
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=mysql_modify(id,title,data))
                    )

        elif event.message.text == "?????????????????????":
                    line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="?????? delete id")
                    )
        
        elif str(event.message.text).find("delete") != -1 or str(event.message.text).find("Delete") != -1:
            if search_user(user_id) == "Administrator":
                try:
                    data_1, data_2 = str(event.message.text).split('Delete ', 1)
                    check = str(data_2)
                except Exception as e:
                    pass

                try:
                    data_1, data_2 = str(event.message.text).split('delete ', 1)
                    check = str(data_2)
                except Exception as e:
                    pass
                
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=mysql_delete(check))
                    )
#------------------mysqlcommand--------------------------
# -----------------------------------------------
        elif event.message.text == "??????":
            if search_user(user_id) == 'Y' or search_user(user_id) == 'Administrator':
                client = mqtt.Client()
                client.username_pw_set("yujie", "12345")
                client.connect(mqtt_address, 1883, 60)
                client.publish("esp8266/opendoorsub", "o")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="??????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????????????????", text="??????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????????????????", text="??????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????"))
                                        ]
                                    ))
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="?????????????????????????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help"))
                                        ]))
                )

        elif event.message.text == "??????":
            line_bot_api.reply_message(
                event.reply_token,
                home_poweronoffmenu
            ) 
            
        elif event.message.text == "??????????????????":
            if search_user(user_id) == 'Y' or search_user(user_id) == 'Administrator':
                checkroom = search_user_info(user_id)
                if checkroom[1] == "A1" or search_user(user_id) == 'Administrator':
                    client = mqtt.Client()
                    client.username_pw_set("yujie", "12345")
                    client.connect(mqtt_address, 1883, 60)
                    client.publish("esp8266/opendoorsub", "n")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="???????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="??????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????????????????", text="??????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????????????????", text="??????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????"))
                                        ]
                                    ))
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="?????????????????????????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help"))
                                        ]))
                )

        elif event.message.text == "??????????????????":
            if search_user(user_id) == 'Y' or search_user(user_id) == 'Administrator':
                checkroom = search_user_info(user_id)
                if checkroom[1] == "A1" or search_user(user_id) == 'Administrator':
                    client = mqtt.Client()
                    client.username_pw_set("yujie", "12345")
                    client.connect(mqtt_address, 1883, 60)
                    client.publish("esp8266/opendoorsub", "f")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="???????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="??????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????????????????", text="??????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????????????????", text="??????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????"))
                                        ]
                                    ))
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="?????????????????????????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help"))
                                        ]))
                )
        
        elif event.message.text == "??????":
            line_bot_api.reply_message(
                event.reply_token,
                light_poweronoffmenu
            )   
            
        elif event.message.text == "????????????":
            if search_user(user_id) == 'Y' or search_user(user_id) == 'Administrator':
                checkroom = search_user_info(user_id)
                if checkroom[1] == "A1" or checkroom[1] == "Administrator":
                    client = mqtt.Client()
                    client.username_pw_set("yujie", "12345")
                    client.connect(mqtt_address, 1883, 60)
                    client.publish("esp8266/opendoorsub", "L")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="???????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="??????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????????????????", text="??????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????????????????", text="??????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????"))
                                        ]
                                    ))
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="?????????????????????????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help"))
                                        ]))
                )

        elif event.message.text == "????????????":
            if search_user(user_id) == 'Y' or search_user(user_id) == 'Administrator':
                checkroom = search_user_info(user_id)
                if checkroom[1] == "A1" or checkroom[1] == "Administrator":
                    client = mqtt.Client()
                    client.username_pw_set("yujie", "12345")
                    client.connect(mqtt_address, 1883, 60)
                    client.publish("esp8266/opendoorsub", "l")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="???????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="??????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????????????????", text="??????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????????????????", text="??????????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????"))
                                        ]
                                    ))
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="?????????????????????????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help"))
                                        ]))
                )     
                          
        elif event.message.text == "????????????":
            if search_user(user_id) == 'Y' or search_user(user_id) == 'Administrator':
                curr = currload()
                ser = serial.Serial("COM13",115200,timeout = 5) # ??????com3???????????????115200?????????5
                ser.flushInput() # ???????????????
                DHT_data=[]
                while True:
                    count = ser.inWaiting() # ??????????????????????????????
                    if count !=0 :
                        DHT_data = ser.read(ser.in_waiting).decode("gbk") # ????????????????????????????????????gbk??????
                        if DHT_data != 0:
                            break
                
                
                text1 = str(DHT_data[5:11]) + "???"
                text2 = "??????:" + str(DHT_data[0:4]) + "%RH"
                line_bot_api.reply_message(
                    event.reply_token,
                    [
                    ImageSendMessage(
                        original_content_url=make_temp_pic(text1,text2),
                        preview_image_url=make_temp_pic(text1,text2)
                    ),
                    ImageSendMessage(
                        original_content_url=make_power_pic(curr[1]),
                        preview_image_url=make_power_pic(curr[1])
                    )
                    ]
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="?????????????????????????????????",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="????????????", text="????????????")),
                                            QuickReplyButton(action=MessageAction(
                                                label="??????", text="help"))
                                        ])))

        elif event.message.text == "????????????":
            if(search_user(user_id)) == 'Y' or (search_user(user_id)) == 'Administrator':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="?????????????????????????????????")
                )
            elif(search_user(user_id)) == 'en':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="????????????????????????????????????????????????")
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="?????????????????????add??????????????????????????????????????????\n??????:add ????????? A1 0912345678 TSJ55688@gmail.com")
                )

        elif str(event.message.text).find("Add") != -1 or str(event.message.text).find("add") != -1:
            if(search_user(user_id)) == 'Y':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="?????????????????????????????????")
                )
            elif(search_user(user_id)) == 'en':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="????????????????????????????????????????????????")
                )
            else:
                try:
                    data_1, data_2 = str(event.message.text).split('Add ', 1)
                    name, room_no, phone, email = str(data_2).split(' ', 3)
                except Exception as e:
                    pass

                try:
                    data_1, data_2 = str(event.message.text).split('add ', 1)
                    name, room_no, phone, email = str(data_2).split(' ', 3)
                except Exception as e:
                    pass

                try:
                    db = MySQLdb.connect(host='localhost', port=3306, user='root',
                                         passwd='123qwe', db='room_data', charset='utf8mb4')
                    cursor = db.cursor()
                    try:
                        emailcheckcode = random.randrange(10000, 99999)
                        cursor.execute(
                            "INSERT INTO tenant_info(name,room_no,phone,lineid,email,check_status,emailCheckcode,time) VALUES('%s','%s','%s','%s','%s','en','%s','%s')" % (name, room_no, phone, user_id, email, emailcheckcode,date))
                        db.commit()
                        sendcheckcode(email, emailcheckcode)
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="???????????????????????????????????????????????????????????????")
                        )
                    except Exception as e:
                        print(e)
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="????????????????????????????????????",
                                            items=[
                                                QuickReplyButton(action=MessageAction(
                                                    label="????????????", text="????????????")),
                                                QuickReplyButton(action=MessageAction(
                                                    label="??????", text="help"))
                                            ])
                        )
                except:
                    db.rollback()
                db.close()

        elif event.message.text == "????????????":
            if search_user(user_id) == 'Y' or search_user(user_id) == 'Administrator':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="????????????r?????????????????????\n??????r ???????????????\n??????????????????????????????????????????????????????",
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(action=MessageAction(
                                    label="??????", text="help")),
                                QuickReplyButton(action=MessageAction(
                                    label="????????????", text="????????????")),
                                QuickReplyButton(action=MessageAction(
                                    label="??????", text="??????")),
                                QuickReplyButton(action=MessageAction(
                                    label="??????????????????", text="??????????????????")),
                                QuickReplyButton(action=MessageAction(
                                    label="??????????????????", text="??????????????????")),
                            ]
                        ))
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="?????????????????????????????????",
                                    items=[
                                        QuickReplyButton(action=MessageAction(
                                            label="????????????", text="????????????")),
                                        QuickReplyButton(action=MessageAction(
                                            label="??????", text="help"))
                                    ])
                )
                
        elif event.message.text == "????????????":
            if search_user(user_id) == 'Y' or search_user(user_id) == 'Administrator':
                user_info = search_user_info(user_id)
                output = "?????????{0}\n???????????????{1}".format(user_info[1],user_info[4])
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text=output,
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(action=MessageAction(
                                    label="??????", text="help")),
                                QuickReplyButton(action=MessageAction(
                                    label="????????????", text="????????????")),
                                QuickReplyButton(action=MessageAction(
                                    label="??????", text="??????")),
                                QuickReplyButton(action=MessageAction(
                                    label="??????????????????", text="??????????????????")),
                                QuickReplyButton(action=MessageAction(
                                    label="??????????????????", text="??????????????????")),
                            ]
                        ))
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="?????????????????????????????????",
                                    items=[
                                        QuickReplyButton(action=MessageAction(
                                            label="????????????", text="????????????")),
                                        QuickReplyButton(action=MessageAction(
                                            label="??????", text="help"))
                                    ])
                )
                
        elif str(event.message.text).find("r") != -1 or str(event.message.text).find("r") != -1:
            if search_user(user_id) == 'Y' or search_user(user_id) == 'Administrator':
                try:
                    data_1, data_2 = str(event.message.text).split('r ', 1)
                    check = str(data_2)
                except Exception as e:
                    pass

                try:
                    data_1, data_2 = str(event.message.text).split('R ', 1)
                    check = str(data_2)
                except Exception as e:
                    pass

                try:
                    date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    info = search_user_info(user_id)
                    db = MySQLdb.connect(host='localhost', port=3306, user='root',
                                         passwd='123qwe', db='room_data', charset='utf8mb4')
                    cursor = db.cursor()
                    cursor.execute(
                        "INSERT INTO failure_report(name,room_no,phone,report,date,schedule,email) VALUES ('%s','%s','%s','%s','%s','????????????','%s')" % (info[0], info[1], info[2], data_2, date, info[3]))
                    db.commit()
                    notice = "???????????????????????????????????????\n?????????{0}\n?????????{1}\n?????????{2}\n???????????????{3}\n???????????????{4}\n???????????????'https://imgur.com/a/cvFJ6ib'".format(
                        info[0], info[1], info[2], data_2, date)
                    subject = "??????????????????????????????!"
                    emailnotify(subject, notice)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="?????????????????????????????????????????????!????????????????????????Email??????!",
                                        quick_reply=QuickReply(
                                            items=[
                                                QuickReplyButton(action=MessageAction(
                                                    label="??????", text="help")),
                                            +    QuickReplyButton(action=MessageAction(
                                                    label="????????????", text="????????????")),
                                                QuickReplyButton(action=MessageAction(
                                                    label="??????", text="??????")),
                                                QuickReplyButton(action=MessageAction(
                                                    label="??????????????????", text="??????????????????")),
                                                QuickReplyButton(action=MessageAction(
                                                    label="??????????????????", text="??????????????????")),
                                            ]
                                        ))
                    )
                except Exception as e:
                    db.rollback()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="???????????????")
                    )
                    print(e)
                db.close()
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="???????????????",
                                    items=[
                                        QuickReplyButton(action=MessageAction(
                                            label="????????????", text="????????????")),
                                        QuickReplyButton(action=MessageAction(
                                            label="??????", text="help"))
                                    ])
                )

        elif search_user(user_id) == 'en':
            try:
                if int(echeckcode[0]) >= 10000 and int(echeckcode[0]) <= 99999 and echeckcode[0] == search_emailcheckcode(user_id):
                    update_checkstatus(user_id)
                    userdata = find_user(user_id)
                    notice = "?????????{0}\n?????????{1}\n?????????{2}\n?????????{3}\n???????????????{4}\n\n\n??????LINE?????????!".format(
                        userdata[0], userdata[1], userdata[2], userdata[3], date)
                    subject = "?????????????????????!"
                    emailnotify(subject, notice)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="???????????????????????????????????????"))
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="????????????????????????????????????"))
            except ValueError:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="????????????????????????help???????????????????????????",
                                    items=[
                                        QuickReplyButton(action=MessageAction(
                                            label="????????????", text="????????????")),
                                        QuickReplyButton(action=MessageAction(
                                            label="??????", text="help"))
                                    ])
                )

        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="????????????????????????help???????????????????????????",
                                items=[
                                    QuickReplyButton(action=MessageAction(
                                        label="????????????", text="????????????")),
                                    QuickReplyButton(action=MessageAction(
                                        label="??????", text="help"))
                                ])
            )

    reply_arr = []
    reply_arr.append(TextSendMessage('????????????'))
    reply_arr.append(TextSendMessage('????????????:https://imgur.com/a/cvFJ6ib'))

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
                'static', 'C:/Users/goldcity5/Desktop/project/pylinebot/pic', dist_name)
            client.upload_from_path(path, config=config, anon=False)
            os.remove(path)
            print(path)
            line_bot_api.reply_message(
                event.reply_token,
                reply_arr)
        except:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage('????????????'))
        return 0

#Mysql command
#------------------
def mysql_printalldata():
    try:
        db = MySQLdb.connect(host='localhost', port=3306, user='root',
                             passwd='123qwe', db='room_data', charset='utf8mb4')
        cursor = db.cursor()
        cursor.execute(
            "SELECT id,name,room_no,phone,check_status FROM tenant_info")
        tup = cursor.fetchall()
        notice = "?????????????????????\nid name room_no phone check_status"
        for i in range(len(tup)):
            notice += '\n'
            notice += str(tup[i])
        return notice
    except Exception as e:
        print(e)
    finally:
        db.close()
        
def mysql_modify(mysql_id,mysql_title,mysql_data):
    try:
        db = MySQLdb.connect(host='localhost', port=3306, user='root',
                             passwd='123qwe', db='room_data', charset='utf8mb4')
        cursor = db.cursor()
        cursor.execute(
            ("UPDATE tenant_info SET {0} ='{1}' WHERE id ='{2}'").format(mysql_title,mysql_data,mysql_id))
        db.commit()
    except Exception as e:
        print(e)
        return e
    finally:
        db.close()
        return "sucess"
        
def mysql_delete(mysql_id):
    try:
        db = MySQLdb.connect(host='localhost', port=3306, user='root',
                             passwd='123qwe', db='room_data', charset='utf8mb4')
        cursor = db.cursor()
        cursor.execute(
            ("DELETE FROM tenant_info WHERE id = {0}").format(mysql_id))
        db.commit()
    except Exception as e:
        print(e)
        return e
    finally:
        db.close()
        return "sucess"

#------------------   
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
        
def search_user_info(user_id):
    try:
        db = MySQLdb.connect(host='localhost', port=3306, user='root',
                             passwd='123qwe', db='room_data', charset='utf8mb4')
        cursor = db.cursor()
        cursor.execute(
            "SELECT name,room_no,phone,email,time FROM tenant_info WHERE lineid = '%s'" % (user_id))
        checkcorrect = cursor.fetchone()
        return checkcorrect
    except Exception as e:
        print(e)
    finally:
        db.close()


def search_emailcheckcode(user_id):
    try:
        db = MySQLdb.connect(host='localhost', port=3306, user='root',
                             passwd='123qwe', db='room_data', charset='utf8mb4')
        cursor = db.cursor()
        cursor.execute(
            "SELECT emailCheckcode FROM tenant_info WHERE lineid = '%s'" % (user_id))
        checkcorrect = cursor.fetchone()
        return checkcorrect[0]
    except Exception as e:
        print(e)
    finally:
        db.close()


def update_checkstatus(user_id):
    try:
        db = MySQLdb.connect(host='localhost', port=3306, user='root',
                             passwd='123qwe', db='room_data', charset='utf8mb4')
        cursor = db.cursor()
        cursor.execute(
            "UPDATE tenant_info SET check_status='n' WHERE lineid='%s'" % (user_id))
        db.commit()
    except Exception as e:
        print(e)
    finally:
        db.close()


def search_user_register_list():
    try:
        db = MySQLdb.connect(host='localhost', port=3306, user='root',
                             passwd='123qwe', db='room_data', charset='utf8mb4')
        cursor = db.cursor()
        cursor.execute(
            "SELECT id,name,room_no,phone,check_status FROM tenant_info WHERE check_status = 'n'")
        tup = cursor.fetchall()
        notice = "?????????????????????"
        for i in range(len(tup)):
            notice += '\n'
            notice += str(tup[i])
        return notice
    except Exception as e:
        print(e)
    finally:
        db.close()


def find_user(user_id):
    try:
        db = MySQLdb.connect(host='localhost', port=3306, user='root',
                             passwd='123qwe', db='room_data', charset='utf8mb4')
        cursor = db.cursor()
        cursor.execute(
            "SELECT name,room_no,phone,email FROM tenant_info WHERE lineid = '%s'" % (user_id))
        db.commit()
        tup = cursor.fetchone()
        return tup
    except Exception as e:
        print(e)
    finally:
        db.close()


def find_user_email(id):
    try:
        db = MySQLdb.connect(host='localhost', port=3306, user='root',
                             passwd='123qwe', db='room_data', charset='utf8mb4')
        cursor = db.cursor()
        cursor.execute(
            "SELECT email FROM failure_report WHERE id='%s'" % (id))
        db.commit()
        tup = cursor.fetchone()
        return tup[0]
    except Exception as e:
        print(e)
    db.close()


def search_user_report_list():
    try:
        db = MySQLdb.connect(host='localhost', port=3306, user='root',
                             passwd='123qwe', db='room_data', charset='utf8mb4')
        cursor = db.cursor()
        cursor.execute(
            "SELECT id,name,room_no,phone,report,date,schedule FROM failure_report WHERE schedule != '?????????'")
        tup = cursor.fetchall()
        notice = "???????????????????????????"
        for i in range(len(tup)):
            notice += '\n'
            notice += str(tup[i])
        return notice
    except Exception as e:
        print(e)
    finally:
        db.close()


def currload():
    url = 'https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/loadpara.json'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.62'}
    response = requests.get(url=url, headers=headers, timeout=5)
    doc = response.json()
    doc1 = doc['records']
    dict1 = {}
    dict1 = doc1[0]
    currload = dict1['curr_load']
    dict3 = {}
    dict3 = doc1[2]
    powerstatus = dict3['yday_peak_resv_indicator']
    try:
        dict2 = {}
        dict2 = doc1[3]
        realmaxicapacity = dict2['real_hr_maxi_sply_capacity']
        usagerate = (float(currload)/float(realmaxicapacity))
        usagerate = round(usagerate*100)
        usagerate = str(usagerate) + '%'
    except IndexError:
        usagerate = '(????????????????????????)'
    if(powerstatus == "G"):
        powerstatus = "????????????"
    elif(powerstatus == "Y"):
        powerstatus = "????????????"
    else:
        powerstatus = "????????????"
    return currload, usagerate, powerstatus


def emailnotify(subject, notice):
    content = MIMEMultipart()  # ??????MIMEMultipart??????
    content["subject"] = subject  # ????????????
    content["from"] = "jay002200@gmail.com"  # ?????????
    content["to"] = "jay002200@gmail.com"  # ?????????
    content.attach(
        MIMEText("{0}".format(notice)))  # ????????????

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # ??????SMTP?????????
        try:
            smtp.ehlo()  # ??????SMTP?????????
            smtp.starttls()  # ??????????????????
            smtp.login("jay002200@gmail.com", "rgtvetnfbrlvwgkv")  # ???????????????gmail
            smtp.send_message(content)  # ????????????
            smtp.quit()
            print("????????????!")
        except Exception as e:
            print("Error message: ", e)


def sendcheckcode(email, emailcheckcode):
    content = MIMEMultipart()  # ??????MIMEMultipart??????
    content["subject"] = "?????????????????????"  # ????????????
    content["from"] = "jay002200@gmail.com"  # ?????????
    content["to"] = email  # ?????????
    content.attach(
        MIMEText("?????????????????????{0}".format(emailcheckcode)))  # ????????????

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # ??????SMTP?????????
        try:
            smtp.ehlo()  # ??????SMTP?????????
            smtp.starttls()  # ??????????????????
            smtp.login("jay002200@gmail.com", "rgtvetnfbrlvwgkv")  # ???????????????gmail
            smtp.send_message(content)  # ????????????
            print("????????????!")
            smtp.quit()
        except Exception as e:
            print("Error message: ", e)


def sendsuccess(subject, email):
    content = MIMEMultipart()  # ??????MIMEMultipart??????
    content["subject"] = subject  # ????????????
    content["from"] = "jay002200@gmail.com"  # ?????????
    content["to"] = email  # ?????????
    content.attach(
        MIMEText("??????????????????????????????!???????????????????????????!"))  # ????????????

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # ??????SMTP?????????
        try:
            smtp.ehlo()  # ??????SMTP?????????
            smtp.starttls()  # ??????????????????
            smtp.login("jay002200@gmail.com", "rgtvetnfbrlvwgkv")  # ???????????????gmail
            smtp.send_message(content)  # ????????????
            print("????????????!")
            smtp.quit()
        except Exception as e:
            print("Error message: ", e)


def sendchange(email, attach):
    content = MIMEMultipart()  # ??????MIMEMultipart??????
    content["subject"] = "?????????????????????!"  # ????????????
    content["from"] = "jay002200@gmail.com"  # ?????????
    content["to"] = email  # ?????????
    content.attach(
        MIMEText("???????????????????????????{0}".format(attach)))  # ????????????

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # ??????SMTP?????????
        try:
            smtp.ehlo()  # ??????SMTP?????????
            smtp.starttls()  # ??????????????????
            smtp.login("jay002200@gmail.com", "rgtvetnfbrlvwgkv")  # ???????????????gmail
            smtp.send_message(content)  # ????????????
            print("????????????!")
            smtp.quit()
        except Exception as e:
            print("Error message: ", e)

def make_temp_pic(text,text1):
    img = cv2.imread("temperature.png")
    imgPil = Image.fromarray(img)
    fontPath = "./font.ttf"
    font = ImageFont.truetype(fontPath,120)
    font1 = ImageFont.truetype(fontPath,50)
    draw = ImageDraw.Draw(imgPil)
    draw.text((142,121),text,font=font,fill=(0,0,0))
    draw.text((210,305),text1,font=font1,fill=(0,0,0))
    img = np.array(imgPil)
    name = (''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8)))
    name += ".jpg"
    path = "C:\\Users\\goldcity5\\Desktop\\project\\pylinebot\\temperature\\"
    path += name
    cv2.imwrite(path,img)
    im = pyimgur.Imgur(client_id)
    uploaded_image = im.upload_image(path,title="123")
    os.remove(path)
    return(uploaded_image.link)

def make_power_pic(text):
    img = cv2.imread("power.png")
    imgPil = Image.fromarray(img)
    fontPath = "./font.ttf"
    font = ImageFont.truetype(fontPath,120)
    draw = ImageDraw.Draw(imgPil)
    draw.text((478,489),text,font=font,fill=(0,0,0))
    img = np.array(imgPil)
    name = (''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8)))
    name += ".jpg"
    path = "C:\\Users\\goldcity5\\Desktop\\project\\pylinebot\\power\\"
    path += name
    cv2.imwrite(path,img)
    im = pyimgur.Imgur(client_id)
    uploaded_image = im.upload_image(path,title="123")
    os.remove(path)
    return(uploaded_image.link)
  
@ handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="?????????????????????????????????'????????????'?????????????????????????????????",
                        items=[
                            QuickReplyButton(action=MessageAction(
                                label="????????????", text="????????????")),
                            QuickReplyButton(action=MessageAction(
                                label="??????", text="??????"))
                        ]))

@handler.add(PostbackEvent)
def handle_postback(event):
    # postback ??????
    data = event.postback.data
    # ?????????Id
    userId = event.source.user_id
    
    # ?????????
    if data == "action=prev":
        # ????????????????????????
        line_bot_api.unlink_rich_menu_from_user(userId) 
        
    if data == "action=next":
        line_bot_api.link_rich_menu_to_user(userId, "richmenu-55851767f95250f7f79f8054f5345e13")

if __name__ == "__main__":
    app.run()
