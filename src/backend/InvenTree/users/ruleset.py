"""Ruleset definitions which control the InvenTree user permissions."""

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from generic.enums import StringEnum


class RuleSetEnum(StringEnum):
    """Enumeration of ruleset names."""

    ADMIN = 'admin'
    PART_CATEGORY = 'part_category'
    PART = 'part'
    BOM = 'bom'
    STOCK_LOCATION = 'stock_location'
    STOCK = 'stock'
    BUILD = 'build'
    PURCHASE_ORDER = 'purchase_order'
    SALES_ORDER = 'sales_order'
    RETURN_ORDER = 'return_order'
    TRANSFER_ORDER = 'transfer_order'

    COMPANY = 'company'  # kept for backward compatibility (hidden from RULESET_CHOICES)
    CUSTOMER = 'customer'  # Company model, labelled as Customers
    VENDOR = 'vendor'  # Company model, labelled as Vendors
    COMPANY_CONTACT = 'company_contact'
    COMPANY_ADDRESS = 'company_address'

    MASTER_METAL_TYPE = 'master_metal_type'
    MASTER_METAL_PURITY = 'master_metal_purity'
    MASTER_METAL_RATE = 'master_metal_rate'
    MASTER_JEWELRY_CATEGORY = 'master_jewelry_category'
    MASTER_JEWELRY_SUB_CATEGORY = 'master_jewelry_sub_category'
    MASTER_FINDING_TYPE = 'master_finding_type'
    MASTER_FINDING_ITEM = 'master_finding_item'
    MASTER_SETTING = 'master_setting'
    MASTER_LABOUR_SETTING = 'master_labour_setting'
    MASTER_FINISH_TYPE = 'master_finish_type'
    MASTER_DUTY = 'master_duty'
    MASTER_STAMP = 'master_stamp'
    MASTER_AC_EXECUTIVE = 'master_ac_executive'
    MASTER_TERMS = 'master_terms'
    MASTER_COURIER_SERVICE = 'master_courier_service'
    MASTER_PO_MAIL = 'master_po_mail'
    MASTER_TEMPLATES = 'master_templates'

    PROPERTIES_DIAMOND_STONE = 'properties_diamond_stone'
    PROPERTIES_DIAMOND_CUT = 'properties_diamond_cut'
    PROPERTIES_DIAMOND_SHAPE = 'properties_diamond_shape'
    PROPERTIES_DIAMOND_COLOR = 'properties_diamond_color'
    PROPERTIES_DIAMOND_SIZE = 'properties_diamond_size'
    PROPERTIES_DIAMOND_QUALITY = 'properties_diamond_quality'
    PROPERTIES_DIAMOND_STONE_RATE = 'properties_diamond_stone_rate'
    PROPERTIES_COLOR_STONE = 'properties_color_stone'
    PROPERTIES_COLOR_STONE_CUT = 'properties_color_stone_cut'
    PROPERTIES_COLOR_STONE_SHAPE = 'properties_color_stone_shape'
    PROPERTIES_COLOR_STONE_COLOR = 'properties_color_stone_color'
    PROPERTIES_COLOR_STONE_SIZE = 'properties_color_stone_size'
    PROPERTIES_COLOR_STONE_QUALITY = 'properties_color_stone_quality'
    PROPERTIES_COLOR_STONE_RATE = 'properties_color_stone_rate'

    COST_CARD_STONE_PLACE = 'cost_card_stone_place'
    COST_CARD = 'cost_card'
    COST_CARD_DIAMOND_LINE = 'cost_card_diamond_line'
    COST_CARD_COLOR_STONE_LINE = 'cost_card_color_stone_line'
    COST_CARD_FINISH_LINE = 'cost_card_finish_line'
    COST_CARD_VERSION = 'cost_card_version'

    JS_PURCHASE_ORDER = 'js_purchase_order'  # PurchaseOrder model, potype=ORDER
    JS_PURCHASE_ORDER_LINE = 'js_purchase_order_line'
    JS_PURCHASE_REQUEST = 'js_purchase_request'  # PurchaseOrder model, potype=REQUEST
    JS_PURCHASE_REQUEST_LINE = 'js_purchase_request_line'  # PurchaseOrderLine model
    JS_PO_COST_CARD = 'js_po_cost_card'
    JS_PO_COST_CARD_LINE = 'js_po_cost_card_line'

    REQUISITION_FLUTE_ENTRY = 'requisition_flute_entry'
    REQUISITION_FLUTE_ENTRY_LINE = 'requisition_flute_entry_line'
    REQUISITION_METAL_SENT = 'requisition_metal_sent'

    VENDOR_SHIPMENT = 'vendor_shipment'
    VENDOR_SHIPMENT_LINE = 'vendor_shipment_line'

    REPORT = 'report'  # kept for backward compatibility (hidden from RULESET_CHOICES)
    REPORT_OPEN_ORDER = 'report_open_order'
    REPORT_CLOSE_ORDER = 'report_close_order'
    REPORT_INVOICE_VALUE = 'report_invoice_value'
    REPORT_PO_STONE_VALUATION = 'report_po_stone_valuation'
    REPORT_PO_STONE_STATUS = 'report_po_stone_status'
    REPORT_PO_STATUS = 'report_po_status'
    REPORT_BAL_DIA_VENDOR = 'report_bal_dia_vendor'
    REPORT_COST_CARD = 'report_cost_card'


