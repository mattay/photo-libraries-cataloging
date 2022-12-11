def original_date(date_time: str) -> object:
    date = '    :  :  '
    if date_time == '-':
        pass
    elif date_time == '    :  :     :  :':
        pass
    elif date_time:
        date = date_time[:10]
    return date

