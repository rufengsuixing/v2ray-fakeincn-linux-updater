try:
    import requests
except:
    print('pip install requests')
    exit()
import hashlib
import os
import json
import re
from copy import deepcopy
#import time
#请先手动加入一次fakeinchina规则，之后脚本会识别出你添加的位置并更新
tmproot='/root'
config_path='/etc/v2ray/config.json'
restart_v2ray=True
failedlog=True
backup_config=True
a=requests.get('http://opt.cn2qq.com/opt-script/scriptsh.txt')
md5new=re.findall('Sh20_fakeincn=(.*?)\n',a.text)[0]
if os.path.exists(r'Sh20_fakeincn.sh'):
    with open('Sh20_fakeincn.sh',"rb") as fb:
        md5obj=hashlib.md5(fb.read())
        md5old=md5obj.hexdigest()
else:
    md5old=0
if md5new==md5old:
    print('不用')
    with open(tmproot+'/v2raycnupd.log','a') as warnf:
        warnf.write('不用')
    exit(0)
a=requests.get('http://opt.cn2qq.com/opt-script/script/Sh20_fakeincn.sh')
with open(tmproot+"/Sh20_fakeincn.sh", "wb") as fl:
    fl.write(a.content)
domainli=re.findall('ipset=/(.*?)/tocn',a.text)
ipli=re.findall(r'\d{1,3}\.\d{1,3}.\d{1,3}\.\d{1,3}/*\d{0,2}',a.text)
ipli=[i for i in ipli if i!='0.0.0.0']
with open(config_path,"r") as cf:
    configstr=cf.read()
    config=json.loads(configstr)
    configbk=deepcopy(config)
    if backup_config:
        with open(config_path+".backup",'w') as cf2:
            cf2.write(configstr)
for num in range(0,len(config['routing']['settings']['rules'])):
    rule=config['routing']['settings']['rules'][num]
    if 'domain' in rule:
        for dom in rule['domain']:
            if dom in domainli:
                config['routing']['settings']['rules'][num]["domain"]=domainli
                break
    elif 'ip' in rule:
        for ip in rule['ip']:
            if ip in ipli:
                config['routing']['settings']['rules'][num]["ip"]=ipli
                break
with open(tmproot+'/v2rayconfig.tmp','w') as wriin:
    json.dump(config,wriin,indent=2)
if os.path.exists(r'/usr/bin/v2ray/v2ctl'):
    ret=os.system("/usr/bin/v2ray/v2ctl config<"+tmproot+'/v2rayconfig.tmp')
    if ret!=0:
        print('warning 修改失败 未应用修改 配置可见 v2rayconfig.tmp')
        if failedlog:
            with open(tmproot+'/v2raycnupd.log','a') as warnf:
                warnf.write('warning 修改失败 未应用修改 配置可见 v2rayconfig.tmp')
        exit(1)
    else:
        with open(config_path,'w') as wriin:
            json.dump(config,wriin,indent=2)
if restart_v2ray:
    ret=os.system("service v2ray restart")
    if ret!=0:
        print('warning 修改失败 进行回退')
        with open(config_path,'w') as wriin:
            json.dump(configbk,wriin,indent=2)
        os.system("service v2ray restart")
        if failedlog:
            with open(tmproot+'/v2raycnupd.log','a') as warnf:
                warnf.write('warning 修改失败 进行回退 ')
        exit(1)
with open(tmproot+'/v2raycnupd.log','a') as warnf:
    warnf.write('success')
