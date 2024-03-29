from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator


class TourInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title: str
    price: float
    start_date: date
    end_date: date

    @field_validator('start_date', 'end_date')
    @classmethod
    def parse_date(cls, value: date | str) -> date:
        if isinstance(value, date):
            return value
        elif isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise ValueError('Invalid date format. Use YYYY-MM-DD.')
        raise ValueError('Invalid data type. Expected a string or a date object.')