# Ruleset choices shown in the system (used to assign permissions to a group).
# Label format: "Group -> Item". Custom groups first, InvenTree built-ins hidden.
RULESET_CHOICES = [
    # Master -> Parties
    (RuleSetEnum.CUSTOMER, _('Master -> Customers')),
    (RuleSetEnum.VENDOR, _('Master -> Vendors')),
    (RuleSetEnum.COMPANY_CONTACT, _('Master -> Contacts')),
    (RuleSetEnum.MASTER_AC_EXECUTIVE, _('Master -> A/C Executives')),
    # Master -> Metal
    (RuleSetEnum.MASTER_METAL_TYPE, _('Master -> Metal Types')),
    (RuleSetEnum.MASTER_METAL_PURITY, _('Master -> Metal Purities')),
    (RuleSetEnum.MASTER_METAL_RATE, _('Master -> Metal Rates')),
    # Master -> Jewelry
    (RuleSetEnum.MASTER_JEWELRY_CATEGORY, _('Master -> Jewelry Categories')),
    (RuleSetEnum.MASTER_JEWELRY_SUB_CATEGORY, _('Master -> Jewelry Sub Categories')),
    # Master -> Findings
    (RuleSetEnum.MASTER_FINDING_TYPE, _('Master -> Finding Types')),
    (RuleSetEnum.MASTER_FINDING_ITEM, _('Master -> Finding Items')),
    # Master -> Making
    (RuleSetEnum.MASTER_SETTING, _('Master -> Settings')),
    (RuleSetEnum.MASTER_LABOUR_SETTING, _('Master -> Labour Settings')),
    (RuleSetEnum.MASTER_FINISH_TYPE, _('Master -> Finish Types')),
    (RuleSetEnum.MASTER_STAMP, _('Master -> Stamps')),
    # Master -> Commercial
    (RuleSetEnum.MASTER_DUTY, _('Master -> Duties')),
    (RuleSetEnum.MASTER_TERMS, _('Master -> Terms')),
    (RuleSetEnum.MASTER_COURIER_SERVICE, _('Master -> Courier Services')),
    (RuleSetEnum.MASTER_PO_MAIL, _('Master -> P.O. Mails')),
    (RuleSetEnum.MASTER_TEMPLATES, _('Master -> Templates')),

    # Properties -> Diamond
    (RuleSetEnum.PROPERTIES_DIAMOND_STONE, _('Properties -> Diamond Stones')),
    (RuleSetEnum.PROPERTIES_DIAMOND_CUT, _('Properties -> Diamond Cuts')),
    (RuleSetEnum.PROPERTIES_DIAMOND_SHAPE, _('Properties -> Diamond Shapes')),
    (RuleSetEnum.PROPERTIES_DIAMOND_COLOR, _('Properties -> Diamond Colors')),
    (RuleSetEnum.PROPERTIES_DIAMOND_SIZE, _('Properties -> Diamond Sizes')),
    (RuleSetEnum.PROPERTIES_DIAMOND_QUALITY, _('Properties -> Diamond Qualities')),
    (RuleSetEnum.PROPERTIES_DIAMOND_STONE_RATE, _('Properties -> Diamond Stone Rates')),
    # Properties -> Color Stone
    (RuleSetEnum.PROPERTIES_COLOR_STONE, _('Properties -> Color Stones')),
    (RuleSetEnum.PROPERTIES_COLOR_STONE_CUT, _('Properties -> Color Stone Cuts')),
    (RuleSetEnum.PROPERTIES_COLOR_STONE_SHAPE, _('Properties -> Color Stone Shapes')),
    (RuleSetEnum.PROPERTIES_COLOR_STONE_COLOR, _('Properties -> Color Stone Colors')),
    (RuleSetEnum.PROPERTIES_COLOR_STONE_SIZE, _('Properties -> Color Stone Sizes')),
    (RuleSetEnum.PROPERTIES_COLOR_STONE_QUALITY, _('Properties -> Color Stone Qualities')),
    (RuleSetEnum.PROPERTIES_COLOR_STONE_RATE, _('Properties -> Color Stone Rates')),

    # Cost Card
    (RuleSetEnum.COST_CARD, _('Cost Card -> Cost Cards')),
    (RuleSetEnum.COST_CARD_DIAMOND_LINE, _('Cost Card -> Diamonds')),
    (RuleSetEnum.COST_CARD_COLOR_STONE_LINE, _('Cost Card -> Color Stones')),
    (RuleSetEnum.COST_CARD_FINISH_LINE, _('Cost Card -> Finish Types')),
    (RuleSetEnum.COST_CARD_STONE_PLACE, _('Cost Card -> Stone Places')),
    (RuleSetEnum.COST_CARD_VERSION, _('Cost Card -> Versions')),

    # Purchase (same PurchaseOrder model, split into Requests and Orders)
    (RuleSetEnum.JS_PURCHASE_REQUEST, _('Purchase -> Requests')),
    (RuleSetEnum.JS_PURCHASE_REQUEST_LINE, _('Purchase -> Request Items')),
    (RuleSetEnum.JS_PURCHASE_ORDER, _('Purchase -> Orders')),
    (RuleSetEnum.JS_PURCHASE_ORDER_LINE, _('Purchase -> Order Items')),
    (RuleSetEnum.JS_PO_COST_CARD, _('Purchase -> Cost Cards')),
    (RuleSetEnum.JS_PO_COST_CARD_LINE, _('Purchase -> Cost Card Items')),

    # Requisition
    (RuleSetEnum.REQUISITION_FLUTE_ENTRY, _('Requisition -> Flute Entries')),
    (RuleSetEnum.REQUISITION_FLUTE_ENTRY_LINE, _('Requisition -> Flute Entry Items')),
    (RuleSetEnum.REQUISITION_METAL_SENT, _('Requisition -> Metal Sent')),

    # Vendor Shipment
    (RuleSetEnum.VENDOR_SHIPMENT, _('Vendor Shipment -> Shipments')),
    (RuleSetEnum.VENDOR_SHIPMENT_LINE, _('Vendor Shipment -> Shipment Items')),

    # Report (same order as the Reports menu)
    # (RuleSetEnum.REPORT, _('Report -> Reports')),
    (RuleSetEnum.REPORT_OPEN_ORDER, _('Report -> Open Order')),
    (RuleSetEnum.REPORT_CLOSE_ORDER, _('Report -> Close Order')),
    (RuleSetEnum.REPORT_INVOICE_VALUE, _('Report -> Invoice Value P/C')),
    (RuleSetEnum.REPORT_PO_STONE_VALUATION, _('Report -> P.O. Stone Valuation')),
    (RuleSetEnum.REPORT_PO_STONE_STATUS, _('Report -> P.O. Stone Status')),
    (RuleSetEnum.REPORT_PO_STATUS, _('Report -> P.O. Status')),
    (RuleSetEnum.REPORT_BAL_DIA_VENDOR, _('Report -> Balance Dia. With Vendor')),
    (RuleSetEnum.REPORT_COST_CARD, _('Report -> Cost Card Export')),

    # Hidden
    # (RuleSetEnum.COMPANY, _('Master -> Companies')),
    # (RuleSetEnum.ADMIN, _('Admin')),
    # (RuleSetEnum.PURCHASE_ORDER, _('Purchase Orders')),
    # (RuleSetEnum.BOM, _('Bills of Material')),
    # (RuleSetEnum.BUILD, _('Build Orders')),
    # (RuleSetEnum.PART_CATEGORY, _('Part Categories')),
    # (RuleSetEnum.PART, _('Parts')),
    # (RuleSetEnum.RETURN_ORDER, _('Return Orders')),
    # (RuleSetEnum.SALES_ORDER, _('Sales Orders')),
    # (RuleSetEnum.STOCK, _('Stock Items')),
    # (RuleSetEnum.STOCK_LOCATION, _('Stock Locations')),
    # (RuleSetEnum.TRANSFER_ORDER, _('Transfer Orders')),
]

