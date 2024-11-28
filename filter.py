#!/usr/bin/env python
"""
现场bag过大时,过滤部分bag,便于保存传输
"""
import sys
import os
import shutil
import rosbag

a = shutil.get_terminal_size()
terminal_width = a[0] - 5

def process_bar(start,end,time_now):
    """
    进度条
    """
    _precent = (time_now - start) / (end - start)
    indx = int(_precent * terminal_width)
    print("{}%".format(round(_precent * 100, 3)), "▓" * (indx), end="\r")


def filter_topics(inbag, outbag, topics_to_keep):
    """
    根据topic过滤inbag
    """
    print(topics_to_keep)
    with rosbag.Bag(outbag, 'w') as outbag_handle:
        for topic, msg, time in rosbag.Bag(inbag).read_messages():
            if topic in topics_to_keep:
                outbag_handle.write(topic, msg, time)

def filter_time(inbag, outbag, start_time, end_time):
    """
    根据时间过滤内容
    """
    print(f"start_time:{start_time}, end_time:{end_time}")
    with rosbag.Bag(outbag, 'w') as outbag_handle:
        for topic, msg, time in rosbag.Bag(inbag).read_messages():
            if float(time.secs) < start_time:
                continue
            if float(time.secs) >= end_time:
                outbag_handle.close()
                break
            process_bar(start_time, end_time, float(time.secs))
            outbag_handle.write(topic, msg, time)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: filter_bag.py "\
        "<initial_bag> <output_bag> <topics/time> <topics_to_keep/start_time, end_time>")
        sys.exit(1)

    INPUT_BAG = sys.argv[1]
    OUTPUT_BAG = sys.argv[2]
    FILTER_TYPE = sys.argv[3]
    filter_condition = sys.argv[4:]

    if FILTER_TYPE == "topics":
        topics_list = filter_condition[0].split(',')
        filter_topics(INPUT_BAG, OUTPUT_BAG, topics_list)
    elif FILTER_TYPE == "time":
        time_list = filter_condition[0].split(',')
        t1 = float(time_list[0])
        t2 = float(time_list[1])
        filter_time(INPUT_BAG, OUTPUT_BAG, t1,t2)
    else:
        print('wrong type')
        sys.exit(1)
    os.system(f"rosbag compress --lz4 {OUTPUT_BAG}")
    orin_name = OUTPUT_BAG.split('.')[0]+'.orig.bag'
    os.system(f"rm {orin_name}")
