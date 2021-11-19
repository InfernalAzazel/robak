import asyncio
import os

from robak import EWechat, Jdy, JdySerialize, JdyLog, utils


async def test1():
    async def errFn(e):
        if e is not None:
            print(e)
            return

    appId = ''
    entryId = ''
    api_key = ''
    api = Jdy(appId, entryId, api_key)

    # 获取表单字段
    widgets, err = await api.get_form_widgets()
    print('获取表单字段：')
    print(widgets)

    # 按条件获取表单数据
    data, err = await api.get_form_data('', 100, ['_widget_1528252846720', '_widget_1528252846801'], {
        'rel': 'and',
        'cond': [{
            'field': '_widget_1528252846720',
            'type': 'text',
            'method': 'empty'
        }]
    })
    await errFn(err)
    print('按条件获取表单数据：')
    for v in data:
        print(v)

    # 获取所有表单数据
    form_data, err = await api.get_all_data(
        data_filter={
            "cond": [
                {
                    "field": 'jzdh',
                    "method": "eq",
                    "value": 'GZKK20210800041'  # 来源单号
                }
            ],
        },
        label='测试'
    )
    await errFn(err)
    print('所有表单数据：')
    for v in form_data:
        print(v)

    # 创建单条数据
    create_data, err = await api.create_data(
        data={
            'msg': {
                'value': '123'
            },
        }
    )
    await errFn(err)

    print('创建单条数据：')
    print(create_data)

    # 更新单条数据
    result, err = await api.update_data(
        dataId=create_data['_id'],
        data={
            'msg': {
                'value': '999'
            }
        }
    )
    await errFn(err)

    print('更新单条数据：')
    print(result)

    # 查询单条数据
    retrieve_data, err = await api.retrieve_data(
        dataId=create_data['_id']
    )
    await errFn(err)
    print('查询单条数据：')
    print(retrieve_data)

    # 删除单条数据
    result, err = await api.delete_data(
        dataId=create_data['_id']
    )
    await errFn(err)
    print('删除单条数据：')
    print(result)


async def test2():
    async def errFn(e):
        if e is not None:
            print(e)

    ew = EWechat('', '')
    # res, err = await ew.send_red_pack(
    #     scene_id='PRODUCT_4',
    #     agent_id='',
    #     secret='',
    #     key='',
    #     mch_bill_no=str(int(round(time.time() * 1000))),
    #     mch_id='1267951401',
    #     userid='weisheng',
    #     total_amount='100',
    #     wishing='感谢您参加猜灯谜活动，祝您元宵节快乐！',
    #     act_name='审核奖励发放',
    #     remark='备注 是 猜越多得越多，快来抢！',
    #     cert=('apiclient_cert.pem', 'apiclient_key.pem'),
    #     debug=True,
    # )
    # await errFn(err)
    res, err = await ew.query_red_pack(
        mch_bill_no='',
        mch_id='',
        key='',
        cert=('apiclient_cert.pem', 'apiclient_key.pem'),
        debug=True
    )
    await errFn(err)
    # print(res)
    receiver_id, err = await ew.get_convert_to_userid(openid="otN550VEFctj6uy3NQ2izEit0Do8")
    print(receiver_id)


async def test3():
    data = [{
        '_id': '60bf5e3456262300083b2775',
        '_widget_1623150457454': '启用',
        '_widget_1623150457516': '百事',
        '_widget_1623150457539': '002',
        '_widget_1623150923283': '张三002'
    }]
    data2 = {'dispatch': [{
        '_id': '5e4ba30a87517d0006ba0864',
        'name': '林会',
        'status': 1,
        'username': 'LinHui'
    },
        {
            '_id': '5e4ba30d87517d0006ba0881',
            'name': '张志',
            'status': 1,
            'username': 'ZhangZhi'
        }]
    }

    print(JdySerialize.subform(
        subform_field='test',
        data=data
    ))

    print(JdySerialize.member_array_err_to_none(data2, 'dispatch'))


async def test4():
    print(os.path.dirname(__file__))
    print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 获取项目的根目录
    log = JdyLog(
        app_id='',
        entry_id='',
        api_key='',
        exe_name='robak',
        root_path=os.path.dirname(__file__)  # 获取项目的根目录
    )
    start_time = log.start_time()
    # await log.send(level=log.ERROR, url='http://www.baidu.com', secret='asdas324dsads34ad', err='s啊实打实的', data={
    #     'a': 1,
    #     'b': 'asdsa'
    # })
    # log.print('测试表单', 'ask建档立卡时间', )

    await log.push(
        url='http://127.0.0.1:9999/api/v1/jd/web-hook/test?nonce=2af421&timestamp=1635575734',
        secret='jIYbq5RGrjeA1AsrNGdWfpH0',
        data='{"op": "data_update", "data": {"_id": "617ca8d0bdb142000828cb7f", "appId": "5dde829086f77b0006f3833e", "code": "啊实打实大所", "createTime": "2021-10-30T02:07:12.602Z", "creator": {"_id": "60aee58d252135000741253f", "name": "张畅汇", "status": 1, "username": "18029971256"}, "deleteTime": null, "deleter": null, "entryId": "617ca868d23b3b000779281a", "flowState": 1, "formName": "单元测试", "name": "260阿萨德", "updateTime": "2021-10-30T06:35:33.992Z", "updater": {"_id": "60aee58d252135000741253f", "name": "张畅汇", "status": 1, "username": "18029971256"}}}'
    )
    log.print(name='http://www.baidu.com', info=f'处理耗时{log.elapsed(start_time)}s')


if __name__ == '__main__':
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test4())
