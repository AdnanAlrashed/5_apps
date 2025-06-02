from os.path import join as opj
from odoo import models, api, exceptions
from odoo.exceptions import UserError
import logging
import os

_logger = logging.getLogger(__name__)
EXPORTS_DIR = '/srv/exports'
class ProductProduct(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'
    @api.model
    def export_stock_level(self, stock_location):
        products = self.with_context(location=stock_location.id).search([])
        products = products.filtered('qty_available')
        fname = opj(EXPORTS_DIR, 'stock_level.txt')
        try:
            with open(fname, 'w') as fobj:
                for prod in products:
                    fobj.write('%s\t%f\n' % (prod.name,
                prod.qty_available))
        except IOError:
            raise exceptions.UserError('unable to save file')
        
    @api.model
    def export_stock_level(self, stock_location):
        _logger.info('Exporting stock level for %s', stock_location.name)

        # التحقق من أن المجلد موجود، وإذا لم يكن موجودًا، إنشاؤه
        if not os.path.exists(EXPORTS_DIR):
            try:
                os.makedirs(EXPORTS_DIR, exist_ok=True)
                _logger.info('Created directory: %s', EXPORTS_DIR)
            except OSError as e:
                _logger.exception('Error creating directory %s: %s', EXPORTS_DIR, str(e))
                raise UserError(_('Unable to create export directory: %s') % EXPORTS_DIR)

        products = self.with_context(location=stock_location.id).search([])
        products = products.filtered('qty_available')

        _logger.debug('%d products in the location', len(products))

        fname = opj(EXPORTS_DIR, 'stock_level.txt')

        try:
            with open(fname, 'w') as fobj:
                for prod in products:
                    fobj.write('%s\t%f\n' % (prod.name, prod.qty_available))
            _logger.info('Stock level exported successfully to %s', fname)
        except IOError as e:
            _logger.exception('Error while writing to %s in %s', 'stock_level.txt', EXPORTS_DIR)
            raise UserError(_('Unable to save file: %s\nError: %s') % (fname, str(e)))