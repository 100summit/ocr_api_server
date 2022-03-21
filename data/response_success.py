from dataclasses import dataclass
from dataclasses_json import dataclass_json
import datetime


@dataclass_json
@dataclass
class Data:
    result: str
    createAt: str
    data: object

    def __post_init__(self):
        if self.result is None:
            self.result = 'success'
        if self.createAt is None:
            self.createAt = str(datetime.datetime.now())
