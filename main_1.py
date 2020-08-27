# coding:utf-8
import sys

sys.path.insert(0, "..")
import time
from opcua import Client, ua
import queue
import traceback
import json
import yaml
import logger
import datetime
import re
from database_1 import DatabaseAdapter
import random
from tenacity import retry, stop_after_attempt

infoqueue = queue.Queue(0)  # 初始化信息队列


class SubHandler(object):
    """
    订阅处理程序,接收来自服务器的订阅事件从接收线程直接调用data_change和event方法不要在方法写耗时或网络操作
    """

    def datachange_notification(self, node, val, data):
        if val:
            status = False
            print('node:', node)
            print('val:', val)
            print('data---->', data)
            tn = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            infoqueue.put({"name": node, "LASTUPDATEON": tn, "VALUE": val})

            # if str(data).find("StatusCode(Good)") != -1:
            #     status = True
            # if status and val != None:
            #     n = re.findall(';s=([\\s\\S]*?)\\)', str(node))
            #     t = re.findall('SourceTimestamp:([\\s\\S]*?),', str(data))
            #     tn = None
            #     if len(n) > 0 and len(t) > 0:
            #         if '.' in t[0]:
            #             timenow = t[0].split('.')[0]
            #             # print(timenow)
            #             t = datetime.datetime.strptime(timenow, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=8)
            #             tn = t.strftime('%Y-%m-%d %H:%M:%S')
            #         else:
            #             tn = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            #     else:
            #         tn = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            #
            #     station = n[0].split('.')[0]
            #     infoqueue.put({'station': station, 'esn': val, 'plccontrolword': '', 'time': tn})
            # else:
            #     print('StatusCode is not Good-->' + str(node) + '||' + str(val))
            #     # logger.writeLog('StatusCode is not Good-->' + str(node) + '||' + str(val))

    def event_notification(self, event):
        pass


class OPCUAClient:
    """
    定义opcuaclient
    """

    def __init__(self, url, username='', password=''):
        try:
            self.client = Client(url)  # 初始化OPCUA客户端
            if username != '' and password != '':  # 初始化时如果提供用户名密码则配置
                self.client.activate_session("username", "password")  # 配置用户名密码
            self.client.connect()
        except Exception as e:
            print("OPCUAClient INIT ERROR", e)

    def subscribeTag(self, stringNodeID):
        """
        通过StringNodeID订阅Tag
        """
        tag = self.client.get_node(stringNodeID)  # 获取需要读取的节点tag值
        print('tag节点值：', tag)
        handler = SubHandler()
        subobj = self.client.create_subscription(100, handler)  # 返回一个订阅对象第一个参数为发布间隔(毫秒)
        handle = subobj.subscribe_data_change(tag)  # 返回可用于退订的句柄
        return subobj, handle, stringNodeID  # 返回的三个参数可用于取消订阅

    def unsubscribeTag(self, subobj, handle):
        """
        取消订阅
        """
        subobj.unsubscribe(handle)

    def getNodeValue(self, stringNodeID, type=1):
        """
        通过StringNodeID读取节点tag值
        type = 1 获取值
        type = 2 获取DataValue object
        """
        tag = self.client.get_node(stringNodeID)
        return tag.get_value()

    def setNodeValue(self, stringNodeID, value):
        """
        通过StringNodeID设置节点tag值
        """
        tag = self.client.get_node(stringNodeID)
        tag.set_value(value)  # 使用隐含变量类型设置节点值

    def disconnect(self, client):
        """
        断开连接
        """
        return client.disconnect()


