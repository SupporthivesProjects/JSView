from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError

from rest_framework import status
from rest_framework.test import APITestCase

from master.models import FinishType

from costcard.models import (
    StonePlace,
    CostCard,
    CostCardDiamondLine,
    CostCardColorStoneLine,
    CostCardFinishLine,
)

User = get_user_model()


def make_cost_card(**overrides):
    data = {
        'our_style_no': 'STY-0001',
        'karat': '18KT',
        'metal_grams': Decimal('5.500'),
    }
    data.update(overrides)
    return CostCard.objects.create(**data)


class StonePlaceModelTest(TestCase):

    def setUp(self):
        self.stone_place = StonePlace.objects.create(
            name='Center',
            description='Center stone placement',
        )

    def test_str_returns_name(self):
        self.assertEqual(str(self.stone_place), 'Center')

    def test_defaults(self):
        self.assertTrue(self.stone_place.active)

    def test_name_is_unique(self):
        with self.assertRaises(IntegrityError):
            StonePlace.objects.create(name='Center')


class CostCardModelTest(TestCase):

    def test_cost_card_no_auto_generated_on_first_save(self):
        card = make_cost_card()
        self.assertEqual(card.cost_card_no, 'CC000001')

    def test_cost_card_no_increments(self):
        first = make_cost_card(our_style_no='STY-0001')
        second = make_cost_card(our_style_no='STY-0002')
        self.assertEqual(first.cost_card_no, 'CC000001')
        self.assertEqual(second.cost_card_no, 'CC000002')

    def test_cost_card_no_not_overwritten_on_update(self):
        card = make_cost_card()
        original_no = card.cost_card_no
        card.our_style_no = 'STY-9999'
        card.save()
        card.refresh_from_db()
        self.assertEqual(card.cost_card_no, original_no)

    def test_str_representation(self):
        card = make_cost_card()
        self.assertEqual(str(card), f'{card.cost_card_no} - {card.our_style_no}')

    def test_default_numeric_fields(self):
        card = make_cost_card()
        self.assertEqual(card.dia_pcs, 0)
        self.assertEqual(card.dia_amount, Decimal('0'))
        self.assertEqual(card.final_amount, Decimal('0'))
        self.assertTrue(card.active)

    def test_parent_relationship(self):
        parent = make_cost_card(our_style_no='STY-PARENT')
        child = make_cost_card(our_style_no='STY-CHILD', parent=parent)
        self.assertEqual(child.parent, parent)
        self.assertIn(child, parent.child_cards.all())


class CostCardStoneLineTest(TestCase):

    def setUp(self):
        self.card = make_cost_card()

    def test_create_diamond_line(self):
        line = CostCardDiamondLine.objects.create(
            cost_card=self.card,
            pcs=2,
            cts=Decimal('0.5000'),
            rate=Decimal('100.0000'),
            amount=Decimal('50.00'),
        )
        self.assertEqual(line.cost_card, self.card)
        self.assertEqual(line.pc, 'C')
        self.assertTrue(line.default_rate)
        self.assertIn(line, self.card.diamond_lines.all())

    def test_diamond_line_str(self):
        line = CostCardDiamondLine.objects.create(cost_card=self.card, pcs=1)
        self.assertEqual(str(line), f'{self.card.cost_card_no} - None')

    def test_create_colorstone_line(self):
        line = CostCardColorStoneLine.objects.create(
            cost_card=self.card,
            pcs=3,
            cts=Decimal('1.2000'),
        )
        self.assertEqual(line.cost_card, self.card)
        self.assertIn(line, self.card.colorstone_lines.all())

    def test_diamond_line_deleted_when_cost_card_deleted(self):
        line = CostCardDiamondLine.objects.create(cost_card=self.card, pcs=1)
        line_pk = line.pk
        self.card.delete()
        self.assertFalse(CostCardDiamondLine.objects.filter(pk=line_pk).exists())


class CostCardFinishLineTest(TestCase):

    def setUp(self):
        self.card = make_cost_card()
        self.finish_type = FinishType.objects.create(name='Rhodium Plating')

    def test_create_finish_line(self):
        line = CostCardFinishLine.objects.create(
            cost_card=self.card,
            finish_type=self.finish_type,
            rate=Decimal('25.00'),
        )
        self.assertEqual(line.cost_card, self.card)
        self.assertEqual(line.finish_type, self.finish_type)
        self.assertIn(line, self.card.finish_lines.all())

    def test_finish_line_str(self):
        line = CostCardFinishLine.objects.create(
            cost_card=self.card,
            finish_type=self.finish_type,
        )
        self.assertEqual(str(line), f'{self.card.cost_card_no} - {self.finish_type}')

    def test_unique_cost_card_finish_type_constraint(self):
        CostCardFinishLine.objects.create(
            cost_card=self.card,
            finish_type=self.finish_type,
        )
        with self.assertRaises(IntegrityError):
            CostCardFinishLine.objects.create(
                cost_card=self.card,
                finish_type=self.finish_type,
            )


class StonePlaceAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='password123',
        )
        self.client.force_authenticate(user=self.user)
        self.stone_place = StonePlace.objects.create(name='Halo')

    def test_list_stone_places(self):
        url = reverse('api-stone-place-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_stone_place(self):
        url = reverse('api-stone-place-list')
        payload = {'name': 'Side', 'description': 'Side stones'}
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(StonePlace.objects.filter(name='Side').exists())

    def test_retrieve_stone_place(self):
        url = reverse('api-stone-place-detail', kwargs={'pk': self.stone_place.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Halo')

    def test_update_stone_place(self):
        url = reverse('api-stone-place-detail', kwargs={'pk': self.stone_place.pk})
        response = self.client.patch(url, {'description': 'Updated'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.stone_place.refresh_from_db()
        self.assertEqual(self.stone_place.description, 'Updated')

    def test_delete_stone_place(self):
        url = reverse('api-stone-place-detail', kwargs={'pk': self.stone_place.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(StonePlace.objects.filter(pk=self.stone_place.pk).exists())


class CostCardAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin2', email='admin2@example.com', password='password123',
        )
        self.client.force_authenticate(user=self.user)
        self.card = make_cost_card()

    def test_list_cost_cards(self):
        url = reverse('api-cost-card-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_cost_card(self):
        url = reverse('api-cost-card-list')
        payload = {
            'our_style_no': 'STY-0002',
            'karat': '14KT',
            'metal_grams': '3.250',
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CostCard.objects.filter(our_style_no='STY-0002').exists())

    def test_retrieve_cost_card(self):
        url = reverse('api-cost-card-detail', kwargs={'pk': self.card.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['our_style_no'], self.card.our_style_no)

    def test_update_cost_card(self):
        url = reverse('api-cost-card-detail', kwargs={'pk': self.card.pk})
        response = self.client.patch(url, {'karat': '22KT'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.card.refresh_from_db()
        self.assertEqual(self.card.karat, '22KT')

    def test_delete_cost_card(self):
        url = reverse('api-cost-card-detail', kwargs={'pk': self.card.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CostCard.objects.filter(pk=self.card.pk).exists())

    def test_duplicate_cost_card(self):
        url = reverse('api-cost-card-duplicate', kwargs={'pk': self.card.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('duplicated', response.data)
        new_no = response.data['duplicated']['cost_card_no']
        self.assertNotEqual(new_no, self.card.cost_card_no)


class CostCardLineAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            username='admin3', email='admin3@example.com', password='password123',
        )
        self.client.force_authenticate(user=self.user)
        self.card = make_cost_card()
        self.finish_type = FinishType.objects.create(name='Matte')

    def test_create_diamond_line_via_api(self):
        url = reverse('api-cost-card-diamond-line-list')
        payload = {
            'cost_card': self.card.pk,
            'pcs': 4,
            'cts': '0.8000',
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CostCardDiamondLine.objects.filter(cost_card=self.card).count(), 1)

    def test_create_colorstone_line_via_api(self):
        url = reverse('api-cost-card-colorstone-line-list')
        payload = {
            'cost_card': self.card.pk,
            'pcs': 2,
            'cts': '0.4000',
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CostCardColorStoneLine.objects.filter(cost_card=self.card).count(), 1)

    def test_create_finish_line_via_api(self):
        url = reverse('api-cost-card-finish-line-list')
        payload = {
            'cost_card': self.card.pk,
            'finish_type': self.finish_type.pk,
            'rate': '10.00',
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CostCardFinishLine.objects.filter(cost_card=self.card).count(), 1)

    def test_finish_line_duplicate_via_api_fails(self):
        CostCardFinishLine.objects.create(cost_card=self.card, finish_type=self.finish_type)
        url = reverse('api-cost-card-finish-line-list')
        payload = {
            'cost_card': self.card.pk,
            'finish_type': self.finish_type.pk,
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_diamond_line_via_api(self):
        line = CostCardDiamondLine.objects.create(cost_card=self.card, pcs=1)
        url = reverse('api-cost-card-diamond-line-detail', kwargs={'pk': line.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CostCardDiamondLine.objects.filter(pk=line.pk).exists())