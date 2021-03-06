from scipy.signal import iirdesign, freqz
import matplotlib.pyplot as plt
import numpy

FS = 48000.
BANDPASS = 1000.
STOPBAND = 1500.

b, a = iirdesign(wp = BANDPASS/(FS/2), ws = STOPBAND/(FS/2), gpass=0.1, gstop=40)
h, w = freqz(b, a, worN=2000)

f = h * 48000. / (2*numpy.pi)
f[0]=10

fig = plt.figure()
plt.title('Digital filter frequency response')
ax1 = fig.add_subplot(111)


plt.semilogx(f, 20* numpy.log10(numpy.abs(w)),"b", lw=3)
plt.ylabel('Amplitude (dB)', color='b')
plt.xlabel('Frequency (Hz)')
plt.grid()
plt.legend()
plt.savefig('imagen_filtro.png', dpi=100)


       
