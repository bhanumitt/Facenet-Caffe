import caffe
import tensorflow as tf
import os
import numpy as np
import sys
import cv2
from caffe.proto import caffe_pb2

import sys
sys.path.append("mtcnn")
import mtcnn

from time import time
_tstart_stack = []
def tic():
    _tstart_stack.append(time())
def toc(fmt="Elapsed: %s s"):
    print(fmt % (time()-_tstart_stack.pop()))

def load_model(model, input_map=None):
    model_exp = os.path.expanduser(model)
    print('Model directory: %s' % model_exp)
    meta_file = 'model-20180402-114759.meta'
    ckpt_file = 'model-20180402-114759.ckpt-275'

    saver = tf.train.import_meta_graph(os.path.join(model_exp, meta_file), input_map=input_map)
    saver.restore(tf.get_default_session(), os.path.join(model_exp, ckpt_file))

def Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net):
    var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/weights:0'))
    net.params[caffeLayerName][0].data[...] = var1.transpose((3, 2, 0, 1))
    var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/BatchNorm/moving_mean:0'))
    net.params[caffeLayerName+'/BatchNorm'][0].data[...] = var1
    var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/BatchNorm/moving_variance:0'))
    net.params[caffeLayerName+'/BatchNorm'][1].data[...] = var1 + 0.001
    net.params[caffeLayerName+'/BatchNorm'][2].data[...] = 1
    var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/BatchNorm/beta:0'))
    net.params[caffeLayerName+'/Scale'][0].data[...] = 1
    net.params[caffeLayerName+'/Scale'][1].data[...] = var1
    return net

    ########## Origin Style
    # var1 = sess.run(tf.get_default_graph().get_tensor_by_name('InceptionResnetV1/Conv2d_4b_3x3/weights:0'))
    # net.params['Conv2d_4b_3x3'][0].data[...] = var1.transpose((3, 2, 0, 1))
    # var1 = sess.run(tf.get_default_graph().get_tensor_by_name('InceptionResnetV1/Conv2d_4b_3x3/BatchNorm/moving_mean:0'))
    # net.params['Conv2d_4b_3x3/BatchNorm'][0].data[...] = var1
    # var1 = sess.run(tf.get_default_graph().get_tensor_by_name('InceptionResnetV1/Conv2d_4b_3x3/BatchNorm/moving_variance:0'))
    # net.params['Conv2d_4b_3x3/BatchNorm'][1].data[...] = var1 + 0.001
    # net.params['Conv2d_4b_3x3/BatchNorm'][2].data[...] = 1
    # var1 = sess.run(tf.get_default_graph().get_tensor_by_name('InceptionResnetV1/Conv2d_4b_3x3/BatchNorm/beta:0'))
    # net.params['Conv2d_4b_3x3/Scale'][0].data[...] = 1
    # net.params['Conv2d_4b_3x3/Scale'][1].data[...] = var1

