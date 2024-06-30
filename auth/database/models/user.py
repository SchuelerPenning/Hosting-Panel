from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    username: str
    email: str
    state: str
    firstname: str
    lastname: str
    role: str
    street: str
    number: str  # house number
    postcode: str
    city: str
    country: str
