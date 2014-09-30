# FreqShow main application model/state.
# Author: Tony DiCola (tony@tonydicola.com)
#
# The MIT License (MIT)
#
# Copyright (c) 2014 Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import numpy as np
from rtlsdr import *

import freqshow


class FreqShowModel(object):
	def __init__(self, width, height):
		"""Create main FreqShow application model.  Must provide the width and
		height of the screen in pixels.
		"""
		# Set properties that will be used by views.
		self.width = width
		self.height = height
		self._clear_intensity()
		# Initialize RTL-SDR library.
		self.sdr = RtlSdr()
		self.set_center_freq(90.3)
		self.set_sample_rate(2.4)
		self.set_gain('AUTO')

	def _clear_intensity(self):
		self.min_intensity = None
		self.max_intensity = None
		self.range = None

	def get_center_freq(self):
		"""Return center frequency of tuner in megahertz."""
		return self.sdr.get_center_freq()/1000000.0

	def set_center_freq(self, freq_mhz):
		"""Set tuner center frequency to provided megahertz value."""
		try:
			self.sdr.set_center_freq(freq_mhz*1000000.0)
			self._clear_intensity()
		except IOError:
			# Error setting value, ignore it for now but in the future consider
			# adding an error message dialog.
			pass

	def get_sample_rate(self):
		"""Return sample rate of tuner in megahertz."""
		return self.sdr.get_sample_rate()/1000000.0

	def set_sample_rate(self, sample_rate_mhz):
		"""Set tuner sample rate to provided frequency in megahertz."""
		try:
			self.sdr.set_sample_rate(sample_rate_mhz*1000000.0)
		except IOError:
			# Error setting value, ignore it for now but in the future consider
			# adding an error message dialog.
			pass

	def get_gain(self):
		"""Return gain of tuner.  Can be either the string 'AUTO' or a numeric
		value that is the gain in decibels.
		"""
		if self.auto_gain:
			return 'AUTO'
		else:
			return self.sdr.get_gain()

	def set_gain(self, gain_db):
		"""Set gain of tuner.  Can be the string 'AUTO' for automatic gain
		or a numeric value in decibels for fixed gain.
		"""
		if gain_db == 'AUTO':
			self.sdr.set_manual_gain_enabled(False)
			self.auto_gain = True
			self._clear_intensity()
		else:
			try:
				self.sdr.set_gain(float(gain_db))
				self.auto_gain = False
				self._clear_intensity()
			except IOError:
				# Error setting value, ignore it for now but in the future consider
				# adding an error message dialog.
				pass

	def get_data(self):
		"""Get spectrogram data from the tuner.  Will return width number of
		values which are the intensities of each frequency bucket (i.e. FFT of
		radio samples).
		"""
		# Get width number of raw samples so the number of frequency bins is
		# the same as the display width.
		samples = self.sdr.read_samples(freqshow.SDR_SAMPLE_SIZE)[0:self.width]
		# Run an FFT and take the absolute value to get frequency magnitudes.
		freqs = np.absolute(np.fft.fft(samples))
		# Update model's min and max intensities.
		min_intensity = np.min(freqs)
		max_intensity = np.max(freqs)
		if self.min_intensity is None:
			self.min_intensity = min_intensity
		else:
			self.min_intensity = min(min_intensity, self.min_intensity)
		if self.max_intensity is None:
			self.max_intensity = max_intensity
		else:
			self.max_intensity = max(max_intensity, self.max_intensity)
		self.range = self.max_intensity - self.min_intensity
		# Return frequency intensities.
		return freqs
