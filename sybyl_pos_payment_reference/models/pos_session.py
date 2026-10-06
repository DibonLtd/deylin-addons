from odoo import models


class PosSessionLoadFields(models.Model):
    """Inherited model pos session for loading field in pos payment into
       pos session.
        Methods:
            _pos_ui_models_to_load(self):
                Supering the method to load model pos payment and res config
                settings into pos session
            _loader_params_res_config_settings(self):
                Loads field is_allow_payment_ref to pos session
            _get_pos_ui_res_config_settings(self, params):
                Load res config settings parameters to pos session
            _loader_params_pos_payment(self):
                Loads field user_payment_reference to pos session
            _get_pos_ui_pos_payment(self, params):
                Load pos payment parameters to pos session."""
    _inherit = 'pos.session'

    def _loader_params_pos_payment_method(self):
        result = super()._loader_params_pos_payment_method()
        result['search_params']['fields'].append('enable_payment_ref')
        result['search_params']['fields'].append('user_payment_reference')
        return result
