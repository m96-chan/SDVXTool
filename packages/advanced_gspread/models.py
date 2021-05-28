from functools import cached_property
from typing import Optional

from gspread import Spreadsheet, WorksheetNotFound
from gspread.utils import finditem


class AdvancedSpreadsheetReader:

    def __init__(self, spread_sheet: Spreadsheet):
        self._client = spread_sheet.client
        self._spread_sheet = spread_sheet
        self._sheet_data = None

    @property
    def sheet_data(self):
        if not self._sheet_data:
            self._sheet_data = self._spread_sheet.fetch_sheet_metadata({'includeGridData': 'true'})
        return self._sheet_data

    def get_worksheet(self, index: int):
        try:
            return AdvancedReadOnlyWorkSheet(self, self.sheet_data['sheets'][index])
        except (KeyError, IndexError):
            return None

    def worksheet(self, title: str):
        try:
            return AdvancedReadOnlyWorkSheet(self, finditem(
                lambda x: x['properties']['title'] == title,
                self.sheet_data['sheets'],
            ))
        except (StopIteration, KeyError):
            raise WorksheetNotFound(title)


class AdvancedReadOnlyWorkSheet:
    def __init__(self, spread_sheet: AdvancedSpreadsheetReader, worksheet):
        self._spread_sheet = spread_sheet
        self._properties = worksheet['properties']
        [self._data] = worksheet['data']

    def __repr__(self):
        return '<%s %s id:%s>' % (
            self.__class__.__name__,
            repr(self.title),
            self.id,
        )

    @property
    def id(self):
        """Worksheet ID."""
        return self._properties['sheetId']

    @property
    def title(self):
        """Worksheet title."""
        return self._properties['title']

    @property
    def row_count(self):
        """Number of rows."""
        return self._properties['gridProperties']['rowCount']

    @property
    def col_count(self):
        """Number of columns."""
        return self._properties['gridProperties']['columnCount']

    @property
    def exist_row_count(self):
        """データが存在するRowカウント"""
        return len(self._data['rowData'])

    @cached_property
    def exist_col_count(self):
        return max(len(r.get('values', [])) for r in self._data['rowData'])

    @property
    def frozen_row_count(self):
        """Number of frozen rows."""
        return self._properties['gridProperties'].get('frozenRowCount', 0)

    @property
    def frozen_col_count(self):
        """Number of frozen columns."""
        return self._properties['gridProperties'].get('frozenColumnCount', 0)

    def row_iter(self, row: int):
        for col_index in range(self.exist_col_count):
            yield self.cell(row, col_index + 1)

    def col_iter(self, col: int):
        for row_index in range(self.exist_row_count):
            yield self.cell(row_index + 1, col)

    def cell(self, row: int, col: int):
        try:
            raw_data = self._data['rowData'][row - 1]['values'][col - 1]
            return AdvancedReadOnlyCell(row, col, raw_data)
        except (KeyError, IndexError):
            return AdvancedReadOnlyCell.empty(row, col)


class AdvancedReadOnlyCell:

    @classmethod
    def empty(cls, row: int, col: int):
        return cls(row, col, {})

    def __init__(self, row, col, raw_data):
        self._raw_data = raw_data
        self._row = row
        self._col = col

    @property
    def row(self):
        """Row number of the cell."""
        return self._row

    @property
    def col(self):
        """Column number of the cell."""
        return self._col

    @property
    def value(self):
        return self._raw_data.get('formattedValue')

    @property
    def numeric_value(self):
        try:
            return float(self.value)
        except ValueError:
            return None

    @property
    def background_color(self):
        # 実際にあたってる方
        return RGB(self._raw_data.get('effectiveFormat', {}).get('backgroundColor', {}))

    @property
    def borders(self):
        return self._raw_data.get('effectiveFormat', {}).get('borders', {})

    @property
    def horizontal_alignment(self):
        return self._raw_data.get('effectiveFormat', {}).get('horizontalAlignment', 'LEFT')

    @property
    def vertical_alignment(self):
        return self._raw_data.get('effectiveFormat', {}).get('verticalAlignment', 'LEFT')


class RGB:
    def __init__(self, rgb: dict):
        self._raw = rgb

    def __eq__(self, other):
        if isinstance(other, RGB):
            return other.red == self.red and other.blue == self.blue and other.green == self.green
        return False

    @property
    def red(self):
        return self._raw.get('red', 1)

    @property
    def green(self):
        return self._raw.get('green', 1)

    @property
    def blue(self):
        return self._raw.get('blue', 1)

