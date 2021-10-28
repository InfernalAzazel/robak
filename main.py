import asyncio
import os

from robak import EWechat, Jdy, JdySerialize, JdyLog


async def test1():
    async def errFn(e):
        if e is not None:
            print(e)

    appId = '5dde829086f77b0006f3833e'
    entryId = '60dd8e24224ed700089fbe49'
    api_key = 'Q20Prk3r78ih4w0ZYOr6iEFfj9g6cEk0'
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

    ew = EWechat('ww9ec26301b4320ef9', 'IAFxK_Qalqg6DHVEXIpXN9_b42wVWBSjcFn9HV-Y1b0')
    # res, err = await ew.send_red_pack(
    #     scene_id='PRODUCT_4',
    #     agent_id='3010046',
    #     secret='Wd_y4mASauhbRMnzNp8HPFnloyKeI-Oo50BQ47Ktpb4',
    #     key='N5N8LzXt4Sp7PkSeQmPBNzHz4aSaf4S1',
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
        mch_bill_no='HBZF125465ASDSAD11',
        mch_id='1267951401',
        key='N5N8LzXt4Sp7PkSeQmPBNzHz4aSaf4S1',
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
        app_id='5dde829086f77b0006f3833e',
        entry_id='617649d05253940008e471d8',
        api_key='Q20Prk3r78ih4w0ZYOr6iEFfj9g6cEk0',
        exe_name='robak',
        root_path=os.path.dirname(__file__)  # 获取项目的根目录
    )
    start_time = log.start_time()
    await log.send(level=log.ERROR, url='http://www.baidu.com', secret='asdas324dsads34ad', err='s啊实打实的', data={
        'a': 1,
        'b': 'asdsa'
    })
    log.print('测试表单', 'ask建档立卡时间', )
    log.print(name='http://www.baidu.com', info=f'处理耗时{log.elapsed(start_time)}s')


if __name__ == '__main__':
    new_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(new_loop)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test4())
