#!/usr/bin/env ruby

class PageMarker
    include Comparable

    attr_accessor :page, :line

    def initialize(page, line)
        @page, @line = page, line
    end

    def <=>(other)
        cmp = page <=> other.page

        if cmp == 0
            cmp = line <=> other.line
        end

        return cmp
    end

    def to_s
        "#{@page}.#{@line}"
    end
end

class IntervalTree
    include Comparable

    attr_accessor :start, :end, :root, :left, :right

    def initialize(page1, line1, page2, line2)
        @start = PageMarker.new(page1, line1)
        @end   = PageMarker.new(page2, line2)
        @root  = nil
        @left  = nil
        @right = nil

        if @end < @start
            @start, @end = @end, @start
        end
    end

    def <(other)
        @end < other.start
    end

    def >(other)
        @start > other.end
    end

    def include?(other)
        @start <= other.end and other.start <= @end
    end

    def adjust_left(node, curr, left=true)
        return if curr.nil?

        if node.include? curr
            node.start = [ node.start, curr.start ].min

            if not curr.root.nil?
                if left
                    curr.root.left = curr.left
                    curr.left.root = curr.root if not curr.left.nil?

                    adjust_left node, curr.left
                else
                    curr.root.right = curr.left
                    curr.right.root = curr.root if not curr.right.nil?
                    curr            = curr.right

                    adjust_left node, curr.right, false
                end
            else
                # how?
            end
        else
            adjust_left node, curr.right, false
        end
    end

    def adjust_right(node, curr, right=true)
        return if curr.nil?

        if node.include? curr
            node.end = [ node.end, curr.end ].max

            if not curr.root.nil?
                if right
                    curr.root.right = curr.right
                    curr.right.root = curr.root if not curr.right.nil?

                    adjust_right node, curr.right
                else
                    curr.root.left = curr.right
                    curr.left.root = curr.root if not curr.left.nil?

                    adjust_right node, curr.left, false
                end
            else
                # how?
            end
        else
            adjust_right node, curr.left, false
        end
    end

    def adjust(other)
        if other.start < @start
            @start = other.start
            adjust_left self, @left
        end

        if other.end > @end
            @end = other.end
            adjust_right self, @right
        end
    end

    def insert(node)
        if include? node
            adjust node
        elsif node < self
            if @left.nil?
                node.root = self
                @left     = node
            else
                @left << node
            end
        elsif self < node
            if @right.nil?
                node.root = self
                @right    = node
            else
                @right << node
            end
        end
    end

    def to_s
        s = ""
        s << @left.to_s if not @left.nil?
        s << "#{@start}-#{@end} "
        s << @right.to_s if not @right.nil?

        return s
    end

    alias << insert
end

pattern = /(\d+).(\d+)-(\d+).(\d+)/
root    = nil

while line = gets
    line.chomp!
    if md = pattern.match(line)
        node = IntervalTree.new(md[1].to_i, md[2].to_i, md[3].to_i, md[4].to_i)

        if root.nil?
            root = node
        else
            root << node
        end
    end
end

puts root if not root.nil?
