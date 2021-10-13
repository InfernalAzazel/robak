import random
import string

from . import utils


class EWechat:

    def __init__(self, corp_id, corp_secret):

        self.__corp_id = corp_id
        self.__corp_secret = corp_secret
        self.__url_gettoken = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={corp_secret}'
        self.__url_convert_to_openid = 'https://qyapi.weixin.qq.com/cgi-bin/user/convert_to_openid?'
        self.__url_convert_to_userid = 'https://qyapi.weixin.qq.com/cgi-bin/user/convert_to_userid?'
        self.__url_send_work_wx_red_pack = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/sendworkwxredpack'
        self.__url_query_work_wx_red_pack = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/queryworkwxredpack'

    # 获取 token
    async def get_token(self):
        """
        获取 token 认证

        :return: res, err
        """
        res, err = await utils.send_e_wechat_request('GET', self.__url_gettoken, data={})

        if err is not None:
            return {}, err
        if res['errcode'] != 0:
            return {}, res
        return res['access_token'], None

    # 成员 userid 转换 openid
    async def get_convert_to_openid(self, userid):
        """
        成员 userid 转换 openid

        :param userid: 成员id
        :return: openid, err
        """
        token, err, = await self.get_token()
        if err is not None:
            return {}, err
        res, err = await utils.send_e_wechat_request(
            'POST', self.__url_convert_to_openid + f'access_token={token}',
            data={
                'userid': userid
            }
        )
        if err is not None:
            return {}, err
        if res['errcode'] != 0:
            return {}, res
        return res['openid'], None

    # openid 转 userid
    async def get_convert_to_userid(self, openid):

        """
        成员 openid 转换 userid

        :param openid: 成员id
        :return: userid, err
        """
        token, err = await self.get_token()

        if err is not None:
            return {}, err
        res, err = await utils.send_e_wechat_request(
            'POST',
            self.__url_convert_to_userid + f'access_token={token}',
            data={
                'openid': openid
            }
        )
        if err is not None:
            return {}, err
        if res['errcode'] != 0:
            return {}, res
        return res['userid'], None

    # 发放企业红包
    async def send_red_pack(
            self,
            scene_id,
            agent_id,
            secret,
            key,
            mch_bill_no,
            mch_id,
            userid,
            total_amount,
            wishing,
            act_name,
            remark,
            cert=('apiclient_cert.pem', 'apiclient_key.pem'),
            debug=False):
        """
        发放企业红包

        - 场景参数

            PRODUCT_1:  商品促销
            PRODUCT_2:  抽奖
            PRODUCT_3:  虚拟物品兑奖
            PRODUCT_4:  企业内部福利
            PRODUCT_5:  渠道分润
            PRODUCT_6:  保险回馈
            PRODUCT_7:  彩票派奖
            PRODUCT_8:  税务刮奖

        :param scene_id: 场景
        :param key: 微信支付 key 秘钥
        :param agent_id: 企业微信支付应用 ID 值
        :param secret:  企业微信支付应用 secret 值
        :param mch_bill_no:  商户订单号   是   123456  String(28)  商户订单号（每个订单号必须唯一。取值范围：0~9，a~z，A~Z）.接口根据商户订单号支持重入，如出现超时可再调用。组成参考：mch_id+yyyymmdd+10位一天内不能重复的数字
        :param mch_id:  商户号 是   10000098    String(32)  微信支付分配的商户号
        :param userid:   成员 userid    是    2605541
        :param total_amount:    金额  是   1000    int 金额，单位分，单笔最小金额默认为1元
        :param wishing: 红包祝福语	是   感谢您参加猜灯谜活动，祝您元宵节快乐！ String(128) 红包祝福语
        :param act_name:    项目名称    是   猜灯谜抢红包活动    String(32)  项目名称
        :param remark:  备注  是   猜越多得越多，快来抢！ String(256) 备注信息
        :param debug: 打印发送与接收信息 默认 false
        :param cert: API 证书 ('apiclient_cert.pem', 'apiclient_key.pem')
        :return: xml, err
        """
        re_openid, err = await self.get_convert_to_openid(userid)
        if err is not None:
            return {}, err

        nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 32)).upper()  # 随机32位字符串
        wxappid = self.__corp_id
        stringA = f'act_name={act_name}&mch_billno={mch_bill_no}&mch_id={mch_id}&nonce_str={nonce_str}&re_openid={re_openid}&total_amount={total_amount}&wxappid={wxappid}'
        stringSignTemp = f'{stringA}&secret={secret}'
        workwx_sign = utils.str_to_md5_utf8_upper(stringSignTemp)  # 企业微信签名算法
        if debug:
            print('企业微信签名算法', stringSignTemp)
            print('企业微信签名算法MD5加密', workwx_sign)

        stringA = f'act_name={act_name}' \
                  f'&agentid={agent_id}' \
                  f'&mch_billno={mch_bill_no}' \
                  f'&mch_id={mch_id}' \
                  f'&nonce_str={nonce_str}' \
                  f'&re_openid={re_openid}' \
                  f'&remark={remark}' \
                  f'&scene_id={scene_id}' \
                  f'&total_amount={total_amount}' \
                  f'&wishing={wishing}' \
                  f'&workwx_sign={workwx_sign}' \
                  f'&wxappid={wxappid}'
        stringSignTemp = f'{stringA}&key={key}'
        sign = utils.str_to_md5_utf8_upper(stringSignTemp)  # 微信支付签名算法 需要所有字段除 sign 外
        if debug:
            print('微信支付签名算法', stringSignTemp)
            print('微信支付签名算法MD5加密', sign)

        xml = f"""
          <xml>
                <nonce_str>{nonce_str}</nonce_str>
                <sign>{sign}</sign>
                <mch_billno>{mch_bill_no}</mch_billno>
                <mch_id>{mch_id}</mch_id>
                <wxappid>{wxappid}</wxappid>
                <agentid>{agent_id}</agentid>
                <re_openid>{re_openid}</re_openid>
                <scene_id>{scene_id}</scene_id>
                <total_amount>{total_amount}</total_amount> 
                <wishing>{wishing}</wishing>
                <act_name>{act_name}</act_name>
                <remark>{remark}</remark>
                <workwx_sign>{workwx_sign}</workwx_sign>
            </xml>
        """

        res, err = await utils.send_e_wechat_xml_request(self.__url_send_work_wx_red_pack, data=xml, cert=cert)
        if err is not None:
            return {}, err
        if debug:
            print(xml)
            print(res)
        return res, None

    # 查询红包记录
    async def query_red_pack(
            self,
            mch_bill_no,
            mch_id, key,
            cert=('apiclient_cert.pem', 'apiclient_key.pem'),
            debug=False):
        """
        查询红包记录

        :param mch_bill_no: 商户订单号
        :param mch_id: 商户号
        :param key: 微信支付 key 秘钥
        :param cert: API 证书 ('apiclient_cert.pem', 'apiclient_key.pem')
        :param debug: bool 输出调试记录 默认 False
        :return: xml, err
        """
        nonce_str = ''.join(random.sample(string.ascii_letters + string.digits, 32)).upper()  # 随机32位字符串
        appid = self.__corp_id
        stringA = f'appid={appid}' \
                  f'&mch_billno={mch_bill_no}' \
                  f'&mch_id={mch_id}' \
                  f'&nonce_str={nonce_str}'

        stringSignTemp = f'{stringA}&key={key}'
        sign = utils.str_to_md5_utf8_upper(stringSignTemp)  # 微信支付签名算法 需要所有字段除 sign 外
        if debug:
            print('微信支付签名算法', stringSignTemp)
            print('微信支付签名算法MD5加密', sign)
        xml = f"""
          <xml>
          <nonce_str>{nonce_str}</nonce_str>
          <sign>{sign}</sign>
          <mch_billno>{mch_bill_no}</mch_billno>
          <mch_id>{mch_id}</mch_id>
          <appid>{appid}</appid>
          </xml>
        """
        res, err = await utils.send_e_wechat_xml_request(self.__url_query_work_wx_red_pack, data=xml, cert=cert)
        if err is not None:
            return {}, err
        if debug:
            print(xml)
            print(res)
        return res, None
