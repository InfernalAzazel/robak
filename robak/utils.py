import hashlib
import json
import aiohttp
import requests
import urllib3.contrib.pyopenssl


async def send_jdy_request(method, headers, request_url, data, retry_if_limited):
    """
    发送简道云请求

    :param method: string 请求方法
    :param headers: json 头部
    :param request_url: string 请求地址
    :param data: json 数据
    :param retry_if_limited: string 是否重发
    :return: result, err
    """
    if method == 'GET':
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(request_url, data=json.dumps(data), headers=headers) as response:
                    try:
                        status = response.status
                        result = await response.json(encoding='utf-8')
                    except Exception as e:
                        return {}, e
        except Exception as e:
            return {}, e
    if method == 'POST':
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(request_url, data=json.dumps(data), headers=headers, ) as response:
                    try:
                        status = response.status
                        result = await response.json(encoding='utf-8')
                    except Exception as e:
                        return {}, e
        except Exception as e:
            return {}, e

    if status >= 400:
        if result['code'] == 8303 and retry_if_limited:
            return await send_jdy_request(method, headers, request_url, data, retry_if_limited)
        else:
            return {}, result
    else:
        return result, None


async def send_e_wechat_request(method, request_url, data):
    """
    发送企业微信请求

    :param method: string 请求方法
    :param request_url: string 请求地址
    :param data: json 数据
    :return: result, err
    """
    if method == 'GET':
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(request_url, data=json.dumps(data)) as response:
                    try:
                        result = await response.json(encoding='utf-8')
                    except Exception as e:
                        return {}, e
        except Exception as e:
            return {}, e
    if method == 'POST':
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(request_url, data=json.dumps(data)) as response:
                    try:
                        result = await response.json(encoding='utf-8')
                    except Exception as e:
                        return {}, e
        except Exception as e:
            return {}, e
    return result, None


async def send_e_wechat_xml_request(request_url, data, cert):
    """
    发送企业微信请求

    :param request_url: string 请求地址
    :param data: string xml文本
    :param cert: 证书 cert=('apiclient_cert.pem', 'apiclient_key.pem')
    :return: result, err
    """
    try:
        urllib3.contrib.pyopenssl.inject_into_urllib3()
        res = requests.post(request_url, data=data.encode(encoding='utf-8'),
                            cert=cert)
        result = res.text
    except Exception as e:
        return {}, e
    return result, None


def str_to_md5_utf8_upper(string):
    """
    字符串转 MD5 大写 utf-8

    :param string: 字符串
    :return: string
    """
    m = hashlib.md5()
    m.update(string.encode("utf8"))
    return m.hexdigest().upper()


def str_to_md5_gbk_upper(string):
    """
    字符串转 MD5 大写 utf-8

    :param string: 字符串
    :return: string
    """
    m = hashlib.md5(string.encode(encoding='gb2312'))
    return m.hexdigest().upper()
