import tensorflow as tf
from architecture import netD, netG
import sys
import numpy as np
import random
import cv2
import ntpath
import os

sys.path.insert(0, 'config/')
sys.path.insert(0, '../ops/')
import loadceleba

'''
   Builds the computational graph
'''
def build_graph(info):

   batch_size = info['batch_size']
   dataset    = info['dataset']
   load       = info['load']

   # load celeba data
   if dataset == 'celeba':
      image_data = loadceleba.load(load=True)

   train(image_data, batch_size)

def train(image_data, batch_size):
   num_critic  = 5
   clip_values = [-0.01, 0.01]
      
   global_step = tf.Variable(0, name='global_step', trainable=False)
   real_images = tf.placeholder(tf.float32, shape=(batch_size, 64, 64, 3), name='color_images')
   z           = tf.placeholder(tf.float32, shape=(batch_size, 100), name='z')

   # generated images
   gen_images = netG(z, batch_size)
  
   errD_real = netD(real_images, batch_size)
   errD_fake = netD(gen_images, batch_size, reuse=True)

   errD = tf.reduce_mean(errD_real - errD_fake)
   errG = tf.reduce_mean(errD_fake)

   tf.summary.scalar('d_loss', errD)
   #tf.summary.scalar('d_loss_real', errD_real)
   #tf.summary.scalar('d_loss_gen', errD_fake)
   tf.summary.scalar('g_loss', errG)
   tf.summary.image('real_images', real_images, max_outputs=20)
   tf.summary.image('generated_images', gen_images, max_outputs=20)
   merged_summary_op = tf.summary.merge_all()
   
   t_vars = tf.trainable_variables()
   d_vars = [var for var in t_vars if 'd_' in var.name]
   g_vars = [var for var in t_vars if 'g_' in var.name]

   # clip values
   clip_discriminator_var_op = [var.assign(tf.clip_by_value(var, clip_values[0], clip_values[1])) for
      var in d_vars]

   G_train_op = tf.train.RMSPropOptimizer(learning_rate=0.00005).minimize(errG, var_list=g_vars, global_step=global_step)
   D_train_op = tf.train.RMSPropOptimizer(learning_rate=0.00005).minimize(errD, var_list=d_vars, global_step=global_step)
   
   gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.5)
   init      = tf.global_variables_initializer()
   sess      = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options))
   #sess = tf.Session()
   sess.run(init)

   summary_writer = tf.summary.FileWriter(checkpoint_dir+'logs/', graph=tf.get_default_graph())
   
   saver = tf.train.Saver(max_to_keep=1)
   ckpt = tf.train.get_checkpoint_state(checkpoint_dir+'celeba/')
   if ckpt and ckpt.model_checkpoint_path:
      print "Restoring previous model..."
      try:
         saver.restore(sess, ckpt.model_checkpoint_path)
         print "Model restored"
      except:
         print "Could not restore model"
         pass
   
   step = sess.run(global_step)
   while True:

      # get the discriminator properly trained at the start
      if step < 25 or step % 500 == 0:
         n_critic = 100
      else: n_critic = 5

      # train the discriminator for 5 or 25 runs
      for critic_itr in range(n_critic):
         batch_real_images = random.sample(image_data, batch_size)
         batch_z = np.random.uniform(-1.0, 1.0, size=[batch_size, 100]).astype(np.float32)
         sess.run(D_train_op, feed_dict={real_images:batch_real_images, z:batch_z})
         sess.run(clip_discriminator_var_op)

      # now train the generator once!
      batch_z = np.random.uniform(-1.0, 1.0, size=[batch_size, 100]).astype(np.float32)
      sess.run(G_train_op, feed_dict={z:batch_z})


      if step % 10 == 0:
         # now get all losses and summary *without* performing a training step - for tensorboard
         D_loss, D_loss_real, D_loss_fake, G_loss, summary = sess.run([errD, errD_real, errD_fake, errG, merged_summary_op], feed_dict={real_images:batch_real_images, z:batch_z})
         print 'Step:',step,'D_loss:',D_loss,'G_loss:',G_loss
      step += 1

      summary_writer.add_summary(summary, step)
      
      if step%500 == 0:
         print 'Saving model...'
         saver.save(sess, checkpoint_dir+dataset+'/checkpoint-'+str(step), global_step=global_step)
      
         batch_z = np.random.uniform(-1.0, 1.0, size=[batch_size, 100]).astype(np.float32)
         gen_imgs = sess.run([gen_images], feed_dict={z:batch_z})

         num = 0
         for img in gen_imgs[0]:
            img = np.asarray(img)
            img = (img+1.)/2.
            img *= 255.0/img.max()
            cv2.imwrite('images/celeba/step_'+str(step)+'_'+str(num)+'.png', img)
            num += 1
            if num == 10:
               #os.sys('cp images/celeba/step_'+str(step)+'_'+str(num)+'.png gitimgs/img.png',)
               #os.sys('git add -f gitimgs/img.png; git commit -m \'added image\'; git push')
               break

if __name__ == '__main__':

   # this loads a config file like: import config_name
   try:
      config_file = ntpath.basename(sys.argv[1]).split('.py')[0]
      config = __import__(config_file)
      print '\nsuccessfully imported',config_file
   except:
      print 'config',sys.argv[1],'not found'
      print
      raise
      exit()

   # set up params from config
   checkpoint_dir = config.checkpoint_dir
   learning_rate  = config.learning_rate
   batch_size     = config.batch_size
   dataset        = config.dataset
   task           = config.task
   load           = config.load
   if checkpoint_dir[-1] is not '/': checkpoint_dir+='/'

   try: os.mkdir(checkpoint_dir)
   except: pass

   info = dict()
   info['checkpoint_dir'] = checkpoint_dir
   info['learning_rate']  = learning_rate
   info['batch_size']     = batch_size
   info['dataset']        = dataset
   info['task']           = task
   info['load']           = load

   print
   print 'checkpoint_dir:',checkpoint_dir
   print 'learning_rate: ',learning_rate
   print 'batch_size:    ',batch_size
   print 'dataset:       ',dataset
   print 'task:          ',task
   print 'load:          ',load
   print
   
   # build the graph - placeholders, loss functions, etc, then call train.
   build_graph(info)






