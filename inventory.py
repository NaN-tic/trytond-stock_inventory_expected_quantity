# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from copy import copy
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = ['InventoryLine']
__metaclass__ = PoolMeta


class InventoryLine:
    __name__ = 'stock.inventory.line'

    @staticmethod
    def _compute_expected_quantity(inventory, product, lot=None):
        pool = Pool()
        Inventory = pool.get('stock.inventory')
        Product = pool.get('product.product')
        try:
            Lot = pool.get('stock.lot')
        except KeyError:
            Lot = None
        if not isinstance(inventory, Inventory):
            inventory = Inventory(inventory)

        if not inventory or not inventory.location:
            return 0.0
        with Transaction().set_context(stock_date_end=inventory.date,
                locations=[inventory.location.id]):
            if Lot and lot:
                return Lot(lot).quantity
            elif product:
                return Product(product).quantity
        return 0.0

    @fields.depends('inventory', '_parent_inventory.date',
        '_parent_inventory.location', 'product', 'lot')
    def on_change_with_expected_quantity(self):
        try:
            lot = self.lot
        except AttributeError:
            lot = None
        return self._compute_expected_quantity(self.inventory, self.product,
            lot)

    @classmethod
    def create(cls, vlist):
        for values in vlist:
            if 'expected_quantity' not in values:
                values['expected_quantity'] = cls._compute_expected_quantity(
                    values.get('inventory'), values.get('product'),
                    values.get('lot'))

        return super(InventoryLine, cls).create(vlist)
