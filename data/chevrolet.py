from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Data:
    basicPrice: str  # 기본가격
    optionPrice: str  # 옵션가격
    consignmentPrice: str  # 탁송료
    acquisitionTax: str  # 취득세
    bond: str  # 공채
    proof_license: str  # 증지/번호판대
    registrationFee: str  # 등록수수료
    paymentMethod: str  # 결제방식
    downPayment: str  # 계약금
    deliveryFee: str  # 인도금
    total: str  # 총비용
