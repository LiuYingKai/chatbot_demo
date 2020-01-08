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
    0.0003,
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
    5,
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
    0,
    '是否测试bleu'
)
tf.app.flags.DEFINE_boolean(
    'test',
    False,
    '是否在测试'
)

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

def test_bleu(count):
    """测试bleu"""
    print("bleu test mode")
    from nltk.translate.bleu_score import sentence_bleu
    from tqdm import tqdm
    # 准备数据
    print('准备数据')
    bucket_dbs = data_utils.read_bucket_dbs(FLAGS.buckets_dir)
    bucket_sizes = []
    for i in range(len(buckets)):
        bucket_size = bucket_dbs[i].size
        bucket_sizes.append(bucket_size)
        print('bucket {} 中有数据 {} 条'.format(i, bucket_size))
    total_size = sum(bucket_sizes)
    print('共有数据 {} 条'.format(total_size))
    # bleu设置0的话，默认对所有样本采样
    if count <= 0:
        count = total_size
    buckets_scale = [
        sum(bucket_sizes[:i + 1]) / total_size
        for i in range(len(bucket_sizes))
    ]
    with tf.Session() as sess:
        #　构建模型
        model = create_model(sess, True)
        model.batch_size = 1
        # 初始化变量
        # sess.run(tf.initialize_all_variables())
        # model.saver.restore(sess, os.path.join(FLAGS.model_dir, FLAGS.model_name))
        sess.run(tf.initialize_all_variables())

        ckpt = tf.train.get_checkpoint_state(FLAGS.model_dir)
        if ckpt == None or ckpt.model_checkpoint_path == None:
            print('restore model fail')
            return

        print('restore model file %s' % ckpt.model_checkpoint_path)
        print(ckpt.model_checkpoint_path)

        model.saver.restore(sess, ckpt.model_checkpoint_path)

        total_score = 0.0
        for i in tqdm(range(count)):
            # 选择一个要训练的bucket
            random_number = np.random.random_sample()
            bucket_id = min([
                i for i in range(len(buckets_scale))
                if buckets_scale[i] > random_number
            ])
            data, _ = model.get_batch_data(
                bucket_dbs,
                bucket_id
            )
            encoder_inputs, decoder_inputs, decoder_weights = model.get_batch(
                bucket_dbs,
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
            ask, _ = data[0]
            all_answers = bucket_dbs[bucket_id].all_answers(ask)
            ret = data_utils.indice_sentence(outputs)
            if not ret:
                continue
            references = [list(x) for x in all_answers]
            score = sentence_bleu(
                references,
                list(ret),
                weights=(1.0,)
            )
            total_score += score
        print('BLUE: {:.2f} in {} samples'.format(total_score / count * 10, count))


def main(_):
    test_bleu(100)

if __name__ == '__main__':
    np.random.seed(0)
    tf.set_random_seed(0)
    tf.app.run()
