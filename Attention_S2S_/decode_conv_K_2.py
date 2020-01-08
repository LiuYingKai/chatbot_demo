# create by LYK 2019/12/09
# 语料库使用
import sys
import re
import os
import sqlite3
from tqdm import tqdm

#读取文件, 返回举子列表
def file_lines(file_path,file_path2):
    '''
    :param file_path: 源语料文件地址
    :return: 句子列表
    '''
    #(1) open → readlines 处理数据中的E和M
    with open(file_path,'rb') as fp:
        b = fp.read()
    content = b.decode('utf-8','ignore')
    print('开始读入数据集1')
    #读取每一行数据
    # lines = []
    # for line in tqdm(content.split("\n")):
    #     # \r\n : \r 生成一个新的行，但是光标还是在当前行
    #     # \n  光标移到下一行
    #     line = line.strip()
    #     # (2)E行的数据, 返回列表中设置为''
    #     if line.startswith('E'):
    #         lines.append('')
    #     # (3)M行的数据,返回的列表中存储为去掉/之后的结构
    #     # 原数据形状:"M 什/么/情/况"
    #     elif line.startswith('M'):
    #         # replace   split → join
    #         chars= line[2:].strip('…./').split('/')
    #         # 去掉尾部的.
    #         # 部分形状是   'M 发/射/倒/计/时/：/1/./././ /2/./././ /3/./././'
    #         # while len(chars) and chars[len(chars)-1]=='.':
    #         #     chars.pop()
    #         if chars:
    #             sentence = ''.join(chars).strip()
    #             # 去除句子内的空字符
    #             sentence = re.sub('\s+',',',sentence)
    #             lines.append(sentence)
    print('开始读入数据集2')
    with open(file_path2, 'rb') as fp:
        b = fp.read()
    content = b.decode('utf-8', 'ignore')
    lines2 = []
    idx = 3
    for line in tqdm(content.split("\r\n")):
        # \r\n : \r 生成一个新的行，但是光标还是在当前行
        # \n  光标移到下一行
        line = line.rstrip()
        # (2)E行的数据, 返回列表中设置为''
        # if line.startswith('E'):
        #     lines.append('')
        # (3)M行的数据,返回的列表中存储为去掉/之后的结构
        # 原数据形状:"M 什/么/情/况"
        if line:
            # replace   split → join
            if idx % 2 == 1:
                chars = line
            else:
                chars = line
            if chars == '':
                print(idx - 2)
            # 去掉尾部的.
            # 部分形状是   'M 发/射/倒/计/时/：/1/./././ /2/./././ /3/./././'
            # while len(chars) and chars[len(chars)-1]=='.':
            #     chars.pop()
            if chars:
                sentence = chars
                # 去除句子内的空字符
                sentence = re.sub('\s+', ',', sentence)
                lines2.append(sentence)
            else:
                print(idx - 2)
            idx += 1
    # return lines,lines2
    return lines2

# sqlite数据库链接,数据库都快忘光了.......烦死了........
def sqlite_conn(db_path):
    # 链接
    conn = sqlite3.connect(db_path)
    # 操作游标
    cursor = conn.cursor()
    # 执行操作,创建表
    cursor.execute('''
        create table if not exists conversation(ask text, answer text);
    ''')
    conn.commit()
    return conn,cursor

# 数据验证
def valid(text,max_len = 50):
    if len(text) > 0 and re.findall('[\u4e00-\u9fa5]',text) and (len(text) < max_len or max_len == 0):
        return True
    else:
        return False
# 数据库插入记录的操作
# def insert(ask,answer,cursor):
#     '''
#    :param ask: 上句
#     :param answer: 下句
#     :param cursor: 数据库操作游标
#     :return: None
#     '''
#     cursor.execute('''
#     insert into conversation (ask,answer) values ('{}','{}')
#     '''.format(ask,answer))

# 执行数据验证, 并通过验证执行插入操作
def insert_if(ask, answer, cursor):
    '''

    :param ask: 问句,也就是对话中该死的上句
    :param answer: 回答, 没错,我的老伙计, 就是问句说完之后我要回复的下句
    :param cursor: 数据库操作游标, 真见鬼, 我就要用这玩意来指挥数据库
    :return: 如果通过验证返回1 ,否则就返回0, 哦我的上帝,返回结果就是这样
    '''
    if valid(ask) and valid(answer):
        # insert(ask, answer, cursor)
        cursor.execute('''
            INSERT INTO conversation (ask,answer) VALUES ('{}','{}')
        '''.format(ask.replace("'","''"), answer.replace("'","''")))
        return 1
    return 0
# 读取语料库
def main(file_path,file_path2):
    '''
    :param file_path: 语料库的路径
    :return:
    '''
    # lines,lines2 = file_lines(file_path,file_path2)
    lines2 = file_lines(file_path,file_path2)

    #生成数据库链接conn 和 游标cursor
    db_path = 'db/conversation.db'
    # 判断路径是否存在
    if os.path.exists(db_path):
        # 如果文件已经存在, 那么就要delete这个文件
        os.remove(db_path)
    if not os.path.exists(os.path.dirname(db_path)):
        # 如果文件夹不存在, 那么就执行创建操作
        os.makedirs(os.path.dirname(db_path))
    conn, cursor = sqlite_conn(db_path)
    # 生成问答对
    # 由于语料库中有连续对话,所以在拆分问答对的时候我们应该充分利用语料的特点
    # 来生成上句和下句这样的组合关系
    print('读入数据集1')
    answer = ''
    inserted_num = 0
    # for line in tqdm(lines):
    #     ask =answer# 以上一次的回答作为下一次的问句
    #     answer = line # 使用当前的文本赋值为当前的下句
    #     # 验证问大数据, 并把满足条件的, 执行插入数据的操作
    #     # (3)问答对先缓存到一个db文件中去
    #     inserted_num+=insert_if(ask,answer,cursor)
    #     # 如果不是插入的数据量为0, 并且满足能整除5000的情况下,执行数据库提交操作
    #     if inserted_num!=0 and inserted_num%5000==0:
    #         conn.commit()
    # conn.commit()
    print('读入数据集2')
    idx = 3
    ask = 'a'
    answer = 'b'
    inserted_num = 0
    for line in tqdm(lines2):
        if idx % 2 ==1:
            ask = line
        else:
            answer = line
            inserted_num += insert_if(ask, answer, cursor)
            if inserted_num != 0 and inserted_num % 200 == 0:
                conn.commit()
        idx+=1
    conn.commit()




if __name__ == '__main__':
    file_path = 'xiaohuangji50w_nofenci.conv'
    file_path2 = 'k_data.conv'
    # 外部传递参数时进行接收, 重新定义file_path
    if len(sys.argv)==2:
        # 判断传递过来的参数列表是不是长度为2
        file_path = sys.argv[1]
    # 判断file_path路径是否存在
    if not os.path.exists(file_path):
        print(f'文件{file_path}不存在')
    else:
        # 执行操作
        #pass
        main(file_path,file_path2)
