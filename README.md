# Colorizing-Images-Using-Adversarial-Networks
Colorizing images using an adversarial network approach.

Basically do what I did with the other colorization thing,
but after it's colorized, send it to the other network along
with the true color image, and have the adversary determine
which one is the true image and which one was colored by the
network.

Instead of using classification error, use the energy function as shown
[here](https://openreview.net/pdf?id=ryh9pmcee)


Useful links:

[Generative Adversarial Networks](https://arxiv.org/pdf/1406.2661v1.pdf)
First paper on GANs

[A Tutorial on Energy-Based Learning](http://yann.lecun.com/exdb/publis/pdf/lecun-06.pdf)

[Loss Functions for Discriminative Training of Energy-Based Models](http://yann.lecun.com/exdb/publis/pdf/lecun-huang-05.pdf)

[Tips and Tricks for Training GANs](https://github.com/soumith/ganhacks)

[NIPS Accepted Papers for the Adversarial Training Workshop](https://sites.google.com/site/nips2016adversarial/home/accepted-papers)

[NIPS Tutorial on GANs](https://arxiv.org/pdf/1701.00160v3.pdf)


