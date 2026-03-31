from apps.resources.models import ContactRequest, RequestDemo


def get_contact_request_email_context(instance: ContactRequest):
    from .serializers import ContactRequestSerializer

    data = dict(ContactRequestSerializer(instance).data)

    return {
        "name": data["name"],
        "email": data["email"],
        "national_society": data["national_society"],
        "content": data["content"],
    }


def get_demo_request_email_context(instance: RequestDemo):
    from .serializers import RequestDemoSerializer

    data = dict(RequestDemoSerializer(instance).data)
    tool_name = instance.tool.name
    return {
        "name": data["name"],
        "email": data["email"],
        "national_society": data["national_society"],
        "content": data["content"],
        "tool": tool_name,
    }
