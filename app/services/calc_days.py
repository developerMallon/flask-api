from datetime import date, timedelta
from calendar import monthrange

def calcDays(month, year, holidays=[]):
    today = date.today()

    first_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    last_date = date(year, month, last_day)

    bDay = 0  # dias úteis no mês
    bDayPassed = 0  # dias úteis passados até a data corrente

    # Converter feriados para objetos date
    holidays = [date(ano, mes, dia) for ano, mes, dia in holidays]

    while first_date <= last_date:
        if first_date.weekday() < 5:
            if first_date not in holidays:
                if first_date < today:
                    bDayPassed += 1
                bDay += 1
        first_date += timedelta(days=1)
    return bDay, bDayPassed

