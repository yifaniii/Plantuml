 except:
            # try:
            print('连接断开')
            try:
                list1.append(message)
                print('尝试重连')
                tenacity_ora()
                errstr = traceback.format_exc()
                client = OPCUAClient(opcurl)
                print(list1)
                # print("REOPEN OPCUA Client!")
                for dict1 in list1:
                    sqlstr = """insert into CNC (name, LASTUPDATEON, VALUE)
                                                        values (:name, to_timestamp(:LASTUPDATEON, 'YYYY-MM-DD HH24:MI:SSxFF'), :value)
                                                        """
                    parameters = {'name': str(dict1['name']),
                                  'LASTUPDATEON': dict1['LASTUPDATEON'],
                                  'value': dict1['VALUE']}
                    db.insert(sqlstr, parameters)
            except:
                print('********filed')
                break


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