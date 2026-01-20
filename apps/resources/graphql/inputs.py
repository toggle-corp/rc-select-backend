import strawberry


@strawberry.input
class ContactRequestInput:
    name: str
    email: str
    national_society: str
    content: str
    captcha_hashkey: str
    captcha_code: str
