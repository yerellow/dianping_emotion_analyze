import requests
import json
from pymongo import MongoClient
import time

API_KEY = "改成你自己"
SECRET_KEY = "改成你自己"


# 1. 获取百度AI情感分析的Access Token
def get_access_token():
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    response = requests.post(url, params=params).json()
    return response.get("access_token")


# 2. 调用百度AI情感分析接口
def analyze_sentiment(text, access_token):
    url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/sentiment_classify?charset=UTF-8&access_token=" + access_token
    payload = json.dumps({"text": text})
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=payload)

    result = response.json()
    # print(result)

    if 'items' in result:
        positive_prob = result['items'][0]['positive_prob']
        negative_prob = result['items'][0]['negative_prob']
        # 计算积极情感概率减去消极情感概率
        sentiment_score = positive_prob - negative_prob
        return sentiment_score
    return None


# 3. 将情感分析结果存储到MongoDB
def update_shop_average_sentiment(shop_id, avg_score):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['add']  # 数据库名称
    collection = db['review']  # 集合名称
    try:
        # 更新MongoDB中的店铺平均情感得分
        collection.update_one(
            {"店铺id": shop_id},
            {"$set": {"average_sentiment_score": avg_score}}
        )
        print(f"店铺ID: {shop_id}, 平均情感得分: {avg_score} 已更新")
    except Exception as e:
        print(f'更新失败: {e}')


# 4. 批量处理评论并计算每个店铺的平均情感得分
def process_reviews():
    # 连接MongoDB
    client = MongoClient('mongodb://localhost:27017/')
    db = client['add']
    collection = db['review']

    access_token = get_access_token()  # 获取百度AI的Access Token

    # 存储每个店铺的情感得分列表
    shop_scores = {}

    # 遍历所有评论
    reviews = collection.find({}, {"店铺id": 1, "精选评论": 1})
    j = 0
    for review in reviews:
        if j < 101:
            j += 1
            print(j)

        else:
            j += 1
            print(j)
            shop_id = review['店铺id']
            comments = review.get('精选评论', [])
            if comments == 'ban':
                print(f"店铺{shop_id}被ban")
                continue
            sentiment_scores = []
            i = 1
            # 遍历每个评论
            for comment in comments:
                # print(comments)
                # 调用情感分析API获取情感得分
                sentiment_score = analyze_sentiment(comment['评论内容'], access_token)
                print(f"{j}店铺{shop_id}第{i}条评论共{len(comments)}条得分为: {sentiment_score}")
                i += 1
                if sentiment_score is not None:
                    sentiment_scores.append(sentiment_score)
                time.sleep(0.4)

            # 如果有情感得分，计算平均值并更新
            if sentiment_scores:
                avg_score = sum(sentiment_scores) / len(sentiment_scores)
                update_shop_average_sentiment(shop_id, avg_score)



if __name__ == '__main__':
    process_reviews()
