#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
ASCII String Grid Formatter

MySQL usually format query result into a table like this:
  +---+------+------+------+------+------+------+---+
  | a | b    | c    | d    | e    | f    | g    | h |
  +---+------+------+------+------+------+------+---+
  | 3 | NULL | NULL | NULL | NULL | NULL | NULL | 0 | 
  | 4 | NULL | NULL | NULL | NULL | NULL | NULL | 0 | 
  | 5 | NULL | NULL |    2 | NULL | NULL | NULL | 0 | 
  | 6 | NULL | NULL |    2 | NULL | NULL | NULL | 0 | 
  +---+------+------+------+------+------+------+---+
"""

import six
from wcwidth import wcswidth

class Entry(object):
    """Object that can be rendered as a cell in the grid

    >>> entry = Entry(u"foo")
    >>> entry = Entry(u"foo", align="center")
    >>> entry = Entry(u"12345", align="right")

    Instance attributes:
      text: the string to be displayed in a cell
      align: 'left', 'right' or 'center'
    """
    def __init__(self, text=None, align='left'):
        """Create an instance of Entry

        Exceptions: TypeError, ValueError
        """
        if text is None:
            text = u''
        else:
            if not isinstance(text, six.text_type):
                raise TypeError('text must be a unicode string')

        if align not in ['left', 'right', 'center']:
            raise ValueError('align should be left, right or center')

        self.text = text
        self.align = align
        self.width = wcswidth(text)

    def __repr__(self):
        """Show Entry instances in an intuitive style"""
        return '<strgrid.Entry text=%r, align=%r>' % \
               (self.text, self.align)

class Grid(object):
    """String grid formatter

    >>> array2d = [[Entry(), ...], [Entry(), ...]]
    >>> grid = Grid(array2d)
    >>> print grid.render()

    Instance attributes:
      array2d: the 2-D array of Entry objects
      row_count: horizontal dimension of the grid
      column_count: vertical dimension of the grid
      column_widths: widths of each column in the grid
    """
    def __init__(self, array2d):
        """Create an instance of Grid

        Exceptions: TypeError, ValueError
        """
        if type(array2d) not in [tuple, list]:
            raise TypeError('array2d must be a tuple or list')

        self.row_count = len(array2d)
        if self.row_count <= 0:
            raise ValueError('array2d cannot be empty')

        self.column_count = 0
        self.column_widths = []

        for i in range(self.row_count):
            row = array2d[i]
            if type(row) not in [tuple, list]:
                raise TypeError('row %d must be a tuple or list' % i)

            size = len(row)
            if size > self.column_count:
                self.column_count = size

            for j in range(size):
                entry = row[j]
                if not isinstance(entry, Entry):
                    raise TypeError('entry (%d, %d) must be an Entry' % (i, j))

                try:
                    if entry.width > self.column_widths[j]:
                        self.column_widths[j] = entry.width
                except IndexError:
                    self.column_widths.append(entry.width)

        if self.column_count <= 0:
            raise ValueError('array2d cannot be empty')

        self.array2d = array2d

    def render(self, output='str'):
        """
        1) draw the 1st horizontal splitter
        2) draw the 1st row
        3) draw the 2nd horizontal splitter
        4) draw the other rows if row_count > 1
        5) draw the 3rd horizontal splitter if row_count > 1
        """
        if output not in ['str', 'list']:
            raise ValueError('output should be list or str')

        rendered_rows = []

        horizontal_splitter = self.renderHorizontalSplitter(self.column_widths)

        # step 1
        rendered_rows.append(horizontal_splitter)

        # step 2
        rendered_rows.append(self.renderRow(0))

        # step 3
        rendered_rows.append(horizontal_splitter)

        if self.row_count > 1:
            # step 4
            for i in range(self.row_count)[1:]:
                rendered_rows.append(self.renderRow(i))

            # step 5
            rendered_rows.append(horizontal_splitter)

        if output == 'str':
            return '\n'.join(rendered_rows)
        else:
            return rendered_rows

    def renderRow(self, index):
        """Render the index-th row"""
        row = self.array2d[index]

        result = ['|']
        for j in range(self.column_count):
            try:
                result.append(self.renderCell(index, j))
            except IndexError:
                result.append(' %s ' % (' ' * self.column_widths[j]))
            result.append('|')

        return ''.join(result)

    def renderCell(self, i, j):
        """Render the cell at row i, column j"""
        entry = self.array2d[i][j]
        column_width = self.column_widths[j]
        spaces = column_width - entry.width

        if entry.align == 'left':
            cont = entry.text + ' ' * spaces
        elif entry.align == 'right':
            cont = ' ' * spaces + entry.text
        else:
            if spaces % 2 == 0:
                half = spaces // 2
                cont = ' ' * half + entry.text + ' ' * half
            else:
                pref = (spaces - 1) // 2
                post = spaces - pref
                cont = ' ' * pref + entry.text + ' ' * post

        return ' %s ' % cont

    def extractStrings(self):
        """Extract strings in self.array2d"""
        def extractRow(row):
            return [entry.text for entry in row]
        return [extractRow(row) for row in self.array2d]

    @staticmethod
    def renderHorizontalSplitter(column_widths):
        """Render the horizontal splitter

        Sample Output:
        +---+------+------+------+------+------+------+---+
        """
        columns = [u'-' * (w + 2) for w in column_widths]
        return u'+%s+' % u'+'.join(columns)

# Shortcuts
E = Entry
G = Grid

def tablize(matrix):
    return G([[E(six.u(c)) for c in r] for r in matrix]).render()

def test():
    """Usage example

    It should output the following:
    +--------+------------------+-----------------+
    | hello  |                  |      world      |
    +--------+------------------+-----------------+
    | 女神様 |    綾波 レイ     |                 |
    |     -3 | 3141592653589793 | Fate/Round Face |
    +--------+------------------+-----------------+
    """
    array2d = [[E(u'hello'), E(u''), E(u'world', 'center')],
               [E(u'女神様'), E(u'綾波 レイ', 'center')],
               [E(u'-3', 'right'), E(u'3141592653589793', 'right'), E(u'Fate/Round Face')]]
    grid = G(array2d)
    print(grid.render())

if __name__ == '__main__':
    test()
