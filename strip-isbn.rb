#!/usr/bin/env ruby
# After I export a CSV file from the Android app, Book Catalogue, I wanted to
# import this list into Google Books.  Unfortunately, Google Books only
# accepts a list of ISBN or ISSN entries, so I made this script to transform
# the original CSV file into just a list of each book's ISBN.
#
# Sample usage: strip-isbn.rb > isbns.txt

require "csv"

isbn_pos = -1

CSV.open('export.csv', 'r') do |row|
	if isbn_pos < 0
		row.each_index do |i|
			isbn_pos = i if row[i] == "isbn"
		end

		break if isbn_pos < 0
		next
	end

	puts row[isbn_pos]
end
