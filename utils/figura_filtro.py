from scipy.signal import iirdesign, freqz
import matplotlib.pyplot as plt
import numpy

FS = 48000.
BANDPASS = 400.
STOPBAND = 600.

b, a = iirdesign(wp = BANDPASS/FS, ws = STOPBAND/FS, gpass=0.1, gstop=40)
h, w = freqz(b, a, worN=2000)

f = h * 48000. / numpy.pi
f[0]=10

fig = plt.figure()
plt.title('Digital filter frequency response')
ax1 = fig.add_subplot(111)


plt.semilogx(f, 20* numpy.log10(numpy.abs(w)),"b", lw=3)
plt.ylabel('Amplitude (dB)', color='b')
plt.xlabel('Frequency (Hz)')
plt.grid()
plt.legend()
plt.show()


       