def Block35_Repeat(sess, net):
    for i in range(1,6):

        caffeLayerName = 'block35_'+str(i)+'/Branch_0/Conv2d_1x1'
        tfLayerName = 'InceptionResnetV1/Repeat/block35_'+str(i)+'/Branch_0/Conv2d_1x1'
        net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)

        caffeLayerName = 'block35_'+str(i)+'/Branch_1/Conv2d_0a_1x1'
        tfLayerName = 'InceptionResnetV1/Repeat/block35_'+str(i)+'/Branch_1/Conv2d_0a_1x1'
        net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
        caffeLayerName = 'block35_'+str(i)+'/Branch_1/Conv2d_0b_3x3'
        tfLayerName = 'InceptionResnetV1/Repeat/block35_'+str(i)+'/Branch_1/Conv2d_0b_3x3'
        net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)

        caffeLayerName = 'block35_'+str(i)+'/Branch_2/Conv2d_0a_1x1'
        tfLayerName = 'InceptionResnetV1/Repeat/block35_'+str(i)+'/Branch_2/Conv2d_0a_1x1'
        net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
        caffeLayerName = 'block35_'+str(i)+'/Branch_2/Conv2d_0b_3x3'
        tfLayerName = 'InceptionResnetV1/Repeat/block35_'+str(i)+'/Branch_2/Conv2d_0b_3x3'
        net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
        caffeLayerName = 'block35_'+str(i)+'/Branch_2/Conv2d_0c_3x3'
        tfLayerName = 'InceptionResnetV1/Repeat/block35_'+str(i)+'/Branch_2/Conv2d_0c_3x3'
        net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)

        caffeLayerName = 'block35_'+str(i)+'/Conv2d_1x1'
        tfLayerName = 'InceptionResnetV1/Repeat/block35_'+str(i)+'/Conv2d_1x1'
        var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/weights:0'))
        net.params[caffeLayerName][0].data[...] = var1.transpose((3, 2, 0, 1))
        var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/biases:0'))
        net.params[caffeLayerName][1].data[...] = var1  # Conv Bias

    ########## Origin Style
    # caffeLayerName = 'block35_1/Branch_0/Conv2d_1x1'
    # tfLayerName = 'InceptionResnetV1/Repeat/block35_1/Branch_0/Conv2d_1x1'
    # net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    #
    # caffeLayerName = 'block35_1/Branch_1/Conv2d_0a_1x1'
    # tfLayerName = 'InceptionResnetV1/Repeat/block35_1/Branch_1/Conv2d_0a_1x1'
    # net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    # caffeLayerName = 'block35_1/Branch_1/Conv2d_0b_3x3'
    # tfLayerName = 'InceptionResnetV1/Repeat/block35_1/Branch_1/Conv2d_0b_3x3'
    # net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    #
    # caffeLayerName = 'block35_1/Branch_2/Conv2d_0a_1x1'
    # tfLayerName = 'InceptionResnetV1/Repeat/block35_1/Branch_2/Conv2d_0a_1x1'
    # net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    # caffeLayerName = 'block35_1/Branch_2/Conv2d_0b_3x3'
    # tfLayerName = 'InceptionResnetV1/Repeat/block35_1/Branch_2/Conv2d_0b_3x3'
    # net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    # caffeLayerName = 'block35_1/Branch_2/Conv2d_0c_3x3'
    # tfLayerName = 'InceptionResnetV1/Repeat/block35_1/Branch_2/Conv2d_0c_3x3'
    # net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    #
    # caffeLayerName = 'block35_1/Conv2d_1x1'
    # tfLayerName = 'InceptionResnetV1/Repeat/block35_1/Conv2d_1x1'
    # var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/weights:0'))
    # net.params[caffeLayerName][0].data[...] = var1.transpose((3, 2, 0, 1))
    # var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/biases:0'))
    # net.params[caffeLayerName][1].data[...] = var1  # Conv Bias

    return net

def Mixed_6a(sess, net):
    caffeLayerName = 'Mixed_6a/Branch_0/Conv2d_1a_3x3'
    tfLayerName = 'InceptionResnetV1/Mixed_6a/Branch_0/Conv2d_1a_3x3'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)

    caffeLayerName = 'Mixed_6a/Branch_1/Conv2d_0a_1x1'
    tfLayerName = 'InceptionResnetV1/Mixed_6a/Branch_1/Conv2d_0a_1x1'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    caffeLayerName = 'Mixed_6a/Branch_1/Conv2d_0b_3x3'
    tfLayerName = 'InceptionResnetV1/Mixed_6a/Branch_1/Conv2d_0b_3x3'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    caffeLayerName = 'Mixed_6a/Branch_1/Conv2d_1a_3x3'
    tfLayerName = 'InceptionResnetV1/Mixed_6a/Branch_1/Conv2d_1a_3x3'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    return net

