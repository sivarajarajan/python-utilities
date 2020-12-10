"""
This utility will consume the memory or disk to the percentage we mention via the argument.
"""
import os
import psutil
import shutil
import time
import argparse
import multiprocessing
from sys import getsizeof


def parse_cmd_arg():
    parser = argparse.ArgumentParser(description="Memory / Disk consuming utility")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-m", "--memory", type=int, help="Percentage of memory to consume")
    group.add_argument("-d", "--disk", type=int, help="Percentage of disk space to consume")
    args = parser.parse_args()
    return args


def fill_disk(expected_percent):
    # temp_data_path = "/tmp/to_be_deleted"
    temp_data_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "to_be_deleted")
    try:
        load_name = "data_block.txt"
        wait_after_fill = 10
        write_str = "!" * 1024 * 1024 * 10  # 10MB
        data_load = os.path.join(temp_data_path, "load_data.txt")

        if not os.path.isdir(temp_data_path):
            os.mkdir(temp_data_path)
        if not os.path.isfile(data_load):
            with open(data_load, "w+") as fp:
                fp.write(write_str)
            print "Primary data load :", data_load
        hdd = psutil.disk_usage("/")
        used_percent = hdd.percent
        print "used_percent :", used_percent, "Expected percent :", expected_percent
        i = 0
        while used_percent <= expected_percent:
            i += 1
            _temp_dataname = os.path.splitext(load_name)[0] + "_" + str(i) + os.path.splitext(load_name)[1]
            temp_data_file = os.path.join(temp_data_path, _temp_dataname)
            shutil.copy(data_load, temp_data_file)
            hdd = psutil.disk_usage("/")
            used_percent = hdd.percent
            print "used_percent :", used_percent
        print "\n** Wait {} seconds for the Alarm trigger **\n".format(wait_after_fill)
        time.sleep(wait_after_fill)

    except Exception as e:
        print "Exception: ", str(e)

    finally:
        if os.path.isdir(temp_data_path):
            print "Removing :", temp_data_path
            shutil.rmtree(temp_data_path)
        return True


def ram_eater(mem_to_eat, time_delay):
    print "mem_to_eat :", mem_to_eat
    print "time_delay :", time_delay
    print "Current memory usage percent :", psutil.virtual_memory().percent
    i = 1
    while psutil.virtual_memory().percent <= 100:
        eat = "a" * 1024 * 1024 * 1024 * i
        i += 1
        print getsizeof(eat)
        if psutil.virtual_memory().percent >= mem_to_eat:
            print "Current memory usage percent :", psutil.virtual_memory().percent
            print "Wait for {0} seconds for the alarm to trigger".format(time_delay)
            time.sleep(time_delay)
            break


def consume_memory(mem_to_eat):
    procs = []
    proc = multiprocessing.Process(target=ram_eater, args=(mem_to_eat, 10))
    procs.append(proc)
    proc.start()


if __name__ == "__main__":
    args = parse_cmd_arg()
    print "Arg memory :", args.memory
    print "arg disk :", args.disk
    if args.disk:
        fill_disk(args.disk)
    elif args.memory:
        consume_memory(args.memory)
