from enum import Enum


class FileType(Enum):
    """Clase de utilidad para diferenciar el tipo de fichero del conjunto de datos."""
    ARFF = 1
    CSV = 2
