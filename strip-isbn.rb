#!/usr/bin/env ruby
# Dumps out only the ISBN field from the CSV file produced by by the Android
# app, ZXing Barcode Scanner.
#
# Sample usage: strip-isbn.rb history-*.csv > isbn.txt

require "csv"

ARGV.each do |argv|
	CSV.open argv, 'r' do |row|
		# The CSV field information were taken from
		#   zxing\android\src\com\google\zxing\client\android\history\HistoryManager.java
		#   buildHistory()
		# The following is a listing of each of the fields:
		#   Raw text
		#   Display text
		#   Format (e.g. QR_CODE)
		#   Timestamp
		#   Formatted version of timestamp

		text   = row[1]
		format = row[2]

		# TODO: Convert UPC to ISBN -- yuck!

		if format.match(/^EAN/) and text.match(/^978/)
			puts text
		end
	end
end
