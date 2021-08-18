from collections import namedtuple

from db.models import Transaction, User, Utils

from tortoise.functions import Sum, Avg
from tortoise.query_utils import Q

import datetime


Data = namedtuple('Data', 'total_incomes total_outcomes average_income_list average_outcome_list')


async def get_total_statistic(user_id: int) -> namedtuple:
    user = await User.get(user_id=user_id)
    total_incomes = await Transaction.all().annotate(total_sum=Sum('amount', _filter=Q(user=user,
                                                                                       type=True))). \
        values('total_sum')
    total_outcomes = await Transaction.all().annotate(total_sum=Sum('amount', _filter=Q(user=user,
                                                                                        type=False))). \
        values('total_sum')
    average_income_list = await Transaction.all().annotate(avg=Avg('amount', _filter=Q(user=user,
                                                                                       type=True))). \
        values('avg')
    average_outcome_list = await Transaction.all().annotate(avg=Avg('amount', _filter=Q(user=user,
                                                                                        type=False))). \
        values('avg')
    return Data(total_incomes, total_outcomes, average_income_list, average_outcome_list)


async def get_last_7_days(user_id: int) -> namedtuple:
    user = await User.get(user_id=user_id)
    today = datetime.datetime.now()
    week_ago = today - datetime.timedelta(days=7)
    incomes_list = await Transaction.all().annotate(total_sum=Sum('amount',
                                                                  _filter=Q(user=user,
                                                                            created__gte=week_ago,
                                                                            type=True))).values('total_sum')
    outcomes_list = await Transaction.all().annotate(total_sum=Sum('amount',
                                                                   _filter=Q(user=user,
                                                                             created__gte=week_ago,
                                                                             type=False))).values('total_sum')
    average_income_list = await Transaction.all().annotate(avg=Avg('amount',
                                                                   _filter=Q(user=user,
                                                                             created__gte=week_ago,
                                                                             type=True))).values('avg')
    average_outcome_list = await Transaction.all().annotate(avg=Avg('amount',
                                                                    _filter=Q(user=user,
                                                                              created__gte=week_ago,
                                                                              type=False))).values('avg')
    return Data(incomes_list, outcomes_list, average_income_list, average_outcome_list)


async def month_statistic(user_id: int, last_month: bool = False) -> namedtuple:
    user = await User.get(user_id=user_id)
    now = datetime.datetime.now()
    if last_month:
        month = now.month - 1 if now.month > 1 else 12
    else:
        month = now.month
    incomes_list = await Transaction.all().annotate(total_sum=Sum('amount',
                                                                  _filter=Q(user=user,
                                                                            created__month=month,
                                                                            type=True))).values('total_sum')
    outcomes_list = await Transaction.all().annotate(total_sum=Sum('amount',
                                                                   _filter=Q(user=user,
                                                                             created__month=month,
                                                                             type=False))).values('total_sum')
    average_income_list = await Transaction.all().annotate(avg=Avg('amount',
                                                                   _filter=Q(user=user,
                                                                             created__month=month,
                                                                             type=True))).values('avg')
    average_outcome_list = await Transaction.all().annotate(avg=Avg('amount',
                                                                    _filter=Q(user=user,
                                                                              created__month=month,
                                                                              type=False))).values('avg')
    return Data(incomes_list, outcomes_list, average_income_list, average_outcome_list)


async def year_statistic(user_id: int, last_year: bool = False) -> namedtuple:
    user = await User.get(user_id=user_id)
    now = datetime.datetime.now()
    if last_year:
        year = now.year - 1
    else:
        year = now.year
    incomes_list = await Transaction.all().annotate(total_sum=Sum('amount',
                                                                  _filter=Q(user=user,
                                                                            created__year=year,
                                                                            type=True))).values('total_sum')
    outcomes_list = await Transaction.all().annotate(total_sum=Sum('amount',
                                                                   _filter=Q(user=user,
                                                                             created__year=year,
                                                                             type=False))).values('total_sum')
    average_income_list = await Transaction.all().annotate(avg=Avg('amount',
                                                                   _filter=Q(user=user,
                                                                             created__year=year,
                                                                             type=True))).values('avg')
    average_outcome_list = await Transaction.all().annotate(avg=Avg('amount',
                                                                    _filter=Q(user=user,
                                                                              created__year=year,
                                                                              type=False))).values('avg')
    return Data(incomes_list, outcomes_list, average_income_list, average_outcome_list)


async def process_statistic(data: Data) -> str:
    utils = await Utils.load()
    incomes = (data.total_incomes[0].get('total_sum') or 0) if data.total_incomes else 0
    outcomes = (data.total_outcomes[0].get('total_sum') or 0) if data.total_outcomes else 0
    average_income = round(data.average_income_list[0].get('avg') or 0) if data.average_income_list else 0
    average_outcome = round(data.average_outcome_list[0].get('avg') or 0) if data.average_outcome_list else 0
    balance = incomes - outcomes
    text = f'<b>Total income:</b> {incomes}\n' + \
           f'<b>Total outcome:</b> {outcomes}\n' + \
           f'<b>Average income:</b> {average_income}\n' + \
           f'<b>Average outcome:</b> {average_outcome}\n' + \
           f'<b>Total balance: </b> {balance}\n' + \
           f'<b>Currency: </b> {utils.default_currency}'
    return text
