from dataclasses import dataclass


@dataclass
class Data:
    text: str  # ocr 결과
    x1: str  # 좌상단 x
    y1: str  # 좌상단 y
    x2: str  # 좌하단 x
    y2: str  # 좌하단 y
