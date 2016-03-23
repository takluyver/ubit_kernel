from ipykernel.kernelapp import IPKernelApp
from .kernel import MicrobitKernel

IPKernelApp.launch_instance(kernel_class=MicrobitKernel)
