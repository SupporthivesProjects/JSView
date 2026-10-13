from dataclasses import dataclass

REGISTRY = {}


@dataclass
class Built:
    filename: str
    content: bytes
    mimetype: str


def register(cls):
    REGISTRY[cls.key] = cls
    return cls


class BaseAttachment:
    key = ''
    mimetype = ''
    extension = ''

    def filename(self, ctx):
        return f"{self.key}_{ctx['po_number']}.{self.extension}".replace(' ', '_')

    def render(self, ctx) -> bytes:
        raise NotImplementedError

    def build(self, ctx) -> Built:
        return Built(self.filename(ctx), self.render(ctx), self.mimetype)