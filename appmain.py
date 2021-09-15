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
# --------------Administrator--------------------------------
        if event.message.text == "help" or event.message.text == "Help":
            if search_user(user_id) == "Administrator":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="用戶註冊列表 : 列出要註冊的房客列表。\n查詢房客 : 列出房客資訊\n房客回報問題列表：列出房客問題回報",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="用戶註冊列表", text="用戶註冊列表")),
                                            QuickReplyButton(action=MessageAction(
                                                label="房客回報問題列表", text="房客回報問題列表")),
                                            QuickReplyButton(action=MessageAction(
                                                label="查詢房客", text="查詢房客")),
                                            QuickReplyButton(action=MessageAction(
                                                label="幫助", text="help")),
                                        ]))
                )
            else:
                if(search_user(user_id) == 'Y'):
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text="故障回報 : 宿舍各項問題及故障回報。\n開門 ： 打開宿舍大門\n電器關閉/開啟 : 開啟或關閉插座的電源。",
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(action=MessageAction(
                                        label="幫助", text="help")),
                                    QuickReplyButton(action=MessageAction(
                                        label="故障回報", text="故障回報")),
                                    QuickReplyButton(action=MessageAction(
                                        label="開門", text="開門")),
                                    QuickReplyButton(action=MessageAction(
                                        label="開啟電器", text="開啟電器")),
                                    QuickReplyButton(action=MessageAction(
                                        label="關閉電器", text="關閉電器")),
                                    
                                ])))
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text="房客註冊 : 新加入的房客輸入自己的資料，驗證過後即可使用功能。\n(您尚未註冊)",
                            quick_reply=QuickReply(
                                items=[
                                    QuickReplyButton(action=MessageAction(
                                        label="房客註冊", text="房客註冊")),
                                    QuickReplyButton(action=MessageAction(
                                        label="幫助", text="help"))
                                ])))

        elif event.message.text == "用戶註冊列表":
            if search_user(user_id) == "Administrator":
                notice = search_user_register_list()
                array = []
                array.append(TextSendMessage(notice))
                array.append(TextSendMessage('先輸入OK，再輸入ID號碼。例：ok 3'))
                line_bot_api.reply_message(
                    event.reply_token,
                    array
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你沒有權限",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="用戶註冊列表", text="用戶註冊列表")),
                                            QuickReplyButton(action=MessageAction(
                                                label="房客回報問題列表", text="房客回報問題列表")),
                                            QuickReplyButton(action=MessageAction(
                                                label="查詢房客", text="查詢房客")),
                                            QuickReplyButton(action=MessageAction(
                                                label="查看回報", text="查看回報")),
                                            QuickReplyButton(action=MessageAction(
                                                label="幫助", text="help")),
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
                    subject = "身分認證成功!"
                    sendsuccess(subject, tup[0])
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
                    TextSendMessage(text="你沒有權限",
                                    items=[
                                        QuickReplyButton(action=MessageAction(
                                            label="房客註冊", text="房客註冊")),
                                        QuickReplyButton(action=MessageAction(
                                            label="幫助", text="help"))
                                    ])
                )

        elif event.message.text == "房客回報問題列表":
            if search_user(user_id) == "Administrator":
                notice = search_user_report_list()
                array = []
                array.append(TextSendMessage(notice))
                array.append(TextSendMessage('更改進度，請先輸入ch。\n例：ch 2 檢查中'))
                line_bot_api.reply_message(
                    event.reply_token,
                    array,
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你沒有權限",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="用戶註冊列表", text="用戶註冊列表")),
                                            QuickReplyButton(action=MessageAction(
                                                label="查詢房客", text="查詢房客")),
                                            QuickReplyButton(action=MessageAction(
                                                label="查看回報", text="查看回報")),
                                            QuickReplyButton(action=MessageAction(
                                                label="幫助", text="help")),
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
                    print("修改成功")
                    subject = "維修進度已變動!"
                    useremail = find_user_email(id)
                    attach = "{0}".format(schedule)
                    sendchange(useremail, attach)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="進度修改完成")
                    )
                except Exception as e:
                    db.rollback()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="進度修改失敗")
                    )
                    print(e)
                db.close()
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你沒有權限",
                                    items=[
                                        QuickReplyButton(action=MessageAction(
                                            label="房客註冊", text="房客註冊")),
                                        QuickReplyButton(action=MessageAction(
                                            label="幫助", text="help"))
                                    ])
                )

        elif event.message.text == "查詢房客":
            if search_user(user_id) == "Administrator":
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="請輸入find+房號，例：find a2",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="幫助", text="help")),
                                            QuickReplyButton(action=MessageAction(
                                                label="故障回報", text="故障回報")),
                                            QuickReplyButton(action=MessageAction(
                                                label="開門", text="開門")),
                                            QuickReplyButton(action=MessageAction(
                                                label="開啟電器", text="開啟電器")),
                                            QuickReplyButton(action=MessageAction(
                                                label="關閉電器", text="關閉電器")),
                                        ]
                                    ))
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你沒有權限",
                                    items=[
                                        QuickReplyButton(action=MessageAction(
                                            label="房客註冊", text="房客註冊")),
                                        QuickReplyButton(action=MessageAction(
                                            label="幫助", text="help"))
                                    ])
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
                    output = '查詢到的資料如下；\n'
                    tup = cursor.fetchone()
                    output = output + \
                        str(tup[0]) + ' ' + str(tup[1]) + ' ' + str(tup[2])
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text=output,
                                        quick_reply=QuickReply(
                                            items=[
                                                QuickReplyButton(action=MessageAction(
                                                    label="幫助", text="help")),
                                                QuickReplyButton(action=MessageAction(
                                                    label="故障回報", text="故障回報")),
                                                QuickReplyButton(action=MessageAction(
                                                    label="開門", text="開門")),
                                                QuickReplyButton(action=MessageAction(
                                                    label="開啟電器", text="開啟電器")),
                                                QuickReplyButton(action=MessageAction(
                                                    label="關閉電器", text="關閉電器")),
                                            ]
                                        ))
                    )
                except Exception as e:
                    db.rollback()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="查無資料或查詢失敗。")
                    )
                    print(e)
                db.close()
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你沒有權限",
                                    items=[
                                        QuickReplyButton(action=MessageAction(
                                            label="房客註冊", text="房客註冊")),
                                        QuickReplyButton(action=MessageAction(
                                            label="幫助", text="help"))
                                    ])
                )
