#-*- coding: utf-8 -*-
__author__ = "PU Junfu"

import re
import time
import subprocess
import pwd
import psutil
import argparse
import itchat


# GPU_Mem_Free_Thred = 2000
def monitor_gpu(free_mem_thre):
    print "Starting monitoring GPUs..."

    stopFlag = False
    send_msg_flag = [False] * 4
    while not stopFlag:
        time.sleep(1)
        info = get_info()
        n_gpu = len(info['gpu'])

        for i in range(n_gpu):
            mem_total = info['gpu'][i]['mem_total']
            mem_usage = info['gpu'][i]['mem_usage']
            mem_free = mem_total - mem_usage

            if (mem_free > free_mem_thre) & (not send_msg_flag[i]):
                msg = "GPU-%d, free memory: %.1fMiB" % (i, mem_free)
                print msg
                toWhom = itchat.search_friends(name = u'.')[0]['UserName']
                # toWhom = 'filehelper'
                itchat.send(msg, toUserName = toWhom)

                send_msg_flag[i] = True




def get_owner(pid):
    try:
        for line in open('/proc/%d/status' % pid):
            if line.startswith('Uid:'):
                uid = int(line.split()[1])
                return pwd.getpwuid(uid).pw_name
    except:
        return None

def get_info():
    info = { 'gpu': [], 'process': [] }
    msg = subprocess.Popen('nvidia-smi', stdout = subprocess.PIPE).stdout.read().decode()
    msg = msg.strip().split('\n')

    lino = 8
    count = 0
    while True:
        status = re.findall('.*\d+%.*\d+C.*\d+W / +\d+W.* +(\d+)MiB / +(\d+)MiB.* +(\d+)%.*', msg[lino])
        if status == []: break
        mem_usage, mem_total, percent = status[0]
        info['gpu'].append({
            'gpu_id': '%s' % count,
            'mem_usage': float(mem_usage),
            'mem_total': float(mem_total),
            'percent': float(percent),
        })
        count += 1
        lino += 3

    lino = -1
    while True:
        lino -= 1
        status = re.findall('\| +(\d+) +(\d+) +\w+ +([^ ]*) +(\d+)MiB \|', msg[lino])
        if status == []: break
        gpuid, pid, program, mem_usage = status[0]
        username = get_owner(int(pid))
        if username is None:
            print('进程已经不存在')
            continue
        try:
            p = psutil.Process(int(pid))
            p.cpu_percent()
            time.sleep(0.5)
            cpu_percent = p.cpu_percent()
        except psutil.NoSuchProcess:
            print('进程已经不存在')
            continue
        info['process'].append({
            'gpuid': int(gpuid),
            'pid': int(pid),
            'program': program,
            'cpu_percent': cpu_percent,
            'mem_usage': float(mem_usage),
            'username': username,
        })
    info['process'].reverse()

    return info


if __name__ == '__main__':
    account_alias = u'.'
    print "Login wechat..."
    itchat.auto_login(enableCmdQR=2, hotReload=True)
    account_info = itchat.search_friends(name = account_alias)


    parser = argparse.ArgumentParser()
    parser.add_argument('--free_mem',type = float, default = 10000, help = '空闲现存阈值')
    monitor_gpu(parser.parse_args().free_mem)