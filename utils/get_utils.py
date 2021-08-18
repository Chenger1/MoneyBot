from aiohttp import ClientSession

from db.models import Utils, Transaction, Tax


currency_url = 'https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?json'

session = ClientSession()


async def get_percentage() -> int:
    utils = await Utils.load()
    return utils.default_percent


async def change_transaction_amount_according_to_currency(user_id: int, old_currency: str):
    utils = await Utils.load()
    async with session.get(currency_url) as resp:
        data = await resp.json()
        current_currency_info = [item for item in data if item.get('cc') == utils.default_currency]
        if old_currency != 'UAH':
            hryvnia_to_old_currency = [item for item in data if item.get('cc') == old_currency]

        transactions = await Transaction.filter(user__user_id=user_id)
        transactions_ids = await Transaction.filter(user__user_id=user_id).values_list('id', flat=True)
        for item in transactions:
            if old_currency == 'UAH':
                item.amount = round(item.amount / int(current_currency_info[0].get('rate', 1)), 2)
            else:
                if utils.default_currency == 'UAH':
                    item.amount = round(item.amount * int(hryvnia_to_old_currency[0].get('rate', 1)), 2)
                else:
                    to_hryvnia = item.amount * int(hryvnia_to_old_currency[0].get('rate', 1))
                    item.amount = round(to_hryvnia / int(current_currency_info[0].get('rate', 1)), 2)
            await item.save()
        taxes = await Tax.filter(transaction__id__in=transactions_ids)
        for item in taxes:
            if old_currency == 'UAH':
                item.sum = round(item.sum / int(current_currency_info[0].get('rate', 1)), 2)
            else:
                if utils.default_currency == 'UAH':
                    item.sum = round(item.amount * int(hryvnia_to_old_currency[0].get('rate', 1)), 2)
                else:
                    to_hryvnia = item.sum * int(hryvnia_to_old_currency[0].get('rate', 1))
                    item.sum = round(to_hryvnia / int(current_currency_info[0].get('rate', 1)), 2)
            await item.save()
