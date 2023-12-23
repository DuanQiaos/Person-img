import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram.ext import MessageHandler, Filters
from PIL import Image, ImageDraw, ImageFont
import requests
import json
# 填入你的机器人 token
token = 'xxx'

def get_address_from_cid(id_number):
    # 使用提供的URL和身份证号码进行请求
    url = f'http://127.0.0.1:8001/?cid={id_number}'
    response = requests.get(url)

    if response.status_code == 200:
        json_response = json.loads(response.text)
        address = json_response.get('result', '')
        print(address)
        return address
    else:
        return None


def process_image(name, address, id_number):
    base_image = Image.open('a.jpg')
    overlay_image = Image.open('datou.jpg')

    draw = ImageDraw.Draw(base_image)

    # 指定字体和文字大小
    font_path = "b.ttf"  # 替换为你的字体文件路径

    text_data = [
        {"text": name, "x": 470, "y": 235, "font_size": 40},
        {"text": address, "x": 550, "y": 405, "font_size": 30},
        {"text": id_number, "x": 550, "y": 500, "font_size": 40}
    ]

    for data in text_data:
        font = ImageFont.truetype(font_path, data["font_size"])
        draw.text((data["x"], data["y"]), data["text"], fill=(0, 0, 0), font=font)

    birth_date = f"{id_number[6:10]}年{id_number[10:12]}月{id_number[12:14]}日"
    font = ImageFont.truetype(font_path, 40)  # 定义字体
    draw.text((550, 320), f"{birth_date}", fill=(0, 0, 0), font=font)

    base_image.paste(overlay_image, (0, 200))

    base_image.save('output.jpg')


def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('''
欢迎使用裸户加版工具
---------------大头加板----------------
(注意 发送命令前 先发大头照片)
发送 /make_id 姓名 身份证号 来生成PLC蓝白板
--------------------------------------------
Powerd By @duanqiao_Build
''')

def make_id(update: Update, context: CallbackContext) -> None:
    user_input = context.args
    if len(user_input) != 2:
        update.message.reply_text('请按照正确格式发送：/make_id 姓名 身份证号')
        return
    name, id_number = user_input

    # 使用身份证号码获取地址
    # 这里使用另一个工具 根据身份证开头获取地址 并且随机xx路xx号
    address = get_address_from_cid(id_number)
    if address is None:
        update.message.reply_text('无法获取地址，请稍后再试。')
        return

    process_image(name, address, id_number)
    with open('output.jpg', 'rb') as photo:
        update.message.reply_photo(photo)

def handle_photo(update: Update, context: CallbackContext) -> None:
    photo = update.message.photo[-1].get_file()

    photo.download('datou.jpg')

    update.message.reply_text('''
保存照片成功,接下来请发送命令
例 /make_id xxx 123123123123123
''')

def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    # 设置代理
    request_kwargs = {
        'proxy_url': 'socks5://127.0.0.1:10808',
    }

    updater = Updater(token, use_context=True, request_kwargs=request_kwargs)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("make_id", make_id))
    dp.add_handler(MessageHandler(Filters.photo, handle_photo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
