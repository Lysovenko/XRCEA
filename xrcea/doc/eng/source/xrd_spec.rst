#############################
XRD file format specification
#############################

XRD file contains representation of a x-ray diffractogram.

========
Overview
========

XRD file
consists of header and two columns, separated by space character. First column
may be angle :math:`2\theta` or :math:`\theta` in degrees, diffractiov vector
:math:`4\pi \sin(\theta)/\lambda`. Second column is observed intensity during
the experiment.

The header lines begin with a #, followed by a variable name that ends by a
colon, followed by the value of the variable.

.. code-block:: text

   #name: Some meaningful sample name
   #sample: powder
   #x_units: 2theta
   #I2: 0.46
   #lambda1: 1.540598
   #lambda2: 1.544426
   5   2
   5.1 3
   5.2 4

==========
Variables:
==========
.. only:: html

   :math:`\require{mediawiki-texvc}`

- **name** name of the sample.
- **contains** elements which sample consists of.
- **density** atomic density in :math:`\AA^{-3}`
- **x_units** units of x axis: 2theta, theta, q
- **lambda1** wavelength in :math:`{\AA}` of the first line
- **lambda2** wavelength in :math:`\AA` of the second line
- **lambda3** wavelength in :math:`\AA` of the third line
- **I2** intensity of the second line as part of the first
- **I3** intensity of the third line as part of the first
- **alpha1** reflection angle of modochromer before inciding beam in degrees
- **alpha2** reflection angle of modochromer before detector in degrees
