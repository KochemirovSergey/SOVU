import pytest
from unittest.mock import MagicMock
from services.link_service import LinkService

@pytest.fixture
def link_service():
    return LinkService()

def test_generate_graduate_link_returns_token(monkeypatch, link_service):
    # Подготовка: подменяем внутренние зависимости, если есть
    graduate_id = 123

    # Если метод использует, например, random или uuid, можно замокать их здесь
    # monkeypatch.setattr('services.link_service.uuid4', lambda: 'fixed-uuid')

    result = link_service.generate_graduate_link(graduate_id)

    assert isinstance(result, str)
    assert len(result) > 0