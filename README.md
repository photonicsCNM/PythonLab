# PythonLab 
*Automate laboratory tasks with Python*
---
### Modules
- [MyLab](): Python Abstraction layer for interactive device control. 

So far implemented device classes:

 - [MySpectrometer](): *Ocean Optics spectrometers* (based on 
[python-seabreeze](https://github.com/ap--/python-seabreeze)), 
- [MyStage](): *[Micos Corvus Eco](http://micosusa.com/old/Con_o_02.html) Microstep Controller* and 
respective [axes](https://www.physikinstrumente.com/en/products/linear-stages/
stages-with-stepper-dc-brushless-dc-bldc-motors/vt-80-linear-stage-1206300/) 
(inspired by [Micos.py](https://gist.github.com/pklaus/3955382)),
- [GPIO](): Control GPIO pins of [Raspberry Pi]()

.. Then there is some some code for accessing video devices like [USB-cameras]() which might come in handy. 

#### Usage examples
[Jupyter Notebooks]() are implemented for interactive control of the devices: 
- [Spectra Acquisition]()
- [Stage Control]()
- [Camera Control]()
- [Camera & Stage Control]()

For complete automation, check out the related [RPi branch](). 

