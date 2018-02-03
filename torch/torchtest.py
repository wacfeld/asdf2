# where I learn PyTorch stuff

from __future__ import print_function
import torch
from torch.autograd import Variable
import math

x = Variable(torch.rand(1000,1000d),requires_grad=True)
y = x.mean()
print(y.grad_fn,y)