def Block17_Repeat(sess, net):
    for i in range(1,11):

        caffeLayerName = 'block17_'+str(i)+'/Branch_0/Conv2d_1x1'
        tfLayerName = 'InceptionResnetV1/Repeat_1/block17_'+str(i)+'/Branch_0/Conv2d_1x1'
        net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)

        caffeLayerName = 'block17_'+str(i)+'/Branch_1/Conv2d_0a_1x1'
        tfLayerName = 'InceptionResnetV1/Repeat_1/block17_'+str(i)+'/Branch_1/Conv2d_0a_1x1'
        net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
        caffeLayerName = 'block17_'+str(i)+'/Branch_1/Conv2d_0b_1x7'
        tfLayerName = 'InceptionResnetV1/Repeat_1/block17_'+str(i)+'/Branch_1/Conv2d_0b_1x7'
        net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
        caffeLayerName = 'block17_'+str(i)+'/Branch_1/Conv2d_0c_7x1'
        tfLayerName = 'InceptionResnetV1/Repeat_1/block17_'+str(i)+'/Branch_1/Conv2d_0c_7x1'
        net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)

        caffeLayerName = 'block17_'+str(i)+'/Conv2d_1x1'
        tfLayerName = 'InceptionResnetV1/Repeat_1/block17_'+str(i)+'/Conv2d_1x1'
        var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/weights:0'))
        net.params[caffeLayerName][0].data[...] = var1.transpose((3, 2, 0, 1))
        var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/biases:0'))
        net.params[caffeLayerName][1].data[...] = var1  # Conv Bias
    return net

def Mixed_7a(sess, net):
    caffeLayerName = 'Mixed_7a/Branch_0/Conv2d_0a_1x1'
    tfLayerName = 'InceptionResnetV1/Mixed_7a/Branch_0/Conv2d_0a_1x1'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    caffeLayerName = 'Mixed_7a/Branch_0/Conv2d_1a_3x3'
    tfLayerName = 'InceptionResnetV1/Mixed_7a/Branch_0/Conv2d_1a_3x3'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)

    caffeLayerName = 'Mixed_7a/Branch_1/Conv2d_0a_1x1'
    tfLayerName = 'InceptionResnetV1/Mixed_7a/Branch_1/Conv2d_0a_1x1'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    caffeLayerName = 'Mixed_7a/Branch_1/Conv2d_1a_3x3'
    tfLayerName = 'InceptionResnetV1/Mixed_7a/Branch_1/Conv2d_1a_3x3'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)

    caffeLayerName = 'Mixed_7a/Branch_2/Conv2d_0a_1x1'
    tfLayerName = 'InceptionResnetV1/Mixed_7a/Branch_2/Conv2d_0a_1x1'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    caffeLayerName = 'Mixed_7a/Branch_2/Conv2d_0b_3x3'
    tfLayerName = 'InceptionResnetV1/Mixed_7a/Branch_2/Conv2d_0b_3x3'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    caffeLayerName = 'Mixed_7a/Branch_2/Conv2d_1a_3x3'
    tfLayerName = 'InceptionResnetV1/Mixed_7a/Branch_2/Conv2d_1a_3x3'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)

    caffeLayerName = 'Conv_const'
    convData = np.zeros([896,896,2,2])
    for i in range(896):
        convData[i][i][0][0] = 1
    net.params[caffeLayerName][0].data[...] = convData
    return net