# Ruleset names available in the system.
RULESET_NAMES = [choice[0] for choice in RULESET_CHOICES]

# Permission types available for each ruleset.
RULESET_PERMISSIONS = ['view', 'add', 'change', 'delete']

RULESET_CHANGE_INHERIT = [('part', 'bomitem')]


def get_ruleset_models() -> dict:
    """Return a dictionary of models associated with each ruleset.

    This function maps particular database models to each ruleset.
    """
    ruleset_models = {
        RuleSetEnum.ADMIN: [
            'auth_group',
            'auth_user',
            'auth_permission',
            'users_apitoken',
            'users_ruleset',
            'report_labeltemplate',
            'report_reportasset',
            'report_reportsnippet',
            'report_reporttemplate',
            'account_emailaddress',
            'account_emailconfirmation',
            'socialaccount_socialaccount',
            'socialaccount_socialapp',
            'socialaccount_socialtoken',
            'otp_totp_totpdevice',
            'otp_static_statictoken',
            'otp_static_staticdevice',
            'mfa_authenticator',
            # Oauth
            'oauth2_provider_application',
            'oauth2_provider_grant',
            'oauth2_provider_idtoken',
            'oauth2_provider_accesstoken',
            'oauth2_provider_refreshtoken',
            'oauth2_provider_devicegrant',
            # Plugins
            'plugin_pluginconfig',
            'plugin_pluginsetting',
            'plugin_pluginusersetting',
            # Misc
            'common_barcodescanresult',
            'common_newsfeedentry',
            'taggit_tag',
            'taggit_taggeditem',
            'flags_flagstate',
            'machine_machineconfig',
            'machine_machinesetting',
            # common / comms
            'common_emailmessage',
            'common_emailthread',
            'django_mailbox_mailbox',
            'django_mailbox_messageattachment',
            'django_mailbox_message',
        ],

        RuleSetEnum.BOM: [
            'part_bomitem',
            'part_bomitemsubstitute',
        ],

        RuleSetEnum.BUILD: [
            'part_part',
            'part_partcategory',
            'part_bomitem',
            'part_bomitemsubstitute',
            'build_build',
            'build_builditem',
            'build_buildline',
            'stock_stockitem',
            'stock_stocklocation',
        ],

        RuleSetEnum.PART_CATEGORY: [
            'part_partcategory',
            'part_partcategoryparametertemplate',
            'part_partcategorystar',
        ],

        RuleSetEnum.PART: [
            'part_part',
            'part_partpricing',
            'part_partsellpricebreak',
            'part_partinternalpricebreak',
            'part_parttesttemplate',
            'part_partrelated',
            'part_partstar',
            'part_partstocktake',
            'part_partcategorystar',
            'company_supplierpart',
            'company_manufacturerpart',
        ],

        RuleSetEnum.STOCK_LOCATION: [
            'stock_stocklocation',
            'stock_stocklocationtype',
        ],

        RuleSetEnum.STOCK: [
            'stock_stockitem',
            'stock_stockitemtracking',
            'stock_stockitemtestresult',
        ],

        RuleSetEnum.PURCHASE_ORDER: [
            'company_company',
            'company_contact',
            'company_address',
            'company_manufacturerpart',
            'company_supplierpart',
            'company_supplierpricebreak',
            'order_purchaseorder',
            'order_purchaseorderlineitem',
            'order_purchaseorderextraline',
        ],

        RuleSetEnum.SALES_ORDER: [
            'company_company',
            'company_contact',
            'company_address',
            'order_salesorder',
            'order_salesorderallocation',
            'order_salesorderlineitem',
            'order_salesorderextraline',
            'order_salesordershipment',
        ],

        RuleSetEnum.RETURN_ORDER: [
            'company_company',
            'company_contact',
            'company_address',
            'order_returnorder',
            'order_returnorderlineitem',
            'order_returnorderextraline',
        ],

        RuleSetEnum.TRANSFER_ORDER: [
            'order_transferorder',
            'order_transferorderallocation',
            'order_transferorderlineitem',
        ],

        # Company (same Company model, exposed as Customers and Vendors)
        RuleSetEnum.COMPANY: ['company_company'],  # legacy, hidden from choices
        RuleSetEnum.CUSTOMER: ['company_company'],
        RuleSetEnum.VENDOR: ['company_company'],
        RuleSetEnum.COMPANY_CONTACT: ['company_contact'],
        RuleSetEnum.COMPANY_ADDRESS: ['company_address'],

        # Master
        RuleSetEnum.MASTER_METAL_TYPE: ['master_metaltype'],
        RuleSetEnum.MASTER_METAL_PURITY: ['master_metalpurity'],
        RuleSetEnum.MASTER_METAL_RATE: ['master_metalrate'],
        RuleSetEnum.MASTER_JEWELRY_CATEGORY: ['master_jewelrycategory'],
        RuleSetEnum.MASTER_JEWELRY_SUB_CATEGORY: ['master_jewelrysubcategory'],
        RuleSetEnum.MASTER_FINDING_TYPE: ['master_findingtype'],
        RuleSetEnum.MASTER_FINDING_ITEM: ['master_findingitem'],
        RuleSetEnum.MASTER_SETTING: ['master_setting'],
        RuleSetEnum.MASTER_LABOUR_SETTING: ['master_laboursetting'],
        RuleSetEnum.MASTER_FINISH_TYPE: ['master_finishtype'],
        RuleSetEnum.MASTER_DUTY: ['master_duty'],
        RuleSetEnum.MASTER_STAMP: ['master_stamp'],
        RuleSetEnum.MASTER_AC_EXECUTIVE: ['master_acexecutive'],
        RuleSetEnum.MASTER_TERMS: ['master_terms'],
        RuleSetEnum.MASTER_COURIER_SERVICE: ['master_courierservice'],
        RuleSetEnum.MASTER_PO_MAIL: ['master_pomail'],
        RuleSetEnum.MASTER_TEMPLATES: ['master_templates'],

        # Properties
        RuleSetEnum.PROPERTIES_DIAMOND_STONE: ['properties_diamondstone'],
        RuleSetEnum.PROPERTIES_DIAMOND_CUT: ['properties_diamondcut'],
        RuleSetEnum.PROPERTIES_DIAMOND_SHAPE: ['properties_diamondshape'],
        RuleSetEnum.PROPERTIES_DIAMOND_COLOR: ['properties_diamondcolor'],
        RuleSetEnum.PROPERTIES_DIAMOND_SIZE: ['properties_diamondsize'],
        RuleSetEnum.PROPERTIES_DIAMOND_QUALITY: ['properties_diamondquality'],
        RuleSetEnum.PROPERTIES_DIAMOND_STONE_RATE: ['properties_diamondstonerate'],
        RuleSetEnum.PROPERTIES_COLOR_STONE: ['properties_colorstone'],
        RuleSetEnum.PROPERTIES_COLOR_STONE_CUT: ['properties_colorstonecut'],
        RuleSetEnum.PROPERTIES_COLOR_STONE_SHAPE: ['properties_colorstoneshape'],
        RuleSetEnum.PROPERTIES_COLOR_STONE_COLOR: ['properties_colorstonecolor'],
        RuleSetEnum.PROPERTIES_COLOR_STONE_SIZE: ['properties_colorstonesize'],
        RuleSetEnum.PROPERTIES_COLOR_STONE_QUALITY: ['properties_colorstonequality'],
        RuleSetEnum.PROPERTIES_COLOR_STONE_RATE: ['properties_colorstonerate'],

        # Cost Card
        RuleSetEnum.COST_CARD_STONE_PLACE: ['costcard_stoneplace'],
        RuleSetEnum.COST_CARD: ['costcard_costcard'],
        RuleSetEnum.COST_CARD_DIAMOND_LINE: ['costcard_costcarddiamondline'],
        RuleSetEnum.COST_CARD_COLOR_STONE_LINE: ['costcard_costcardcolorstoneline'],
        RuleSetEnum.COST_CARD_FINISH_LINE: ['costcard_costcardfinishline'],
        RuleSetEnum.COST_CARD_VERSION: ['revision_costcardversion'],

        # Purchase (same PurchaseOrder model, exposed as Requests and Orders)
        RuleSetEnum.JS_PURCHASE_ORDER: ['purchase_order_purchaseorder'],
        RuleSetEnum.JS_PURCHASE_ORDER_LINE: ['purchase_order_purchaseorderline'],
        RuleSetEnum.JS_PURCHASE_REQUEST: ['purchase_order_purchaseorder'],
        RuleSetEnum.JS_PURCHASE_REQUEST_LINE: ['purchase_order_purchaseorderline'],
        RuleSetEnum.JS_PO_COST_CARD: ['purchase_order_pocostcard'],
        RuleSetEnum.JS_PO_COST_CARD_LINE: ['purchase_order_pocostcardline'],

        # Requisition
        RuleSetEnum.REQUISITION_FLUTE_ENTRY: ['requisition_fluteentry'],
        RuleSetEnum.REQUISITION_FLUTE_ENTRY_LINE: ['requisition_fluteentryline'],
        RuleSetEnum.REQUISITION_METAL_SENT: ['requisition_metalsent'],

        # Vendor Shipment
        RuleSetEnum.VENDOR_SHIPMENT: ['vendor_shipment_vendorshipment'],
        RuleSetEnum.VENDOR_SHIPMENT_LINE: ['vendor_shipment_vendorshipmentline'],

        # Report (permission-only models in the jsreport app)
        RuleSetEnum.REPORT: [],  # legacy, hidden from choices
        RuleSetEnum.REPORT_OPEN_ORDER: ['jsreport_openorderreport'],
        RuleSetEnum.REPORT_CLOSE_ORDER: ['jsreport_closeorderreport'],
        RuleSetEnum.REPORT_INVOICE_VALUE: ['jsreport_invoicevaluereport'],
        RuleSetEnum.REPORT_PO_STONE_VALUATION: ['jsreport_postonevaluationreport'],
        RuleSetEnum.REPORT_PO_STONE_STATUS: ['jsreport_postonestatusreport'],
        RuleSetEnum.REPORT_PO_STATUS: ['jsreport_postatusreport'],
        RuleSetEnum.REPORT_BAL_DIA_VENDOR: ['jsreport_balancediavendorreport'],
        RuleSetEnum.REPORT_COST_CARD: ['jsreport_costcardexportreport'],
    }

    if settings.SITE_MULTI:
        ruleset_models['admin'].append('sites_site')

    return ruleset_models


def get_ruleset_ignore() -> list[str]:
    """Return a list of database tables which do not require permissions."""
    return [
        # Core django models (not user configurable)
        'admin_logentry',
        'contenttypes_contenttype',
        # Models which currently do not require permissions
        'common_attachment',
        'common_parametertemplate',
        'common_parameter',
        'common_customunit',
        'common_dataoutput',
        'common_inventreesetting',
        'common_inventreeusersetting',
        'common_notificationentry',
        'common_notificationmessage',
        'common_notesimage',
        'common_projectcode',
        'common_webhookendpoint',
        'common_webhookmessage',
        'common_inventreecustomuserstatemodel',
        'common_selectionlistentry',
        'common_selectionlist',
        'users_owner',
        'users_userprofile',  # User profile is handled in the serializer - only own user can change
        # Third-party tables
        'error_report_error',
        'exchange_rate',
        'exchange_exchangebackend',
        'usersessions_usersession',
        'sessions_session',
        # Django-q
        'django_q_ormq',
        'django_q_failure',
        'django_q_success',
        'django_q_task',
        'django_q_schedule',
        # Importing
        'importer_dataimportsession',
        'importer_dataimportcolumnmap',
        'importer_dataimportrow',
    ]