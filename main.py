import consul
import requests
import time
import json
import schedule

from utils.parser_yaml import YamlParser

parser = YamlParser('./config.yaml')
config: dict = parser.read_yaml()

# Consul API 地址
consul_url = config.get("consul", {}).get("consul_url", "")
consul_port = int(config.get("consul", {}).get("consul_port", ""))
max_notify_number = int(config.get("running", {}).get("maxNotify", ""))
scheduleIntervel = int(config.get("running", {}).get("scheduleIntervel", ""))

# 钉钉机器人 webhook 地址
dingding_url = config.get("notify", {}).get("dingding_url", "")

# 创建 Consul 客户端
client = consul.Consul(host=consul_url, port=consul_port, )
mession_record = {}

def send_message_dingding(message):
    print(message, dingding_url, )
    headers = {"Content-Type": "application/json"}
    response = requests.post(dingding_url, headers=headers, data=json.dumps(message), verify=False)
    if response.status_code == 200:
        print(response.json())
    else:
        print("钉钉消息发送失败！")

def get_service_detail():
    # 获取所有服务
    services = client.agent.services()

    # 提取服务名
    service_list = list(services.keys())
    service_name_list = [ services.get(service_id, {}).get("Service", "") for service_id in service_list ]
    service_name_list = set(service_name_list)
    for service_name in service_name_list:
        yield client.health.service(service_name)[1]

def get_service_list():
    # 检查服务状态并发送钉钉消息
    for Services in get_service_detail():
        for service in Services:
            address = service.get('Service',{}).get('Address','')
            service_status = service["Checks"][1]["Status"]
            service_name   = service.get('Service',{}).get('Service', "")
            service_realname = service.get('Service',{}).get("ID",'')
            if service_status == "passing" and service_realname in mession_record:
                mession_record.pop(service_realname)
                message = {
                    "msgtype": "text",
                    "text": {
                        "content": f"服务恢复感知: {service_name}:{service_realname} 在 {address} 的状态为 {service_status}！"
                    },
                }
                send_message_dingding(message=message)
            if service_status != "passing":
                if service_realname not in mession_record:
                    mession_record[service_realname] = 1
                else:
                    mession_record[service_realname] += 1
                if mession_record[service_realname] > max_notify_number:continue
                message = {
                    "msgtype": "text",
                    "text": {
                        "content": f"服务离线预警: {service_name}:{service_realname} 在 {address} 的状态为 {service_status}！"
                    },
                }
                send_message_dingding(message=message)

schedule.every(scheduleIntervel).minutes.do(get_service_list)

while True:
    schedule.run_pending()
    time.sleep(30)
# get_service_list()