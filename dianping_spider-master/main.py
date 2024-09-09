# -*- coding:utf-8 -*-

"""
      ┏┛ ┻━━━━━┛ ┻┓
      ┃　　　　　　 ┃
      ┃　　　━　　　┃
      ┃　┳┛　  ┗┳　┃
      ┃　　　　　　 ┃
      ┃　　　┻　　　┃
      ┃　　　　　　 ┃
      ┗━┓　　　┏━━━┛
        ┃　　　┃   神兽保佑
        ┃　　　┃   代码无BUG！
        ┃　　　┗━━━━━━━━━┓
        ┃CREATE BY SNIPER┣┓
        ┃　　　　         ┏┛
        ┗━┓ ┓ ┏━━━┳ ┓ ┏━┛
          ┃ ┫ ┫   ┃ ┫ ┫
          ┗━┻━┛   ┗━┻━┛

"""

import argparse

from function.search import Search
from utils.spider_controller import Controller
from utils.config import global_config
from utils.logger import logger
from utils.spider_config import spider_config
from pymongo import MongoClient

parser = argparse.ArgumentParser()

parser.add_argument('--normal', type=int, required=False, default=1,
                    help='spider as normal(search->detail->review)')
parser.add_argument('--detail', type=int, required=False, default=0,
                    help='spider as custom(just detail)')
parser.add_argument('--review', type=int, required=False, default=0,
                    help='spider as custom(just review)')
parser.add_argument('--shop_id', type=str, required=False, default='',
                    help='custom shop id')
parser.add_argument('--need_more', type=bool, required=False, default=False,
                    help='need detail')
args = parser.parse_args()
if __name__ == '__main__':
    client = MongoClient('mongodb://localhost:27017/')
    db = client['amap_data']  # 数据库名称
    collection = db['arcades']
    # 简单来个查询
    result = collection.find()
    i = 1
    for r in result:
        if i >4:
            print(r['name'])
            controller = Controller(r['name'])
            if args.normal == 1:

                id = controller.main()
                data = {'shop_id': id}
                print(data)
                result = collection.update_one({'name': r['name']}, {'$set': data})  # 61及之前没添加
                print(result)
            if args.detail == 1:
                shop_id = args.shop_id
                logger.info('爬取店铺id：' + shop_id + '详情')
                controller.get_detail(shop_id, detail=args.need_more)
            if args.review == 1:
                shop_id = args.shop_id
                logger.info('爬取店铺id：' + shop_id + '评论')
                # controller.insertid(shop_id, collection)
                controller.get_review(shop_id, detail=args.need_more)
            i += 1
            # shop_id = args.shop_id
            # data = {'shop_id': shop_id}
            # print(data)
            # db.arcades.update({'name': '杰仔电玩咖'}, {'$set': {'shop_id': 'G6josBj9PSnOMeJp'}})
            # result = collection.update_one({'name': r['name']}, {'$set': data})  # 61及之前没添加
            # print(result)
            print(i)
        else:
            i += 1
            print(i)
            continue

