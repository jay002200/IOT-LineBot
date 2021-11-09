from linebot import (
    LineBotApi, WebhookHandler
)

line_bot_api = LineBotApi('channel_access_token')

rich_menu_list = line_bot_api.get_rich_menu_list()

# for rich_menu in rich_menu_list:
#     print(rich_menu.rich_menu_id)

# for rich_menu in rich_menu_list:
#     line_bot_api.delete_rich_menu(rich_menu.rich_menu_id)
line_bot_api.delete_rich_menu("richmenu-0b37c661bb416efbbb714776007d3b7b")