def Block8_Repeat(sess, net):
    for i in range(1,6):

        caffeLayerName = 'block8_'+str(i)+'/Branch_0/Conv2d_1x1'
        tfLayerName = 'InceptionResnetV1/Repeat_2/block8_'+str(i)+'/Branch_0/Conv2d_1x1'
        net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)

        caffeLayerName = 'block8_'+str(i)+'/Branch_1/Conv2d_0a_1x1'
        tfLayerName = 'InceptionResnetV1/Repeat_2/block8_'+str(i)+'/Branch_1/Conv2d_0a_1x1'
        net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
        caffeLayerName = 'block8_'+str(i)+'/Branch_1/Conv2d_0b_1x3'
        tfLayerName = 'InceptionResnetV1/Repeat_2/block8_'+str(i)+'/Branch_1/Conv2d_0b_1x3'
        net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
        caffeLayerName = 'block8_'+str(i)+'/Branch_1/Conv2d_0c_3x1'
        tfLayerName = 'InceptionResnetV1/Repeat_2/block8_'+str(i)+'/Branch_1/Conv2d_0c_3x1'
        net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)

        caffeLayerName = 'block8_'+str(i)+'/Conv2d_1x1'
        tfLayerName = 'InceptionResnetV1/Repeat_2/block8_'+str(i)+'/Conv2d_1x1'
        var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/weights:0'))
        net.params[caffeLayerName][0].data[...] = var1.transpose((3, 2, 0, 1))
        var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/biases:0'))
        net.params[caffeLayerName][1].data[...] = var1  # Conv Bias
    return net

def Block8(sess, net):
    caffeLayerName = 'Block8/Branch_0/Conv2d_1x1'
    tfLayerName = 'InceptionResnetV1/Block8/Branch_0/Conv2d_1x1'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)

    caffeLayerName = 'Block8/Branch_1/Conv2d_0a_1x1'
    tfLayerName = 'InceptionResnetV1/Block8/Branch_1/Conv2d_0a_1x1'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    caffeLayerName = 'Block8/Branch_1/Conv2d_0b_1x3'
    tfLayerName = 'InceptionResnetV1/Block8/Branch_1/Conv2d_0b_1x3'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)
    caffeLayerName = 'Block8/Branch_1/Conv2d_0c_3x1'
    tfLayerName = 'InceptionResnetV1/Block8/Branch_1/Conv2d_0c_3x1'
    net = Conv_BN_Scale_Relu(caffeLayerName, tfLayerName, sess, net)

    caffeLayerName = 'Block8/Conv2d_1x1'
    tfLayerName = 'InceptionResnetV1/Block8/Conv2d_1x1'
    var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/weights:0'))
    net.params[caffeLayerName][0].data[...] = var1.transpose((3, 2, 0, 1))
    var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/biases:0'))
    net.params[caffeLayerName][1].data[...] = var1  # Conv Bias
    return net

def Bottleneck(sess, net):
    caffeLayerName = 'Bottleneck'
    tfLayerName = 'InceptionResnetV1/Bottleneck'
    var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/weights:0'))
    net.params[caffeLayerName][0].data[...] = var1.transpose((1,0))

    var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/BatchNorm/moving_mean:0'))
    net.params[caffeLayerName+'/BatchNorm'][0].data[...] = var1
    var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/BatchNorm/moving_variance:0'))
    net.params[caffeLayerName+'/BatchNorm'][1].data[...] = var1 + 0.001
    net.params[caffeLayerName+'/BatchNorm'][2].data[...] = 1
    var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/BatchNorm/beta:0'))
    net.params[caffeLayerName+'/Scale'][0].data[...] = 1
    net.params[caffeLayerName+'/Scale'][1].data[...] = var1
    return net

def Bottleneck_conv1x1_512(sess, net):
    caffeLayerName = 'Conv1x1_512'
    tfLayerName = 'InceptionResnetV1/Bottleneck'
    var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/weights:0'))
    print(var1.transpose((1,0)).shape)
    print(var1.transpose((1,0))[np.newaxis][np.newaxis].transpose(2,3,0,1).shape)
    print(var1.transpose((1,0))[:,np.newaxis][:,np.newaxis].shape)
    print(var1.transpose((1,0))[np.newaxis,:][:,np.newaxis,:].shape)
    print(net.params[caffeLayerName][0].data.shape)
    net.params[caffeLayerName][0].data[...] = var1.transpose((1,0))[np.newaxis][np.newaxis].transpose(2,3,0,1)
    # print(net.params[caffeLayerName][0].data.shape)

    caffeLayerName = 'Bottleneck'
    var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/BatchNorm/moving_mean:0'))
    net.params[caffeLayerName+'/BatchNorm'][0].data[...] = var1
    var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/BatchNorm/moving_variance:0'))
    net.params[caffeLayerName+'/BatchNorm'][1].data[...] = var1 + 0.001
    net.params[caffeLayerName+'/BatchNorm'][2].data[...] = 1
    var1 = sess.run(tf.get_default_graph().get_tensor_by_name(tfLayerName+'/BatchNorm/beta:0'))
    net.params[caffeLayerName+'/Scale'][0].data[...] = 1
    net.params[caffeLayerName+'/Scale'][1].data[...] = var1
    return net

