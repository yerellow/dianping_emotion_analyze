from pymongo import MongoClient

# 1. 连接MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['add']  # 假设数据库名为 'add'
arcades_collection = db['arcades']  # 需要更新的 'arcades' 集合
review_collection = db['info']  # 包含情感得分的 'review' 集合


# 2. 更新arcades中的人均价格
def update_arcades_with_sentiment():
    # 只查找arcades中有shop_id的文档
    arcades = arcades_collection.find({"shop_id": {"$exists": True}}, {"shop_id": 1})

    for arcade in arcades:
        shop_id = arcade['shop_id']

        # 在review集合中查找匹配的shop_id
        review = review_collection.find_one({"店铺id": shop_id}, {"人均价格": 1})

        if review and '人均价格' in review:
            人均价格 = review['人均价格']

            # 更新arcades集合中的人均价格
            arcades_collection.update_one(
                {"shop_id": shop_id},
                {"$set": {"人均价格": 人均价格}}
            )
            print(f"已更新 shop_id: {shop_id} 的人均价格为: {人均价格}")
        else:
            print(f"未找到 shop_id: {shop_id} 对应的人均价格")


if __name__ == '__main__':
    update_arcades_with_sentiment()
