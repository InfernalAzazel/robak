import datetime
import json
import time

from loguru import logger

from . import Jdy
from . import utils

"""
    异常处理模块
"""


class JdyLog:

    TRACE = '发现'  # TRACE 在线调试。该级别日志，默认情况下，既不打印到终端也不输出到文件。此时，对程序运行效率几乎不产生影响。
    DEBUG = '调试'  # DEBUG 终端查看、在线调试。该级别日志，默认情况下会打印到终端输出，但是不会归档到日志文件。因此，一般用于开发者在程序当前启动窗口上，查看日志流水信息。
    INFO = '信息'  # INFO 报告程序进度和状态信息。一般这种信息都是一过性的，不会大量反复输出。例如：连接商用库成功后，可以打印一条连库成功的信息，便于跟踪程序进展信息。
    WARNING = '警告'  # WARNING 警告信息程序处理中遇到非法数据或者某种可能的错误。该错误是一过性的、可恢复的，不会影响程序继续运行，程序仍处在正常状态。
    ERROR = '异常'  # ERROR 状态错误该错误发生后程序仍然可以运行，但是极有可能运行在某种非正常的状态下，导致无法完成全部既定的功能。

    def __init__(
            self,
            app_id,
            entry_id,
            api_key,
            exe_name,
            root_path,
            is_create_log=True,
            interval='00:00',
            save_time='30 days'

    ):
        """
       :param app_id: string 应用ID
       :param entry_id: string 表单ID
       :param api_key: string API密钥
       :param exe_name: string 项目名称
       :param is_create_log: bool 是否创建本地日志记录 默认 true
       :param interval: string 间隔时间 默认 00:00
       :param save_time: string 保存时间 默认 30 天
       """
        self.__exe_name = exe_name
        self.is_create_log = is_create_log
        self.__jdy = Jdy(app_id=app_id, entry_id=entry_id, api_key=api_key)

        if self.is_create_log:
            p_path = utils.ProjectPath(root_path=root_path)
            logger.add(
                sink=p_path.filename,
                rotation=interval,  # 设置时间点创建一个日志文件
                retention=save_time,  # 配置日志文件最长保留时间
                encoding='utf-8'
            )

    async def send(
            self,
            level,
            url,
            secret,
            err,
            data,
            is_start_workflow=False,
            is_start_trigger=False
    ):
        """

        发送日志

        :param level: string 日志级别
        :param url: sting 接口地址
        :param secret: string 密钥
        :param err: string 异常信息
        :param data: json 数据
        :param is_start_workflow: bool 是否激活流程 默认 false
        :param is_start_trigger: bool  是否激活流程 默认 false
        :return: result,err
        """
        d = ''

        if level == JdyLog.TRACE:
            logger.trace(err)
        elif level == JdyLog.DEBUG:
            logger.debug(err)
        elif level == JdyLog.INFO:
            logger.info(err)
        elif level == JdyLog.WARNING:
            logger.warning(err)
        else:
            logger.error(f'| {self.ERROR}  | {self.__exe_name} |   {url}    |   {secret}   |    is_start_workflow:{is_start_workflow}   |   is_start_trigger:{is_start_trigger}     |   {data}  | ---> {err}')

        current_time = (datetime.datetime.now() - datetime.timedelta(hours=8)).strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        try:
            d = json.dumps(data)
        except:
            logger.error(f'| {self.ERROR}  | {self.__exe_name} |   日志异常    | --->   {err}')

        _, err = await self.__jdy.create_data(
            data={
                'err_time': {'value': current_time},
                'level': {'value': level},
                'url': {'value': url},
                'secret': {'value': secret},
                'is_handle': {'value': '否'},
                'err': {'value': err},
                'data': {'value': d},
            },
            is_start_workflow=is_start_workflow,
            is_start_trigger=is_start_trigger
        )
        if err is not None:
            logger.error(f'| {self.ERROR}  | {self.__exe_name} |   日志异常    | --->   {err}')

    def print(self, name, info):
        """
        打印信息到终端

        :param name: string 名称
        :param info: string 信息
        """
        logger.info(f'| {self.INFO}  | {self.__exe_name} |   {name}    | --->   {info}')

    @staticmethod
    def start_time():
        """
        获取当前程序运行时间
        """
        return time.perf_counter()  # 启动时间

    @staticmethod
    def elapsed(start_time):
        """
        获取程序总耗时

        :param start_time: time 当前程序运行时间
        :return:
        """
        return time.perf_counter() - start_time  # 结束时间
