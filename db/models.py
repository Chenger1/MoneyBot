from tortoise.models import Model
from tortoise import fields


class Row(Model):
    name = fields.CharField(max_length=50)

    table: fields.ReverseRelation['Table']
    transactions: fields.ReverseRelation['Transaction']

    def __str__(self):
        return self.name


class Table(Model):
    name = fields.CharField(max_length=100)
    rows: fields.ForeignKeyRelation[Row] = fields.ForeignKeyField('models.Row',
                                                                  related_name='table', on_delete=fields.CASCADE)

    def __str__(self):
        return self.name


class Category(Model):
    name = fields.CharField(max_length=50)

    transactions: fields.ReverseRelation['Transaction']

    def __str__(self):
        return self.name


class Transaction(Model):
    number = fields.IntField(null=True)
    type = fields.BooleanField(default=False,
                               description='If "True" - income. If "False" - outcome')
    amount = fields.DecimalField(decimal_places=2, max_digits=19)
    category: fields.ForeignKeyRelation[Category] = fields.ForeignKeyField('models.Category',
                                                                           related_name='transactions',
                                                                           on_delete=fields.CASCADE)
    created = fields.DatetimeField(auto_now_add=True)
    row: fields.ForeignKeyRelation[Row] = fields.ForeignKeyField('models.Row', related_name='row_transactions',
                                                                 on_delete=fields.CASCADE)

    def __str__(self):
        return f'№{self.number}'
