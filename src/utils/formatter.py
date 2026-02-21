import datetime
from decimal import Decimal


def format_rows(stats: list):
    for record in stats:
        record_dict = dict(record)
        for key, value in record_dict.items():
            if isinstance(value, Decimal):
                record_dict[key] = float(value)
            
            if isinstance(value, datetime.datetime):
                record_dict[key] = value.isoformat(timespec="seconds")
        
        yield record_dict