# -----------------------------------------------
        elif event.message.text == "開門":
            if search_user(user_id) == 'Y' or search_user(user_id) == 'Administrator':
                client = mqtt.Client()
                client.username_pw_set("yujie", "12345")
                client.connect(mqtt_address, 1883, 60)
                client.publish("esp8266/opendoorsub", "o")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="門已開啟",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="幫助", text="help")),
                                            QuickReplyButton(action=MessageAction(
                                                label="故障回報", text="故障回報")),
                                            QuickReplyButton(action=MessageAction(
                                                label="開門", text="開門")),
                                            QuickReplyButton(action=MessageAction(
                                                label="開啟電器", text="開啟電器")),
                                            QuickReplyButton(action=MessageAction(
                                                label="關閉電器", text="關閉電器")),
                                        ]
                                    ))
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="非本棟用戶，拒絕使用。",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="房客註冊", text="房客註冊")),
                                            QuickReplyButton(action=MessageAction(
                                                label="幫助", text="help"))
                                        ]))
                )

        elif event.message.text == "開啟電器":
            if search_user(user_id) == 'Y' or search_user(user_id) == 'Administrator':
                client = mqtt.Client()
                client.username_pw_set("yujie", "12345")
                client.connect(mqtt_address, 1883, 60)
                client.publish("esp8266/opendoorsub", "n")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="電源已開啟",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="幫助", text="help")),
                                            QuickReplyButton(action=MessageAction(
                                                label="故障回報", text="故障回報")),
                                            QuickReplyButton(action=MessageAction(
                                                label="開門", text="開門")),
                                            QuickReplyButton(action=MessageAction(
                                                label="開啟電器", text="開啟電器")),
                                            QuickReplyButton(action=MessageAction(
                                                label="關閉電器", text="關閉電器")),
                                        ]
                                    ))
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="非本棟用戶，拒絕使用。",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="房客註冊", text="房客註冊")),
                                            QuickReplyButton(action=MessageAction(
                                                label="幫助", text="help"))
                                        ]))
                )

        elif event.message.text == "關閉電器":
            if search_user(user_id) == 'Y' or search_user(user_id) == 'Administrator':
                client = mqtt.Client()
                client.username_pw_set("yujie", "12345")
                client.connect(mqtt_address, 1883, 60)
                client.publish("esp8266/opendoorsub", "f")
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="電源已關閉",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="幫助", text="help")),
                                            QuickReplyButton(action=MessageAction(
                                                label="故障回報", text="故障回報")),
                                            QuickReplyButton(action=MessageAction(
                                                label="開門", text="開門")),
                                            QuickReplyButton(action=MessageAction(
                                                label="開啟電器", text="開啟電器")),
                                            QuickReplyButton(action=MessageAction(
                                                label="關閉電器", text="關閉電器")),
                                        ]
                                    ))
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="非本棟用戶，拒絕使用。",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="房客註冊", text="房客註冊")),
                                            QuickReplyButton(action=MessageAction(
                                                label="幫助", text="help"))
                                        ]))
                )
                   
        elif event.message.text == "房間資訊":
            if search_user(user_id) == 'Y':
                curr = currload()
                text1 = "房間目前溫度：\n房間目前濕度：\n\n\n台灣目前用電量：{0}萬千瓦\n目前使用率：{1}\n{2}".format(
                    curr[0], curr[1], curr[2])
                text2 = "\n\n(資料來自台電官網)"
                text1 += text2
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=text1,
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="幫助", text="help")),
                                            QuickReplyButton(action=MessageAction(
                                                label="故障回報", text="故障回報")),
                                            QuickReplyButton(action=MessageAction(
                                                label="開門", text="開門")),
                                            QuickReplyButton(action=MessageAction(
                                                label="開啟電器", text="開啟電器")),
                                            QuickReplyButton(action=MessageAction(
                                                label="關閉電器", text="關閉電器")),
                                        ]
                                    ))
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="非本棟用戶，拒絕使用。",
                                    quick_reply=QuickReply(
                                        items=[
                                            QuickReplyButton(action=MessageAction(
                                                label="房客註冊", text="房客註冊")),
                                            QuickReplyButton(action=MessageAction(
                                                label="幫助", text="help"))
                                        ])))

        elif event.message.text == "房客註冊":
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(
                    text="請先輸入關鍵字add，輸入姓名、房號、電話和信箱\n範例:add 田中央 A1 0912345678 TSJ55688@gmail.com")
            )

        elif str(event.message.text).find("Add") != -1 or str(event.message.text).find("add") != -1:
            if(search_user) == 'Y':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="您已註冊過，無需註冊。")
                )
            elif(search_user) == 'en':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="請至信箱收取驗證碼後輸入驗證碼。")
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
                            "INSERT INTO tenant_info(name,room_no,phone,lineid,email,check_status,emailCheckcode) VALUES('%s','%s','%s','%s','%s','en','%s')" % (name, room_no, phone, user_id, email, emailcheckcode))
                        db.commit()
                        sendcheckcode(email, emailcheckcode)
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="輸入成功，請去信箱確認驗證信後輸入驗證碼。")
                        )
                    except Exception as e:
                        print(e)
                    else:
                        line_bot_api.reply_message(
                            event.reply_token,
                            TextSendMessage(text="輸入失敗，請詢問管理員。",
                                            items=[
                                                QuickReplyButton(action=MessageAction(
                                                    label="房客註冊", text="房客註冊")),
                                                QuickReplyButton(action=MessageAction(
                                                    label="幫助", text="help"))
                                            ])
                        )
                except:
                    db.rollback()
                db.close()

        elif event.message.text == "故障回報":
            if search_user(user_id) == 'Y' or search_user(user_id) == 'Administrator':
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="請先輸入r，再描述問題。\n例：r 電燈壞了。\n如果要附照片，直接上傳至聊天室即可。",
                        quick_reply=QuickReply(
                            items=[
                                QuickReplyButton(action=MessageAction(
                                    label="幫助", text="help")),
                                QuickReplyButton(action=MessageAction(
                                    label="故障回報", text="故障回報")),
                                QuickReplyButton(action=MessageAction(
                                    label="開門", text="開門")),
                                QuickReplyButton(action=MessageAction(
                                    label="開啟電器", text="開啟電器")),
                                QuickReplyButton(action=MessageAction(
                                    label="關閉電器", text="關閉電器")),
                            ]
                        ))
                )
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="非本棟用戶，拒絕使用。",
                                    items=[
                                        QuickReplyButton(action=MessageAction(
                                            label="房客註冊", text="房客註冊")),
                                        QuickReplyButton(action=MessageAction(
                                            label="幫助", text="help"))
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
                        "INSERT INTO failure_report(name,room_no,phone,report,date,schedule,email) VALUES ('%s','%s','%s','%s','%s','尚未檢查','%s')" % (info[0], info[1], info[2], data_2, date, info[3]))
                    db.commit()
                    notice = "以下是房客的故障問題回報：\n姓名：{0}\n房號：{1}\n電話：{2}\n問題描述：{3}\n回報日期：{4}\n相簿網址：'https://imgur.com/a/cvFJ6ib'".format(
                        info[0], info[1], info[2], data_2, date)
                    subject = "房客故障問題回報通知!"
                    emailnotify(subject, notice)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="輸入完成，管理員會盡快回覆處理!進度變動後會主動Email通知!",
                                        quick_reply=QuickReply(
                                            items=[
                                                QuickReplyButton(action=MessageAction(
                                                    label="幫助", text="help")),
                                                QuickReplyButton(action=MessageAction(
                                                    label="故障回報", text="故障回報")),
                                                QuickReplyButton(action=MessageAction(
                                                    label="開門", text="開門")),
                                                QuickReplyButton(action=MessageAction(
                                                    label="開啟電器", text="開啟電器")),
                                                QuickReplyButton(action=MessageAction(
                                                    label="關閉電器", text="關閉電器")),
                                            ]
                                        ))
                    )
                except Exception as e:
                    db.rollback()
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="輸入失敗。")
                    )
                    print(e)
                db.close()
            else:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="你沒有權限",
                                    items=[
                                        QuickReplyButton(action=MessageAction(
                                            label="房客註冊", text="房客註冊")),
                                        QuickReplyButton(action=MessageAction(
                                            label="幫助", text="help"))
                                    ])
                )

        elif search_user(user_id) == 'en':
            try:
                if int(echeckcode[0]) >= 10000 and int(echeckcode[0]) <= 99999 and echeckcode[0] == search_emailcheckcode(user_id):
                    update_checkstatus(user_id)
                    userdata = find_user(user_id)
                    notice = "姓名：{0}\n房號：{1}\n電話：{2}\n信箱：{3}\n註冊時間：{4}\n\n\n請至LINE上確認!".format(
                        userdata[0], userdata[1], userdata[2], userdata[3], date)
                    subject = "新房客註冊通知!"
                    emailnotify(subject, notice)
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="輸入成功，等待管理員認證。"))
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        TextSendMessage(text="驗證碼錯誤，請重新輸入。"))
            except ValueError:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="指令錯誤，請輸入help確認目前可用指令。",
                                    items=[
                                        QuickReplyButton(action=MessageAction(
                                            label="房客註冊", text="房客註冊")),
                                        QuickReplyButton(action=MessageAction(
                                            label="幫助", text="help"))
                                    ])
                )

        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="指令錯誤，請輸入help確認目前可用指令。",
                                items=[
                                    QuickReplyButton(action=MessageAction(
                                        label="房客註冊", text="房客註冊")),
                                    QuickReplyButton(action=MessageAction(
                                        label="幫助", text="help"))
                                ])
            )

    reply_arr = []
    reply_arr.append(TextSendMessage('上傳成功'))
    reply_arr.append(TextSendMessage('相簿網址:https://imgur.com/a/-'))

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


