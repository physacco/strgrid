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

class Entry(object):
    """Object that can be rendered as a cell in the grid

    >>> entry = Entry("foo")
    >>> entry = Entry("foo", align="center")
    >>> entry = Entry(12345, align="right", width="10")

    Instance attributes:
      repr: the string to be displayed in a cell
      align: 'left', 'right' or 'center'
      width: effective width of repr (useful to unicode)
    """
    def __init__(self, repr='', align='left', width=None):
        """Create an instance of Entry

        Exceptions: TypeError, ValueError
        """
        if repr and type(repr) is not str:
            raise TypeError('type of repr must be str')
        if align not in ['left', 'right', 'center']:
            raise ValueError('align should be left, right or center')
        if width and type(width) not in [int, long]:
            raise TypeError('width must be an integer')

        self.repr = repr
        self.align = align
        self.width = width or len(repr)

    def __repr__(self):
        """Show Entry instances in an intuitive style"""
        return '<strgrid.Entry repr=%r, align=%r, width=%r>' % \
               (self.repr, self.align, self.width)

class StringGrid(object):
    """String grid formatter

    >>> array2d = [[Entry(), ...], [Entry(), ...]]
    >>> grid = StringGrid(array2d)
    >>> print grid.render()

    Instance attributes:
      array2d: the 2-D array of Entry objects
      row_count: horizontal dimension of the grid
      column_count: vertical dimension of the grid
      column_widths: widths of each column in the grid
    """
    def __init__(self, array2d):
        """Create an instance of StringGrid

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
        """Renderer for each row"""
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
        """Renderer for each cell"""
        entry = self.array2d[i][j]
        column_width = self.column_widths[j]
        spaces = column_width - entry.width

        if entry.align == 'left':
            cont = entry.repr + ' ' * spaces
        elif entry.align == 'right':
            cont = ' ' * spaces + entry.repr
        else:
            if spaces % 2 == 0:
                half = spaces / 2
                cont = ' ' * half + entry.repr + ' ' * half
            else:
                pref = (spaces - 1) / 2
                post = spaces - pref
                cont = ' ' * pref + entry.repr + ' ' * post

        return ' %s ' % cont

    def extractStrings(self):
        """Extract strings in self.array2d"""
        def extractRow(row):
            return [entry.repr for entry in row]
        return [extractRow(row) for row in self.array2d]

    @classmethod
    def renderHorizontalSplitter(klass, column_widths):
        """Renderer for horizontal splitter

        Sample Output:
        +---+------+------+------+------+------+------+---+
        """
        return '+%s+' % '+'.join(['-'*(i+2) for i in column_widths])

def test():
    """Usage example

    It should output the following:
    +--------+------------------+-----------------+
    | hello  |                  |      world      |
    +--------+------------------+-----------------+
    | 女神様 | 綾波 レイ        |                 |
    |     -3 | 3141592653589793 | Fate/Round Face |
    +--------+------------------+-----------------+
    """
    array2d = [[Entry('hello'), Entry(''), Entry('world', 'center')],
               [Entry('女神様', width=6), Entry(u'綾波 レイ'.encode('utf-8'), width=9)],
               [Entry(str(-3), align='right'), Entry(str(3141592653589793), align='right'), Entry('Fate/Round Face')]]
    grid = StringGrid(array2d)
    print grid.render()

if __name__ == '__main__':
    test()
