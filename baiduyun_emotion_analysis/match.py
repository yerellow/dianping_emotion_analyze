from pymongo import MongoClient

# 1. 连接MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['add']  # 假设数据库名为 'add'
arcades_collection = db['arcades']  # 需要更新的 'arcades' 集合
review_collection = db['review']  # 包含情感得分的 'review' 集合


# 2. 更新arcades中的average_sentiment_score
def update_arcades_with_sentiment():
    # 只查找arcades中有shop_id的文档
    arcades = arcades_collection.find({"shop_id": {"$exists": True}}, {"shop_id": 1})

    for arcade in arcades:
        shop_id = arcade['shop_id']

        # 在review集合中查找匹配的shop_id
        review = review_collection.find_one({"店铺id": shop_id}, {"average_sentiment_score": 1})

        if review and 'average_sentiment_score' in review:
            average_sentiment_score = review['average_sentiment_score']

            # 更新arcades集合中的average_sentiment_score
            arcades_collection.update_one(
                {"shop_id": shop_id},
                {"$set": {"average_sentiment_score": average_sentiment_score}}
            )
            print(f"已更新 shop_id: {shop_id} 的情感倾向得分为: {average_sentiment_score}")
        else:
            print(f"未找到 shop_id: {shop_id} 对应的情感倾向得分")


if __name__ == '__main__':
    update_arcades_with_sentiment()