def search_user_info(user_id):
    try:
        db = MySQLdb.connect(host='localhost', port=3306, user='root',
                             passwd='123qwe', db='room_data', charset='utf8mb4')
        cursor = db.cursor()
        cursor.execute(
            "SELECT name,room_no,phone,email FROM tenant_info WHERE lineid = '%s'" % (user_id))
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
            "SELECT id,name,phone,check_status FROM tenant_info WHERE check_status = 'n'")
        tup = cursor.fetchall()
        notice = "房客註冊列表："
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
            "SELECT id,name,room_no,phone,report,date,schedule FROM failure_report WHERE schedule != '已解決'")
        tup = cursor.fetchall()
        notice = "房客回報問題列表："
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
        usagerate = '(台電目前未給資料)'
    if(powerstatus == "G"):
        powerstatus = "供電充裕"
    elif(powerstatus == "Y"):
        powerstatus = "供電吃緊"
    else:
        powerstatus = "供電緊戒"
    return currload, usagerate, powerstatus


def emailnotify(subject, notice):
    content = MIMEMultipart()  # 建立MIMEMultipart物件
    content["subject"] = subject  # 郵件標題
    content["from"] = "-"  # 寄件者
    content["to"] = "-"  # 收件者
    content.attach(
        MIMEText("{0}".format(notice)))  # 郵件內容

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login("-", "-")  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            smtp.quit()
            print("傳送成功!")
        except Exception as e:
            print("Error message: ", e)


