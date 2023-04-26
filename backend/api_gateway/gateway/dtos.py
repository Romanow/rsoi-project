import sys
from typing import Dict

from qr_server import ArrayQRDTO, OneOfQRDTO

sys.path.append('..')

from search_service.search.dtos import *
from scout_service.scout.dtos import *

@dataclass
class ErrorDTO(QRDTO):
    message: str


@dataclass
class UserInfoDTO(QRDTO):
    name: str
    last_name: str
    email: str
    login: str
    avatar: str = None


class RecentViewedDTO(EntitiesListDTO):
    pass

@dataclass
class ReportDTO:
    views_cnt: Dict
    downloads_cnt: int
    search_cnt: int
    most_frequent_search: str
    most_frequent_entities:EntitiesListDTO