from dataclasses import dataclass
from dataclasses_json import dataclass_json
@dataclass_json
@dataclass
class Data:
    word: str  # ocr 항목
    result: str  # ocr 결과
