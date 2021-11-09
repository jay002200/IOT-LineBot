from linebot import (
    LineBotApi, WebhookHandler
)

line_bot_api = LineBotApi('H5ExUQxWHnJmOQlGUh0/SDmxb/8AZvKrOAqoGHARDfpMA1yrXJRnME0uL0NSzNxbGYkvPrk56VBs5D9gmwyh1rUoktZpeHcGfgHvp18mtX6pjF3zB4fH6/MUrWWB7CXankjsBfeXV2Gy143lbN74CQdB04t89/1O/w1cDnyilFU=')

rich_menu_list = line_bot_api.get_rich_menu_list()

# for rich_menu in rich_menu_list:
#     print(rich_menu.rich_menu_id)

# for rich_menu in rich_menu_list:
#     line_bot_api.delete_rich_menu(rich_menu.rich_menu_id)
line_bot_api.delete_rich_menu("richmenu-0b37c661bb416efbbb714776007d3b7b")