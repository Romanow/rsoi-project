import sys
from typing import Dict

sys.path.append("..")
sys.path.append("../common")
sys.path.append("../search_service")
sys.path.append("search_service")

from qr_server.dict_parsing import *
from qr_server.dto_converter import *
from search.dtos import AuthorPreviewDTO, SeriesPreviewDTO, BookPreviewDTO


@dataclass
class ID_DTO(QRDTO):
    id: int
    entity_type: str

class RecentViewedIDSDTO(ArrayQRDTO(ID_DTO)):
    pass


@dataclass
class Event(QRDTO):
    event: int
    data: List[Dict]


class EventsInIntervalDTO(ArrayQRDTO(Event)):
    pass