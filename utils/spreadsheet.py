import xlwt


from db.models import Transaction, Utils


class TransactionSpreadSheet:
    def __init__(self):
        self.model = Transaction
        self.wb = None
        self.ws = None
        self._create_new_file()

    def _create_new_file(self):
        self.wb = xlwt.Workbook(encoding='utf-8')
        self.ws = self.wb.add_sheet(self.model.__name__)

    async def check_for_none(self, value):
        if value == 'None':
            return ''
        return value

    async def create_spreadsheet(self, queryset: list[Transaction]):
        font_style = xlwt.XFStyle()
        font_style.font.bold = True
        self.ws.write(0, 0, '#', font_style)
        self.ws.write(0, 1, 'Date', font_style)
        self.ws.write(0, 3, 'Type', font_style)
        self.ws.write(0, 5, 'Category', font_style)
        self.ws.write(0, 10, 'Sum', font_style)
        self.ws.write(0, 11, 'Currency', font_style)
        self.ws.write(0, 13, 'Field', font_style)
        self.ws.write(0, 15, 'Tax', font_style)
        self.ws.write(0, 16, 'Tax Sum', font_style)

        font_style = xlwt.XFStyle()
        row_num = 0
        utils = await Utils.load()
        for row_data in queryset:
            await row_data.fetch_related('category', 'row', 'taxes')
            row_num += 1
            trans_type = 'Income' if row_data.type else 'Outcome'
            self.ws.write(row_num, 0, row_data.number, font_style)
            self.ws.write(row_num, 1, row_data.created.strftime('%Y-%m-%d'), font_style)
            self.ws.write(row_num, 3, trans_type, font_style)
            self.ws.write(row_num, 5, row_data.category.name, font_style)
            self.ws.write(row_num, 10, row_data.amount, font_style)
            self.ws.write(row_num, 11, utils.default_currency, font_style)
            self.ws.write(row_num, 13, row_data.row.name, font_style)
            self.ws.write(row_num, 15, row_data.taxes.percent, font_style)
            self.ws.write(row_num, 16, row_data.taxes.sum, font_style)
        return self.wb