def prewhiten(x):
    mean = np.mean(x)
    std = np.std(x)
    print(mean, std)
    std_adj = np.maximum(std, 1.0/np.sqrt(x.size))
    y = np.multiply(np.subtract(x, mean), 1/std_adj)
    # print(y[0])
    return y

def normL2Vector(bottleNeck):
    sum = 0
    for v in bottleNeck:
        sum += np.power(v, 2)
    sqrt = np.max([np.sqrt(sum), 0.0000000001])
    vector = np.zeros((bottleNeck.shape))
    for (i, v) in enumerate(bottleNeck):
        vector[i] = v/sqrt
    return vector.astype(np.float32)

def convertTf2Caffe():
    model_dir = '/Volumes/SL-BG2/Download/20180402-114759'
    with tf.Session() as sess:
        load_model(model_dir)

        srandData = np.random.random((1,160,160,3))
        inputTF = srandData #[1,160,160,3]
        inputCaffe = srandData.transpose((0,3,1,2)) #[1,3,160,160]

        caffePrototxt = 'resnetInception.prototxt2'
        net = caffe.Net(caffePrototxt, caffe.TEST)

        # print("=====", net.params['Conv2d_1a_3x3'][1].data.shape)
        # net.params['Conv2d_1a_3x3'][1].data[...] = np.zeros(net.params['Conv2d_1a_3x3'][1].data.shape)

        images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
        phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
        embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        feed_dict = { images_placeholder: inputTF, phase_train_placeholder:False }
        print(sess.run(embeddings, feed_dict=feed_dict))
        print('\n=============\n')

        # Conv + BatchNorm + Scale + Relu
        net = Conv_BN_Scale_Relu('Conv2d_1a_3x3', 'InceptionResnetV1/Conv2d_1a_3x3', sess, net)
        net = Conv_BN_Scale_Relu('Conv2d_2a_3x3', 'InceptionResnetV1/Conv2d_2a_3x3', sess, net)
        net = Conv_BN_Scale_Relu('Conv2d_2b_3x3', 'InceptionResnetV1/Conv2d_2b_3x3', sess, net)
        # MaxPool
        net = Conv_BN_Scale_Relu('Conv2d_3b_1x1', 'InceptionResnetV1/Conv2d_3b_1x1', sess, net)
        net = Conv_BN_Scale_Relu('Conv2d_4a_3x3', 'InceptionResnetV1/Conv2d_4a_3x3', sess, net)
        net = Conv_BN_Scale_Relu('Conv2d_4b_3x3', 'InceptionResnetV1/Conv2d_4b_3x3', sess, net)

        net = Block35_Repeat(sess, net)
        net = Mixed_6a(sess, net)
        net = Block17_Repeat(sess, net)
        net = Mixed_7a(sess, net)
        net = Block8_Repeat(sess, net)
        net = Block8(sess, net)
        # Bottleneck(sess, net)
        net = Bottleneck_conv1x1_512(sess, net)
        # var1 = sess.run(tf.get_default_graph().get_tensor_by_name('InceptionResnetV1/Conv2d_1a_3x3/BatchNorm/beta:0'))
        # net.params['Conv2d_1a_3x3/BatchNorm'][0].data[...] = var1
        net.blobs['data'].data[...] = inputCaffe

        net.forward()
        # print(net.blobs['flatten'].data.squeeze())
        vector = normL2Vector(net.blobs['flatten'].data.squeeze())
        print(vector)
        net.save('InceptionResnet_Model/inception_resnet_v1_conv1x1.caffemodel')
        # print(net.blobs['Conv2d_1a_3x3'].data.transpose((0, 2, 3, 1)))
        # print(net.params['Conv2d_1a_3x3'][0].data[...])

