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
from tqdm import tqdm

from function.search import Search
from function.detail import Detail
from function.review import Review
from function.get_encryption_requests import *
from utils.saver.saver import saver
from utils.spider_config import spider_config


class Controller():
    """
    整个程序的控制器
    用来进行爬取策略选择以及数据汇总存储
    """

    def __init__(self, arcade_names):
        self.s = Search()
        self.d = Detail()
        self.r = Review()
        self.arcade_names = arcade_names

        # 初始化基础URL
        if spider_config.SEARCH_URL == '':
            keyword = self.arcade_names
            channel_id = spider_config.CHANNEL_ID
            city_id = spider_config.LOCATION_ID
            self.base_url = 'http://www.dianping.com/search/keyword/' + str(city_id) + '/' + str(
                channel_id) + '_' + str(keyword) + '/p'
            pass
        else:
            # 末尾加一个任意字符，为了适配两种初始化url切割长度
            self.base_url = spider_config.SEARCH_URL + '1'

    def main(self):
        """
        调度
        @return:
        """
        # Todo  其实这里挺犹豫是爬取完搜索直接详情还是爬一段详情一段
        #       本着稀释同类型访问频率的原则，暂时采用爬一段详情一段
        # 调用搜索
        for page in tqdm(range(1, spider_config.NEED_SEARCH_PAGES + 1), desc='搜索页数'):
            # 拼凑url
            search_url, request_type = self.get_search_url(page)
            """
            {
                '店铺id': -,
                '店铺名': -,
                '评论总数': -,
                '人均价格': -,
                '标签1': -,
                '标签2': -,
                '店铺地址': -,
                '详情链接': -,
                '图片链接': -,
                '店铺均分': -,
                '推荐菜': -,
                '店铺总分': -,
            }
            """
            search_res = self.s.search(search_url, request_type)
            # search方法如果返回None，代表页面已经没有数据了
            if not search_res:
                break

            if spider_config.NEED_DETAIL is False and spider_config.NEED_REVIEW is False:
                for each_search_res in search_res:
                    each_search_res.update({
                        '店铺电话': '-',
                        '其他信息': '-',
                        '优惠券信息': '-',
                    })
                    self.saver(each_search_res, {})
                continue
            for each_search_res in tqdm(search_res, desc='详细爬取'):
                each_detail_res = {}
                each_review_res = {}
                # 爬取详情
                if spider_config.NEED_DETAIL:
                    shop_id = each_search_res['店铺id']
                    if spider_config.NEED_PHONE_DETAIL:
                        """
                        {
                            '店铺id': -,
                            '店铺名': -,
                            '评论总数': -,
                            '人均价格': -,
                            '店铺地址': -,
                            '店铺电话': -,
                            '其他信息': -
                        }
                        """
                        each_detail_res = self.d.get_detail(shop_id)
                        # 多版本爬取格式适配
                        each_detail_res.update({
                            '店铺总分': '-',
                            '店铺均分': '-',
                            '优惠券信息': '-',
                        })
                    else:
                        """
                        {
                            '店铺id': -,
                            '店铺名': -,
                            '店铺地址': -,
                            '店铺电话': -,
                            '店铺总分': -,
                            '店铺均分': -,
                            '人均价格': -,
                            '评论总数': -,
                        }
                        """
                        hidden_info = get_basic_hidden_info(shop_id)
                        review_and_star = get_review_and_star(shop_id)
                        each_detail_res.update(hidden_info)
                        each_detail_res.update(review_and_star)
                        # 多版本爬取格式适配
                        each_detail_res.update({
                            '其他信息': '-',
                            '优惠券信息': '-'
                        })
                    # 爬取经纬度
                    if spider_config.NEED_LOCATION:
                        """
                        {
                            '店铺id': -,
                            '店铺名': -,
                            '店铺纬度': -,
                            '店铺经度': -,
                        }
                        """
                        shop_id = each_search_res['店铺id']
                        lat_and_lng = get_lat_and_lng(shop_id)
                        each_detail_res.update(lat_and_lng)
                    else:
                        each_detail_res.update({
                            '店铺纬度': '-',
                            '店铺经度': '-'
                        })



                    # 全局整合，将详情以及评论的相关信息拼接到search_res中。
                    each_search_res['店铺地址'] = each_detail_res['店铺地址']
                    each_search_res['店铺电话'] = each_detail_res['店铺电话']
                    each_search_res['店铺总分'] = each_detail_res['店铺总分']
                    if each_search_res['店铺均分'] == '-':
                        each_search_res['店铺均分'] = each_detail_res['店铺均分']
                    each_search_res['人均价格'] = each_detail_res['人均价格']
                    each_search_res['评论总数'] = each_detail_res['评论总数']
                    each_search_res['其他信息'] = each_detail_res['其他信息']
                    each_search_res['优惠券信息'] = each_detail_res['优惠券信息']
                    each_search_res['店铺纬度'] = each_detail_res['店铺纬度']
                    each_search_res['店铺经度'] = each_detail_res['店铺经度']
                # 爬取评论
                if spider_config.NEED_REVIEW:
                    shop_id = each_search_res['店铺id']
                    if spider_config.NEED_REVIEW_DETAIL:
                        """
                        {
                            '店铺id': -,
                            '评论摘要': -,
                            '评论总数': -,
                            '好评个数': -,
                            '中评个数': -,
                            '差评个数': -,
                            '带图评论个数': -,
                            '精选评论': -,
                        }
                        """
                        each_review_res = self.r.get_review(shop_id)
                        each_review_res.update({'推荐菜': '-'})
                    else:
                        """
                        {
                            '店铺id': -,
                            '评论摘要': -,
                            '评论总数': -,
                            '好评个数': -,
                            '中评个数': -,
                            '差评个数': -,
                            '带图评论个数': -,
                            '精选评论': -,
                            '推荐菜': -,
                        }
                        """
                        each_review_res = get_basic_review(shop_id)

                        # 全局整合，将详情以及评论的相关信息拼接到search_res中。
                        each_search_res['推荐菜'] = each_review_res['推荐菜']
                        # 对于已经给到search_res中的信息，删除
                        each_review_res.pop('推荐菜')
                    data = shop_id




                self.saver(each_search_res, each_review_res)
            # 如果这一页数据小于15，代表下一页已经没有数据了，直接退出
            if len(search_res) < 15:
                return shop_id
                break


    def get_review(self, shop_id, detail=False):
        if detail:
            each_review_res = self.r.get_review(shop_id)
        else:
            each_review_res = get_basic_review(shop_id)
        saver.save_data(each_review_res, 'review')

    def get_detail(self, shop_id, detail=False):
        each_detail_res = {}
        if detail:
            """
            '店铺id': -,
            '店铺名': -,
            '评论总数': -,
            '人均价格': -,
            '店铺地址': -,
            '店铺电话': -,
            '其他信息': -,
            '店铺总分': '-',
            '店铺均分': '-',
            """
            each_detail_res = self.d.get_detail(shop_id)
            # 多版本爬取格式适配
            each_detail_res.update({
                '店铺总分': '-',
                '店铺均分': '-',
            })
        else:
            """
            '店铺id': -,
            '店铺总分': -,
            '店铺均分': -,
            '人均价格': -,
            '评论总数': -,
            '店铺名': -,
            '店铺地址': -,
            '店铺电话': -，
            '其他信息': -,
            """
            hidden_info = get_basic_hidden_info(shop_id)
            review_and_star = get_review_and_star(shop_id)
            each_detail_res.update(hidden_info)
            each_detail_res.update(review_and_star)
            # 多版本爬取格式适配
            each_detail_res.update({
                '其他信息': '-'
            })
        # 获取经纬度
        if spider_config.NEED_LAT_AND_LNG:
            lat_and_lng = get_lat_and_lng(shop_id)
            each_detail_res.update(lat_and_lng)
        saver.save_data(each_detail_res, 'detail')

    def get_search_url(self, cur_page):
        """
        获取搜索链接
        @param cur_page:
        @return:
        """
        if cur_page == 1:
            # return self.base_url[:-2], 'no proxy, no cookie'
            return self.base_url[:-2], 'proxy, cookie'
        else:
            if self.base_url.endswith('p'):
                return self.base_url + str(cur_page), 'proxy, cookie'
            else:
                return self.base_url[:-1] + str(cur_page), 'proxy, cookie'

    def saver(self, each_search_res, each_review_res):
        # save search
        saver.save_data(each_search_res, 'search')
        # save detail
        # if spider_config.NEED_DETAIL:
        #     saver.save_data(each_detail_res, 'detail')

        # save review
        if spider_config.NEED_REVIEW:
            saver.save_data(each_review_res, 'review')


# controller = Controller()