def sendcheckcode(email, emailcheckcode):
    content = MIMEMultipart()  # 建立MIMEMultipart物件
    content["subject"] = "註冊宿舍驗證碼"  # 郵件標題
    content["from"] = "-"  # 寄件者
    content["to"] = email  # 收件者
    content.attach(
        MIMEText("您的驗證碼為：{0}".format(emailcheckcode)))  # 郵件內容

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login("-", "-")  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("傳送成功!")
            smtp.quit()
        except Exception as e:
            print("Error message: ", e)


def sendsuccess(subject, email):
    content = MIMEMultipart()  # 建立MIMEMultipart物件
    content["subject"] = subject  # 郵件標題
    content["from"] = "-"  # 寄件者
    content["to"] = email  # 收件者
    content.attach(
        MIMEText("您的資料已經認證成功!可開始使用各項功能!"))  # 郵件內容

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login("-@gmail.com", "-")  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("傳送成功!")
            smtp.quit()
        except Exception as e:
            print("Error message: ", e)


def sendchange(email, attach):
    content = MIMEMultipart()  # 建立MIMEMultipart物件
    content["subject"] = "維修進度已變動!"  # 郵件標題
    content["from"] = "-@gmail.com"  # 寄件者
    content["to"] = email  # 收件者
    content.attach(
        MIMEText("維修進度已變更成：{0}".format(attach)))  # 郵件內容

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login("-", "-")  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("傳送成功!")
            smtp.quit()
        except Exception as e:
            print("Error message: ", e)


@ handler.add(FollowEvent)
def handle_follow(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="想使用各項功能請先輸入'房客註冊'，認證後即可使用服務。",
                        items=[
                            QuickReplyButton(action=MessageAction(
                                label="房客註冊", text="房客註冊")),
                            QuickReplyButton(action=MessageAction(
                                label="幫助", text="幫助"))
                        ]))


if __name__ == "__main__":
    app.run()
