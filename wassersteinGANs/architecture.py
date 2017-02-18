import tensorflow as tf
import tensorflow.contrib.slim as slim
import sys

sys.path.insert(0, '../ops/')
from tf_ops import lrelu

def netG(z, batch_size):

   print 'GENERATOR'
   z = slim.fully_connected(z, 4*4*1024, activation_fn=None, scope='g_z')
   z = tf.reshape(z, [batch_size, 4, 4, 1024])
   print 'z:',z

   conv1 = slim.convolution2d_transpose(z, 512, 5, stride=2, activation_fn=None, scope='g_conv1')
   conv1 = tf.nn.relu(conv1)
   print 'conv1:',conv1

   conv2 = slim.convolution2d_transpose(conv1, 256, 5, stride=2, activation_fn=None, scope='g_conv2')
   conv2 = lrelu(conv2)
   print 'conv2:',conv2
   
   conv3 = slim.convolution2d_transpose(conv2, 128, 5, stride=2, activation_fn=None, scope='g_conv3')
   conv3 = lrelu(conv3)
   print 'conv3:',conv3

   conv4 = slim.convolution2d_transpose(conv3, 3, 5, stride=2, activation_fn=None, scope='g_conv4')
   conv4 = lrelu(conv4)
   print 'conv4:',conv4
   print
   print 'END G'
   print
   return conv4

'''
   Discriminator network
'''
def netD(input_images, batch_size, reuse=False):
   print 'DISCRIMINATOR' 
   sc = tf.get_variable_scope()
   with tf.variable_scope(sc, reuse=reuse):

      print 'input images:',input_images
      conv1 = slim.convolution(input_images, 128, 5, stride=2, activation_fn=None, scope='d_conv1')
      conv1 = lrelu(conv1)
      print 'conv1:',conv1

      conv2 = slim.convolution(conv1, 256, 5, stride=2, activation_fn=None, scope='d_conv2')
      conv2 = lrelu(conv2)
      print 'conv2:',conv2
      
      conv3 = slim.convolution(conv1, 512, 5, stride=2, activation_fn=None, scope='d_conv3')
      conv3 = lrelu(conv3)
      print 'conv2:',conv3

      conv4 = slim.convolution(conv1, 1024, 5, stride=2, activation_fn=None, scope='d_conv4')
      conv4 = lrelu(conv4)
      print 'conv2:',conv4

      conv4_flat = tf.reshape(conv4, [batch_size, -1])
      fc1 = slim.fully_connected(conv4_flat, 1, activation_fn=None, normalizer_fn=slim.batch_norm)
      fc1 = tf.nn.tanh(fc1)
      print 'fc1:',fc1

      print 'END D'
      return fc1