def calcCaffeVector(img):
    # cv2.imshow('tet', cv2.resize(img, (160,160)))
    # cv2.waitKey(0)
    img = cv2.resize(img, (160,160))
    prewhitened = prewhiten(img)[np.newaxis]
    inputCaffe = prewhitened.transpose((0,3,1,2)) #[1,3,160,160]
    print(inputCaffe.shape)
    caffePrototxt = 'resnetInception.prototxt2'
    caffemodel = 'InceptionResnet_Model/inception_resnet_v1_conv1x1.caffemodel'
    net = caffe.Net(caffePrototxt, caffemodel, caffe.TEST)
    net.blobs['data'].data[...] = inputCaffe
    tic()
    net.forward()
    # print(net.blobs['flatten'].data.squeeze())
    vector = normL2Vector(net.blobs['flatten'].data.squeeze())
    print(vector)
    toc()

def calcTFVector(img):
    model_dir = '/Volumes/SL-BG2/Download/20180402-114759'
    with tf.Session() as sess:
        load_model(model_dir)

        inputTF = cv2.resize(img, (160,160))[np.newaxis]
        print(inputTF.shape)

        images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
        phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
        embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
        feed_dict = { images_placeholder: inputTF, phase_train_placeholder:False }
        tic()
        print(sess.run(embeddings, feed_dict=feed_dict))
        toc()

def caffemodel2Prototxt(modelName):
    with open(modelName, 'rb') as f:
        caffemodel = caffe_pb2.NetParameter()
        caffemodel.ParseFromString(f.read())
        for item in caffemodel.layers:
            item.ClearField('blobs')
        for item in caffemodel.layer:
            item.ClearField('blobs')

        print(str(caffemodel))

def mtcnnDetect(img):
    minsize = 40
    caffe_model_path = "./mtcnn"

    threshold = [0.8, 0.8, 0.6]
    factor = 0.709

    caffe.set_mode_cpu()
    PNet = caffe.Net(caffe_model_path+"/det1.prototxt", caffe_model_path+"/det1.caffemodel", caffe.TEST)
    RNet = caffe.Net(caffe_model_path+"/det2.prototxt", caffe_model_path+"/det2.caffemodel", caffe.TEST)
    ONet = caffe.Net(caffe_model_path+"/det3.prototxt", caffe_model_path+"/det3.caffemodel", caffe.TEST)

    img_matlab = img.copy()
    tmp = img_matlab[:,:,2].copy()
    img_matlab[:,:,2] = img_matlab[:,:,0]
    img_matlab[:,:,0] = tmp

    boundingboxes, points = mtcnn.detect_face(img_matlab, minsize, PNet, RNet, ONet, threshold, False, factor)
    warped = img_matlab[int(boundingboxes[0][1]):int(boundingboxes[0][3]),
                        int(boundingboxes[0][0]):int(boundingboxes[0][2])]
    print(int(boundingboxes[0][1]), int(boundingboxes[0][3]), int(boundingboxes[0][0]), int(boundingboxes[0][2]))
    warped = cv2.resize(warped, (160,160))
    return warped

imgPath = '/Users/ludong/Desktop/VideoFace/VideoFace/mtcnn/ZhaoRuiLong.jpg'
img = cv2.imread(imgPath)
crop = mtcnnDetect(img)

cv2.imshow('test', crop)
cv2.waitKey(0)
# calcTFVector(crop)
# img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
calcCaffeVector(crop)
# convertTf2Caffe()
# caffemodel2Prototxt('inception_resnet_v1.caffemodel')
# net.params['conv_1'][0].data[...] = conv_w1
