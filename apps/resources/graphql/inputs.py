import strawberry


@strawberry.input
class ContactRequestInput:
    name: str
    email: str
    national_society: str
    content: str
    captcha_hashkey: str
    captcha_code: str


@strawberry.input
class RequestDemoInput:
    name: str
    email: str
    content: str
    national_society: str
    tool: strawberry.ID
    captcha_hashkey: str
    captcha_code: str
