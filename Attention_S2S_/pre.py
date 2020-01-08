#!/usr/bin/env python3



import os
import sys
import math
import time

import numpy as np
import tensorflow as tf

import data_utils
import s2s_model

tf.app.flags.DEFINE_float(
    'learning_rate',
    0.00001,
    '学习率'
)
tf.app.flags.DEFINE_float(
    'max_gradient_norm',
    5.0,
    '梯度最大阈值'
)
tf.app.flags.DEFINE_float(
    'dropout',
    1.0,
    '每层输出DROPOUT的大小'
)
tf.app.flags.DEFINE_integer(
    'batch_size',
    64,
    '批量梯度下降的批量大小'
)
tf.app.flags.DEFINE_integer(
    'size',
    512,
    'LSTM每层神经元数量'
)
tf.app.flags.DEFINE_integer(
    'num_layers',
    2,
    'LSTM的层数'
)
tf.app.flags.DEFINE_integer(
    'num_epoch',
    500,
    '训练几轮'
)
tf.app.flags.DEFINE_integer(
    'num_samples',
    512,
    '分批softmax的样本量'
)
tf.app.flags.DEFINE_integer(
    'num_per_epoch',
    10000,
    '每轮训练多少随机样本'
)
tf.app.flags.DEFINE_string(
    'buckets_dir',
    './bucket_dbs',
    'sqlite3数据库所在文件夹'
)
tf.app.flags.DEFINE_string(
    'model_dir',
    './model',
    '模型保存的目录'
)
tf.app.flags.DEFINE_string(
    'model_name',
    'model',
    '模型保存的名称'
)
tf.app.flags.DEFINE_boolean(
    'use_fp16',
    False,
    '是否使用16位浮点数（默认32位）'
)
tf.app.flags.DEFINE_integer(
    'bleu',
    -1,
    '是否测试bleu'
)
tf.app.flags.DEFINE_boolean(
    'test',
    False,
    '是否在测试'
)
tf.app.flags.DEFINE_string('gpu_fraction','3/3','idx / # of gpu fraction e.g. 1/3, 2/3, 3/3')
FLAGS = tf.app.flags.FLAGS
buckets = data_utils.buckets

def create_model(session, forward_only):
    """建立模型"""
    dtype = tf.float16 if FLAGS.use_fp16 else tf.float32
    model = s2s_model.S2SModel(
        data_utils.dim,
        data_utils.dim,
        buckets,
        FLAGS.size,
        FLAGS.dropout,
        FLAGS.num_layers,
        FLAGS.max_gradient_norm,
        FLAGS.batch_size,
        FLAGS.learning_rate,
        FLAGS.num_samples,
        forward_only,
        dtype
    )
    return model

def test():
    print("开始测试")
    class TestBucket(object):
        def __init__(self, sentence):
            self.sentence = sentence
        def random(self):
            return sentence, ''
    with tf.Session() as sess:
        #　构建模型
        model = create_model(sess, True)
        model.batch_size = 1
        # 初始化变量
        sess.run(tf.initialize_all_variables())
        
        ckpt =tf.train.get_checkpoint_state(FLAGS.model_dir)
        if ckpt == None or ckpt.model_checkpoint_path == None:
            print('restore model fail')
            return 

        print('restore model file %s' % ckpt.model_checkpoint_path)
        print(ckpt.model_checkpoint_path)
        
        model.saver.restore(sess,ckpt.model_checkpoint_path)
        print("Input 'exit()' to exit test mode!")
        # sys.stdout.write("me > ")
        # sys.stdout.flush()
        # sentence = sys.stdin.readline()
        sentence = input('me>').strip()
        if "exit()" in sentence:
            sentence = False
        while sentence:
            bucket_id = min([
                b for b in range(len(buckets))
                if buckets[b][0] > len(sentence)
            ])
            data, _ = model.get_batch_data(
                {bucket_id: TestBucket(sentence)},
                bucket_id
            )
            encoder_inputs, decoder_inputs, decoder_weights = model.get_batch(
                {bucket_id: TestBucket(sentence)},
                bucket_id,
                data
            )
            _, _, output_logits = model.step(
                sess,
                encoder_inputs,
                decoder_inputs,
                decoder_weights,
                bucket_id,
                True
            )
            outputs = [int(np.argmax(logit, axis=1)) for logit in output_logits]
            ret = data_utils.indice_sentence(outputs)
            print("AI >", ret)
            # print("me > ", end="")
            # sys.stdout.flush()
            # sentence = sys.stdin.readline()
            sentence = input('me>').strip()
            if "exit()" in sentence:
                break

def main(_):
    test()

if __name__ == '__main__':
    main()
