from django.urls import reverse
import pytest
from pytest_django.asserts import assertTemplateUsed


class TestIndexView():
    @pytest.mark.parametrize('page', ['/', reverse('main:index')])
    def test_view_url_exists_at_desired_location(self, page, django_app):
        resp = django_app.get(page)
        assert resp.status_code == 200

    @pytest.mark.parametrize('page', ['/', reverse('main:index')])
    def test_view_uses_correct_template(self, page, django_app):
        resp = django_app.get(page)
        assertTemplateUsed(resp, 'main/index.html')
