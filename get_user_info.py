#coding=utf-8
#author:Douglas Xie

import itchat
import json
import requests
import codecs

from pandas import DataFrame


sex_dict = {'0': "其他",
            '1': "男",
            '2': "女"}


tuling_white_list = []
ask_list = []

# 图灵机器人API
def tuling(info):
    appkey = "338e06fdb0ec4a2283938aa997b2828d"
    url = "http://www.tuling123.com/openapi/api?key=%s&info=%s"%(appkey,info)
    req = requests.get(url)
    content = req.text
    data = json.loads(content)
    answer = data['text']
    return answer

# 更新图灵机器人白名单.
def update_tuling_white_list(frined_list):
    global tuling_white_list
    json_file_tuling_white_list = './data/tuling_white_list.json'

    simple_friend_list = []
    for friend in friends_list:
        simple_friend_list.append(friend['UserName'])

    try:
        with codecs.open(json_file_tuling_white_list, encoding='utf-8') as f:
            tuling_white_list = json.load(f)

        for person in tuling_white_list:
            if person['UserName'] not in simple_friend_list:
                tuling_white_list.remove(person)
    except:
        tuling_white_list = [friends_list[0]['UserName']]

    with codecs.open(json_file_tuling_white_list, 'w', encoding='utf-8') as f:
        f.write(json.dumps(tuling_white_list, ensure_ascii=False))

# 下载好友头像
def download_images(frined_list):
    image_dir = "./images/"
    num = 1
    for friend in frined_list:
        image_name = str(num)+'.jpg'
        num+=1
        img = itchat.get_head_img(userName=friend["UserName"])
        with open(image_dir+image_name, 'wb') as file:
            file.write(img)

# 保存好友信息
def save_data(frined_list):
    out_file_name = "./data/friends.json"
    with codecs.open(out_file_name, 'w', encoding='utf-8') as json_file:
        json_file.write(json.dumps(frined_list,ensure_ascii=False))

    frame = DataFrame(frined_list)
    frame.to_excel("./data/friends.xlsx", index=True)

# 文字消息自动回复
@itchat.msg_register([itchat.content.TEXT, itchat.content.MAP, itchat.content.CARD, itchat.content.NOTE, itchat.content.SHARING])
def text_reply(msg):
    print("msg_in: %s: %s" % (msg['FromUserName'], msg['Text']))
    if msg['FromUserName'] in tuling_white_list:
        itchat.send('AI: %s' % tuling(msg['Text']), msg['FromUserName'])

# 图片，视频文件自动回复
@itchat.msg_register([itchat.content.PICTURE, itchat.content.RECORDING, itchat.content.ATTACHMENT, itchat.content.VIDEO])
def download_files(msg):
    msg.download("./download/" + msg.fileName)
    typeSymbol = {
        itchat.content.PICTURE: 'img',
        itchat.content.VIDEO: 'vid', }.get(msg.type, 'fil')
    return '@%s@%s' % (typeSymbol, msg.fileName)

# 群消息自动回复
@itchat.msg_register(itchat.content.TEXT, isGroupChat=True)
def group_text_reply(msg):
    if msg.isAt:
        print("group_msg_in: %s at me: %s" % (msg['actualNickName'], msg['Text']))
        print("msg raw: ", msg)
        # msg.user.send(u'@%s\u2005 I received: %s' % (
        #     msg.actualNickName, msg.text))


if __name__ == '__main__':

    itchat.auto_login(hotReload=True)    

    #获取好友信息
    friends = itchat.get_friends(update=True)[0:]
    friends_list = []
    for friend in friends:
        item = {}
        item['NickName'] = friend['NickName']
        item['HeadImgUrl'] = friend['HeadImgUrl']
        item['Sex'] = sex_dict[str(friend['Sex'])]
        item['Province'] = friend['Province']
        item['Signature'] = friend['Signature']
        item['UserName'] = friend['UserName']

        friends_list.append(item)
        print(item)

    update_tuling_white_list(friends_list)
    save_data(friends_list)
    # download_images(friends_list)

    user = itchat.search_friends(name=u'Douglas.XIE')[0]
    user.send(u'Hello 主人,聊天机器人已经启动')
    itchat.run()
