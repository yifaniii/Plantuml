 except:
            # try:
            print('���ӶϿ�')
            try:
                list1.append(message)
                print('��������')
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


#     # ���ӶϿ�
#     # print('CONNECT FAILED')
#     print('��������')
#     errstr = traceback.format_exc()
#     client = OPCUAClient(opcurl)
#     list1.append(message)
#     print(list1)
#
#     # errstr = traceback.format_exc()
#     # time.sleep(3)
#     # recount += 1
#     # print('for' + ' ' + str(recount) + ' ' + 'reconnect')
#     # client = OPCUAClient(opcurl)  # ��ʼ���ͻ���
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
#     raise print('oracle����ʧ��')
#             # else:
#             #     print('����ʧ��')
#         # except:
#         #     print('��������ʧ��')
#
#     # except:
#     #     print("RECONNECT FAILED")
#     #     else:
#     #         print('����')
#     #         break
# except:
#     errstr = traceback.format_exc()
#     print("runerror")
# logger.writeLog("runerror")
# except:
#     errstr = traceback.format_exc()
#     print("read config file error:")
# logger.writeLog("read config file error:")