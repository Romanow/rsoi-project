import sys
from typing import List, Dict
sys.path.append("..")
sys.path.append("../common")

from qr_server.dict_parsing import *
from qr_server.dto_converter import *

def full_parser(d: dict):
    d = parse_dict(d, rename={'book_number': 'book_order'},
                      remove=['created_at', 'updated_at'])

@dataclass
class AuthorLinkDTO(QRDTO):
    id: int
    name: str

@dataclass
class SeriesLinkDTO(QRDTO):
    id: int
    title: str

@dto_kwargs_parser(full_parser)
@dataclass
class AuthorPreviewDTO(QRDTO):
    id: int
    name: str
    photo: str
    type: str = 'author'

@dto_kwargs_parser(full_parser)
@convert_fields({'[]authors': AuthorLinkDTO})
@dataclass
class SeriesPreviewDTO(QRDTO):
    id: int
    title: str
    skin_image: str
    books_count: int
    authors: List[Dict]
    type: str = 'series'

@dto_kwargs_parser(full_parser)
@convert_fields({'[]authors': AuthorLinkDTO, 'series': SeriesLinkDTO})
@dataclass
class BookPreviewDTO(QRDTO):
    id: int
    title: str
    skin_image: str
    authors: List[Dict]
    series: List[Dict] = None
    book_order: int = None
    type: str = 'book'

@dataclass
class BookFileDTO(QRDTO):
    publication_id: int
    file_path: str
    file_type: str


@convert_fields({'[]files': BookFileDTO})
@dataclass
class BookPublicationDTO(QRDTO):
    id: int
    book_id: int
    language_code: str
    isbn: str
    isbn13: str
    publication_year: int
    info: dict
    files: List[Dict]


@dto_kwargs_parser(full_parser)
@convert_fields({
    '[]authors': AuthorLinkDTO,
    'series': SeriesLinkDTO,
    '[]publications': BookPublicationDTO,
                 })
@dataclass
class BookFullDTO(QRDTO):
    id: int
    description: str
    title: str
    skin_image: str
    genres: List[str]
    authors: List[Dict]
    publications: List[Dict]
    series: Dict = None
    book_order: int = None
    type: str = 'book'


@dto_kwargs_parser(full_parser)
@dataclass
class AuthorFullDTO(QRDTO):
    id: int
    description: str
    name: str
    photo: str
    birthdate: str
    country: str
    type: str = 'author'


@dto_kwargs_parser(full_parser)
@convert_fields({'[]authors': AuthorLinkDTO,})
@dataclass
class SeriesFullDTO(QRDTO):
    id: int
    description: str
    title: str
    skin_image: str
    is_finished: str
    books_count: int
    authors: List[Dict]
    type: str = 'series'


class EntitiesListDTO(ArrayQRDTO(OneOfQRDTO(AuthorPreviewDTO, SeriesPreviewDTO, BookPreviewDTO))):
    pass

class SearchMainDTO(EntitiesListDTO):
    pass