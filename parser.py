#!/usr/bin python
import re
import time
import sys, getopt
import xml.etree.ElementTree as ET
import os

LOG_START = 0
LOG_END = 1
LOG_NONE = 2

start_key = ""
end_key = ""
# match start and end with the same signature in them, descript the signature's
# index of start and end using tuple
signature = [0,0]
starter_list = []

def calc_duration(start, end):
    _start = time.strptime("2015-1-1 "+start, "%Y-%m-%d %H:%M:%S")
    _end = time.strptime("2015-1-1 "+end, "%Y-%m-%d %H:%M:%S")
    return time.mktime(_end) - time.mktime(_start)

def load_config(cf_file):
    tree = ET.parse(cf_file)
    root = tree.getroot()
    item = root.find('item')
    s = item.find('start').text
    e = item.find('end').text
    sg = [0,0]
    sgntr = item.find('signature').text
    sgntr = sgntr.split(',')
    if len(sgntr) != 2:
        print "Signature is invalid, please check config file"
    else:
        sg[0] = int(sgntr[0])
        sg[1] = int(sgntr[1])
        print "Signature's range is (%d, %d)" % (sg[0], sg[1])
    return s, e, sg

class Stack:
    def __init__(self):
        self.items= []

    def isEmpty(self):
        return self.items == []

    def push(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def peek(self):
        return self.items[len(self.items)-1]

    def size(self):
        return len(self.items)



def format_log(log):
    pass

def merge_log(start_log, end_log):
    log = {}
    log['Start'] = start_log['time']
    log['End'] = end_log['time']
    log['StartMsg'] = start_log['content']
    log['EndMsg'] = end_log['content']
    return log


def find_keyword(start_k, end_k, msg):
    s = msg.find(start_k)
    e = msg.find(end_k)
    if s != -1:
        return LOG_START
    elif e != -1:
        return LOG_END
    else:
        return LOG_NONE

def parse_log_msg(msg):
    log = {}
    log_type = ''
    #find () or {} or []
    regex = "[\(|\[\{].*[\)\]\}]"
    addr = re.findall(regex, msg)
    if addr:
        log['address'] = addr[0][1:-1]
        type_end = msg.find(addr[0]) - 1
        log_type = msg[:type_end]
        log['type'] = log_type

def parse_line(raw_line):
    log = {}
    regex  = '([\S]+)\s{1,}([\S]+)\s{1,}([\S]+)\s{1,}([\S]+)\s{1,}([\S]+)\s{1,}([\S]+)\s{1,}([\S]+)\s{1,}([\S]+)\s{1,}([\S]+)\s{1,}([\S]+)\s{1,}([^\\r]+)'
    line_tuple = re.match(regex, raw_line).groups()
    log['time'] = line_tuple[4]
    log['content'] = line_tuple[-1]
    return log

def load_param(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:o:k:", ["ifile=", "ofile=", "keyword="])
    except getopt.GetoptError:
        print 'parser.py -i <inputfile> -o <outputfile> -k <keyword>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'parser.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            _inputfile = arg
        elif opt in ("-o", "--ofile"):
            _outputfile = arg
        elif opt in ("-k", "--keyword"):
            _keyword = arg
    return _inputfile, _outputfile



def main(argv):
    inputfile = ''
    outputfile = ''
    keyword = ''
    start_key, end_key, signature = load_config('config.xml')
    inputfile, outputfile = load_param(argv)
    print "Log file: ", inputfile
    print "Output file: ", outputfile
    if inputfile == '' or outputfile == '':
        print 'parser.py -i <inputfile> -o <outputfile>'
        sys.exit()
    log_size = float(os.stat(inputfile).st_size)
    log_file = open(inputfile, "r")
    o_file = open(outputfile, "w")
    for line in log_file:
        print '\r >> ', str(int((log_file.tell()/log_size) * 100)), '% completed',
        log = parse_line(line)
        log_type = find_keyword(start_key, end_key, log['content'])
        if log_type == LOG_NONE:
            continue
        if log_type == LOG_START:
            starter_list.append(log)
        if log_type == LOG_END:
            _s = signature[0]
            _e = signature[1]
            sgntr = log['content'][_s:_e]
            for i in range(len(starter_list)-1, -1, -1):
                if starter_list[i]['content'][_s:_e] == sgntr:
                    start_log = starter_list.pop(i)
                    m_log = merge_log(start_log, log)
                    m_log['address'] = sgntr
                    m_log['duration'] = calc_duration(m_log['Start'], m_log['End'])
                    m_log['type'] = m_log['StartMsg'][:_s]
                    o_file.writelines(m_log['type'] + '\t' + m_log['Start'] + '\t' + m_log['End'] + '\t' +\
                                      str(m_log['duration']) + '\t' + m_log['address'] + '\t' + \
                                      '\t' + m_log['StartMsg'] + '\t' + m_log['EndMsg'] + '\n')

    log_file.close()
    o_file.close()

if __name__ == "__main__":
    main(sys.argv[1:])
