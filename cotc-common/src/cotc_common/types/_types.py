from typing import Any, TypeAlias

JSONObj: TypeAlias = dict[str, Any]
JSONArr: TypeAlias = list[JSONObj]
ServerResponse: TypeAlias = tuple[dict[str, str], int]
