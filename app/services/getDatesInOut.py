from datetime import datetime, timedelta

def getDatesInOut(month=None, year=None):
    # Se os argumentos não foram fornecidos, usar mês e ano atuais
    if month is None:
        month = datetime.now().strftime('%m')
    if year is None:
        year = datetime.now().strftime('%Y')

    # Cria o primeiro dia do mês
    firstDay = datetime(int(year), int(month), 1)

    # Calcula o último dia do mês
    proximo_mes = firstDay.replace(day=28) + timedelta(days=4)
    lastDay = proximo_mes - timedelta(days=proximo_mes.day)

    # Formata as datas para o formato "yyyy-mm-dd"
    firstDay = firstDay.strftime("%Y-%m-%d")
    lastDay = lastDay.strftime("%Y-%m-%d")

    return firstDay, lastDay
