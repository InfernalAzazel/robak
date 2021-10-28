import hashlib
from typing import List
from loguru import logger
from . import utils


class Jdy:

    def __init__(self, app_id, entry_id, api_key, retry_if_limited=True):
        """
        简道云支持库

        :param app_id: 应用ID
        :param entry_id: 表单ID
        :param api_key: 简道云API秘钥
        :param retry_if_limited: 当接口被限制后是否重发 默认 True
        """
        self.__url_get_widgets = 'https://api.jiandaoyun.com/api/v1/app/' + app_id + '/entry/' + entry_id + '/widgets'
        self.__url_get_data = 'https://api.jiandaoyun.com/api/v2/app/' + app_id + '/entry/' + entry_id + '/data'
        self.__url_retrieve_data = 'https://api.jiandaoyun.com/api/v2/app/' + app_id + '/entry/' + entry_id + '/data_retrieve'
        self.__url_update_data = 'https://api.jiandaoyun.com/api/v3/app/' + app_id + '/entry/' + entry_id + '/data_update'
        self.__url_create_data = 'https://api.jiandaoyun.com/api/v3/app/' + app_id + '/entry/' + entry_id + '/data_create'
        self.__url_delete_data = 'https://api.jiandaoyun.com/api/v1/app/' + app_id + '/entry/' + entry_id + '/data_delete'
        self.__url_approval_comments = 'https://api.jiandaoyun.com/api/v1/app/' + app_id + '/entry/' + entry_id + '/data'
        self.__api_key = api_key
        self.__retry_if_limited = retry_if_limited

    # 带有认证信息的请求头
    def __get_req_header(self):
        return {
            'Authorization': 'Bearer ' + self.__api_key,
            'Content-Type': 'application/json;charset=utf-8'
        }

    # 签名
    @staticmethod
    def get_signature(nonce, secret, payload, timestamp):
        """
        解码签名-简道云 WEBHook

        :param nonce:
        :param secret:
        :param payload:
        :param timestamp:
        :return: result String
        """
        content = ':'.join([nonce, payload, secret, timestamp]).encode('utf-8')
        m = hashlib.sha1()
        m.update(content)
        return m.hexdigest()

    # 自动实例化 简道云API对象
    @staticmethod
    def auto_init(app_id_list: List[str], entry_id_list: List[str], api_key: str, retry_if_limited=True):
        """
        自动实例化 简道云API对象

        :param app_id_list: Array
        :param entry_id_list: Array
        :param api_key: Str
        :param retry_if_limited: 当接口被限制后是否重发 默认 True
        :return: Array
        """
        result = []
        if len(app_id_list) != len(entry_id_list):
            return
        for i in range(len(app_id_list)):
            result.append(
                Jdy(app_id=app_id_list[i], entry_id=entry_id_list[i], api_key=api_key,
                    retry_if_limited=retry_if_limited))
        return result

    # 获取表单字段
    async def get_form_widgets(self):
        """
               获取表单字段

               返回 widgets


               widgets[].items	仅子表单控件有；数组里包含了每个子控件的信息

               widgets[].label	控件标题

               widgets[].name	字段名（设置了字段别名则采用别名，未设置则采用控件ID）

               widgets[].type	控件类型；每种控件类型都有对应的数据类型

               :return: result, err

        """
        result, err = await utils.send_jdy_request(
            'POST', self.__get_req_header(),
            self.__url_get_widgets, {},
            self.__retry_if_limited
        )
        if err is not None:
            return {}, err
        return result['widgets'], None

    # 根据条件获取表单中的数据
    async def get_form_data(self, dataId='', limit=10, fields=None, data_filter=None):
        """
        查询表单多条数据

        可以不带参，默认查询 10条

        :param dataId:      String	上一次查询数据结果的最后一条数据的ID，没有则留空
        :param fields:      Array   数据筛选器
        :param data_filter: JSON	需要查询的数据字段
        :param limit:       Number	查询的数据条数，1~100，默认10
        :return: result, err
        """

        if data_filter is None:
            data_filter = {}
        if fields is None:
            fields = []

        result, err = await utils.send_jdy_request(
            'POST',
            self.__get_req_header(),
            self.__url_get_data,
            {
                'data_id': dataId,
                'limit': limit,
                'fields': fields,
                'filter': data_filter
            },
            self.__retry_if_limited
        )
        if err is not None:
            return {}, err
        return result['data'], None

    # 获取表单中满足条件的所有数据
    async def get_all_data(self, fields=None, data_filter=None, label=''):
        """
        查询表单中满足条件的所有数据

        :param fields:          Array   需要查询的数据字段
        :param data_filter:     JSON	数据筛选器
        :param label:           String
        :return: result, err
        """

        if data_filter is None:
            data_filter = {}
        if fields is None:
            fields = []

        form_data = []

        # 递归取下一页数据
        async def get_next_page(dataId):
            data, err = await self.get_form_data(dataId, 100, fields, data_filter)
            if err is not None:
                return {}, err
            if data:
                for v in data:
                    form_data.append(v)
                if label != '':
                    logger.info(f'[{label}] 读取累计 {len(form_data)} 数量 ..')
                dataId = data[len(data) - 1]['_id']
                await get_next_page(dataId)

        await get_next_page('')
        return form_data, None

    # 检索一条数据
    async def retrieve_data(self, dataId):
        """
        检索一条数据

        :param dataId: string
        :return: result, err
        """
        result, err = await utils.send_jdy_request(
            'POST',
            self.__get_req_header(),
            self.__url_retrieve_data,
            {
                'data_id': dataId
            },
            self.__retry_if_limited
        )
        if err is not None:
            return {}, err
        return result['data'], err

    # 创建一条数据
    async def create_data(self, data, is_start_workflow=False, is_start_trigger=False):
        """
        创建一条数据

        :param data:                JSON   数据内容
        :param is_start_workflow:   Bool	是否发起流程（仅流程表单有效）	false
        :param is_start_trigger:    Bool	是否触发智能助手	false
        :return: result, err
        """
        result, err = await utils.send_jdy_request(
            'POST',
            self.__get_req_header(),
            self.__url_create_data,
            {
                'data': data,
                'is_start_workflow': is_start_workflow,
                'is_start_trigger': is_start_trigger
            },
            self.__retry_if_limited
        )
        if err is not None:
            return {}, err
        return result['data'], err

    # 更新数据
    async def update_data(self, dataId, data, is_start_trigger=False):
        """
         更新数据

         :param dataId:              String	数据ID
         :param data:                JSON	数据内容，其他同新建单条数据接口，子表单需要注明子表单数据ID
         :param is_start_trigger:    Bool	是否触发智能助手  false
         :return: result, err
         """
        result, err = await utils.send_jdy_request(
            'POST',
            self.__get_req_header(),
            self.__url_update_data,
            {
                'data_id': dataId,
                'data': data,
                'is_start_trigger': is_start_trigger,
            },
            self.__retry_if_limited
        )
        if err is not None:
            return {}, err
        return result['data'], err

    # 删除数据
    async def delete_data(self, dataId, is_start_trigger=False):
        """
        删除数据

        :param dataId:              String	数据ID
        :param is_start_trigger:	Bool	是否触发智能助手	false
        :return: result, err
       """
        result, err = await utils.send_jdy_request(
            'POST',
            self.__get_req_header(),
            self.__url_delete_data,
            {
                'data_id': dataId,
                'is_start_trigger': is_start_trigger,
            },
            self.__retry_if_limited
        )
        if err is not None:
            return {}, err
        return result, err

    # 查询并更新一条
    async def query_update_data_one(self, data, data_filter=None, non_existent_create=False, is_start_workflow=False,
                                    is_start_trigger=False):
        """
        查询并更新一条

        创建数据支持 发起流程 触发智能助手

        更新数据支持 触发智能助手

        :param data: JSON 数据
        :param data_filter: Array 数据筛选器
        :param non_existent_create: Bool 如果不存在则创建 false
        :param is_start_workflow: Bool 是否发起流程（仅流程表单有效） false
        :param is_start_trigger: Bool 是否触发智能助手 false
        :return: result, err
        """

        if data_filter is None:
            data_filter = {}

        result, err = await self.get_form_data(data_filter=data_filter)
        if err is not None:
            return {}, err
        if not result:
            if non_existent_create:
                result, err = await self.create_data(
                    data=data,
                    is_start_workflow=is_start_workflow,
                    is_start_trigger=is_start_trigger
                )
                if err is not None:
                    return {}, err
                return result, None
        else:
            result, err = await self.update_data(dataId=result[0]['_id'], data=data, is_start_trigger=is_start_trigger)
            if err is not None:
                return {}, err
            return result, None

    # 查询并删除一条
    async def query_delete_one(self, data_filter=None):
        """
        查询并删除一条

        :param data_filter: Array 数据筛选器
        :return: result, err
        """
        if data_filter is None:
            data_filter = {}

        result, err = await self.get_form_data(data_filter=data_filter)
        if err is not None:
            return {}, err
        if result:
            result, err = await self.delete_data(dataId=result[0]['_id'])
            if err is not None:
                return {}, err
        return result, None

    # 流程接口 ----------------------------------------------------------------------------------------------------------

    # 获取单条表单流程数据的审批意见
    async def get_approval_comments(self, data_id, skip=0):
        """
        获取单条表单流程数据的审批意见

        :param data_id: string 数据ID
        :param skip: int 跳过审批意见条数
        :return: result, err
        """
        result, err = await utils.send_jdy_request(
            'POST',
            self.__get_req_header(),
            self.__url_approval_comments + f'/{data_id}/approval_comments',
            {
                'skip': skip
            },
            self.__retry_if_limited
        )
        if err is not None:
            return {}, err
        return result['approveCommentList'], None
