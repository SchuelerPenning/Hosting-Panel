from dataclasses import dataclass
from datetime import datetime


@dataclass
class Session:
    session_id: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    expires_at: datetime
    session_data: str

    def __eq__(self, other):
        if not isinstance(other, Session):
            return False
        return all(
            (
                self.session_id == other.session_id,
                self.user_id == other.user_id,
                self.session_data == other.session_data
            )
        )
