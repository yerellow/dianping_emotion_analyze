import requests
from pymongo import MongoClient
import json

# 高德API Key
def search_nearby(location, keyword):
    api_key = '换成你自己的，可以上咸鱼买'
    radius = 1000
    url = f'https://restapi.amap.com/v3/place/around?key={api_key}&location={location}&keywords={keyword}&radius={radius}&output=JSON'
    response = requests.get(url)
    data = response.json()
    # print(data)
    if data['status'] == '1':
        return data['count']
    else:
        print('周边查询失败:', data['info'])
        return 0


def search():
    api_key = '换成你自己的，可以上咸鱼买'

    # POI类型
    poi_type = '080300'
    # 每页显示条数
    page_size = 50

    # 上海市的区列表
    districts = ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '虹口区', '杨浦区', '闵行区', '宝山区', '嘉定区','浦东新区', '金山区', '松江区', '青浦区', '奉贤区', '崇明区']
    # 遍历各区进行搜索
    for district in districts:
        page_num = 1
        while True:
            # 构造请求URL
            url = f'https://restapi.amap.com/v3/place/text?&keywords=游戏厅&key={api_key}&types={poi_type}&city={district}&offset={page_size}&page={page_num}&extensions=all'

            # 发送请求
            response = requests.get(url)
            data = response.json()

            # 解析返回的JSON数据
            if data['status'] == '1':

                results = data['pois']
                if not results:
                    break
                for result in results:
                    name = result['name']
                    address = result['address']
                    location = result['location']
                    # bus_station_count = search_nearby(location, '公交站')
                    sub_station_count = search_nearby(location, '地铁站')
                    restaurant_count = search_nearby(location, '餐饮')
                    entertainment_count = search_nearby(location, '娱乐')
                    floor = result['indoor_data']['floor']
                    rating = result['biz_ext']['rating']
                    cost = result['biz_ext']['cost']
                    # 组织数据
                    arcade_data = {
                        'district': district,
                        'name': name,
                        'address': address,
                        'location': location,
                        'floor': floor,  # 添加楼层信息
                        'rating': rating,
                        'cost': cost,
                        # 'bus_station_count': bus_station_count,
                        'sub_station_count': sub_station_count,
                        'restaurant_count': restaurant_count,
                        'entertainment_count': entertainment_count
                    }
                    # print(arcade_data)
                    # break

                    # 存储到MongoDB
                    save_to_mongodb(arcade_data)
                    print(f'区: {district}, 名称: {name}, 地址: {address}, 位置: {location}')
                    print(f'周边1公里内地铁站数: {sub_station_count}, 餐饮门店数: {restaurant_count}, 娱乐门店数: {entertainment_count}')

                page_num += 1
                print(data['count'])
                save_sum_mongodb(district, data['count'])
                # break
            else:
                print('查询失败:', data['info'])

        # break

def save_to_mongodb(data):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['amap_data']  # 数据库名称
    collection = db['arcades']  # 集合名称
    try:
        collection.delete_many({'name': data['name'], 'address': data['address']})
        collection.insert_one(data)
        print(f'数据插入成功: {data["name"]}')
    except Exception as e:
        print(f'数据插入失败: {e}')

def save_sum_mongodb(district,data):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['amap_data']  # 数据库名称
    collection = db['sum']  # 集合名称
    try:
        collection.delete_many({'district': district})
        collection.insert_one({'district': district, 'count': data})
        print(f'数据插入成功: {district}')
    except Exception as e:
        print(f'数据插入失败: {e}')

if __name__ == '__main__':
    search()
