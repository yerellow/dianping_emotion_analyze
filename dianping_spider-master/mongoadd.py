from pymongo import MongoClient

# 连接 MongoDB
client = MongoClient('mongodb://localhost:27017/')

# 选择数据库和集合
db = client['add']  # 替换为实际的数据库名
arcades_collection = db['arcades']
info_collection = db['info']
review_collection = db['review']

# 聚合操作
pipeline = [
    {
        # 将 info 集合中的数据左连接到 arcades 集合
        "$lookup": {
            "from": "info",
            "localField": "shop_id",
            "foreignField": "shop_id",
            "as": "info_data"
        }
    },
    {
        # 将 review 集合中的数据左连接到 arcades 集合
        "$lookup": {
            "from": "review",
            "localField": "shop_id",
            "foreignField": "shop_id",
            "as": "review_data"
        }
    },
    {
        # 解构数组字段 info_data 和 review_data（如果它们是数组）
        "$unwind": {
            "path": "$info_data",
            "preserveNullAndEmptyArrays": True
        }
    },
    {
        "$unwind": {
            "path": "$review_data",
            "preserveNullAndEmptyArrays": True
        }
    },
    {
        # 可以根据需求添加更多的字段或进行计算
        "$addFields": {
            "info_field_example": "$info_data.some_field",  # 假设 info 集合有字段 some_field
            "review_field_example": "$review_data.some_field"  # 假设 review 集合有字段 some_field
        }
    },
    # {
    #     # 过滤、排序或其他进一步的处理
    #     "$project": {
    #         "shop_id": 1,
    #         "name": 1,
    #         "info_field_example": 1,
    #         "review_field_example": 1,
    #         # 选择需要的字段
    #     }
    # }
]

# 执行聚合操作
merged_results = list(arcades_collection.aggregate(pipeline))

# 输出结果或保存到新的集合
for result in merged_results:
    print(result)

# 如果需要将结果保存到新的集合
merged_collection = db['merged_arcades']
merged_collection.insert_many(merged_results)