if __name__ == "__main__":
    # 读取配置文件
    # try:
    f = open("config.yaml", "r+")
    fstream = f.read()
    configobj = yaml.safe_load(fstream)

    # OPC配置信息
    opcurl = configobj['opc']['server']
    nodePrefix = configobj['opc']['nodePrefix']
    opcstringNodeId = configobj['opc']['stringNodeId']
    # print('---------', opcstringNodeId[0])
    # print('stringNodeId:', opcstringNodeId)
    # print(type(opcstringNodeId))
    # 数据库初始化
    db = DatabaseAdapter()
    db.oraconnect()
    # print('数据库初始化完成')
    list1 = []
    # 重连次数
    recount = 0
    # try:
    opcClient = OPCUAClient(opcurl)  # 初始化客户端
    # logger.writeLog("Start OPCUA Client!")
    # print("Start OPCUA Client!")
    for sid in opcstringNodeId:
        opcClient.subscribeTag(nodePrefix + sid)  # 订阅节点

    # @retry(stop=stop_after_attempt(3))
    # def tenacity_ora():
    #     try:
    #         db.oraconnect()
    #     except:
    #         raise print('oracle连接失败')

    # while True:
    while recount < 4:
        message = {}
        try:
            res = opcClient.getNodeValue(nodePrefix + opcstringNodeId[0])
            if not infoqueue.empty():  # 队列不为空
                message.update(infoqueue.get())
                sqlstr = """
                           insert into CNC (name, LASTUPDATEON, VALUE)
                           values (:name, to_timestamp(:LASTUPDATEON, 'YYYY-MM-DD HH24:MI:SSxFF'), :value)
                           """
                parameters = {'name': str(message['name']),
                              'LASTUPDATEON': message['LASTUPDATEON'],
                              'value': message['VALUE']}
                # print("str", sqlstr)
                # print("para", parameters)
                db.insert(sqlstr, parameters)
        except:
            # try:
            print('连接断开')
            try:
                list1.append(message)
                print('尝试重连')
                # tenacity_ora()
                errstr = traceback.format_exc()
                # client = OPCUAClient(opcurl)
                db.oraconnect()
                recount += 1
                print(list1)
                print('recount====', recount)
                # print("REOPEN OPCUA Client!")
                if db.oraconnect():
                    for dict1 in list1:
                        sqlstr = """insert into CNC (name, LASTUPDATEON, VALUE)
                                                            values (:name, to_timestamp(:LASTUPDATEON, 'YYYY-MM-DD HH24:MI:SSxFF'), :value)
                                                            """
                        parameters = {'name': str(dict1['name']),
                                      'LASTUPDATEON': dict1['LASTUPDATEON'],
                                      'value': dict1['VALUE']}
                        db.insert(sqlstr, parameters)
                    continue
                # else:
                #     print('++++++++++')
            except:
                print('---------filed')
    print('彻底断开连接')


#     # 连接断开
#     # print('CONNECT FAILED')
#     print('尝试重连')
#     errstr = traceback.format_exc()
#     client = OPCUAClient(opcurl)
#     list1.append(message)
#     print(list1)
#
#     # errstr = traceback.format_exc()
#     # time.sleep(3)
#     # recount += 1
#     # print('for' + ' ' + str(recount) + ' ' + 'reconnect')
#     # client = OPCUAClient(opcurl)  # 初始化客户端
#     # list1.append(message)
#     db.oraconnect()
#
#     print("REOPEN OPCUA Client!")
#     # if recount <= 10 and len(list1) <= 10:
#     for dict1 in list1:
#         sqlstr = """insert into CNC (name, LASTUPDATEON, VALUE)
#                                     values (:name, to_timestamp(:LASTUPDATEON, 'YYYY-MM-DD HH24:MI:SSxFF'), :value)
#                                     """
#         parameters = {'name': str(dict1['name']),
#                       'LASTUPDATEON': dict1['LASTUPDATEON'],
#                       'value': dict1['VALUE']}
#         db.insert(sqlstr, parameters)
#     raise print('oracle连接失败')
#             # else:
#             #     print('连接失败')
#         # except:
#         #     print('重连插入失败')
#
#     # except:
#     #     print("RECONNECT FAILED")
#     #     else:
#     #         print('结束')
#     #         break
# except:
#     errstr = traceback.format_exc()
#     print("runerror")
# logger.writeLog("runerror")
# except:
#     errstr = traceback.format_exc()
#     print("read config file error:")
# logger.writeLog("read config file error:")
