import { t } from '@lingui/core/macro';

/*
 * Enumeration of available user role groups
 */
export enum UserRoles {
  admin = 'admin',
  bom = 'bom',
  build = 'build',
  part = 'part',
  part_category = 'part_category',
  purchase_order = 'purchase_order',
  return_order = 'return_order',
  transfer_order = 'transfer_order',
  sales_order = 'sales_order',
  stock = 'stock',
  stock_location = 'stock_location',

  // Master
  customer = 'customer',
  vendor = 'vendor',
  company_contact = 'company_contact',
  master_ac_executive = 'master_ac_executive',
  master_metal_type = 'master_metal_type',
  master_metal_purity = 'master_metal_purity',
  master_metal_rate = 'master_metal_rate',
  master_jewelry_category = 'master_jewelry_category',
  master_jewelry_sub_category = 'master_jewelry_sub_category',
  master_finding_type = 'master_finding_type',
  master_finding_item = 'master_finding_item',
  master_setting = 'master_setting',
  master_labour_setting = 'master_labour_setting',
  master_finish_type = 'master_finish_type',
  master_stamp = 'master_stamp',
  master_duty = 'master_duty',
  master_terms = 'master_terms',
  master_courier_service = 'master_courier_service',
  master_po_mail = 'master_po_mail',
  master_templates = 'master_templates',

  // Properties
  properties_diamond_stone = 'properties_diamond_stone',
  properties_diamond_cut = 'properties_diamond_cut',
  properties_diamond_shape = 'properties_diamond_shape',
  properties_diamond_color = 'properties_diamond_color',
  properties_diamond_size = 'properties_diamond_size',
  properties_diamond_quality = 'properties_diamond_quality',
  properties_diamond_stone_rate = 'properties_diamond_stone_rate',
  properties_color_stone = 'properties_color_stone',
  properties_color_stone_cut = 'properties_color_stone_cut',
  properties_color_stone_shape = 'properties_color_stone_shape',
  properties_color_stone_color = 'properties_color_stone_color',
  properties_color_stone_size = 'properties_color_stone_size',
  properties_color_stone_quality = 'properties_color_stone_quality',
  properties_color_stone_rate = 'properties_color_stone_rate',

  // Cards
  cost_card = 'cost_card',
  cost_card_diamond_line = 'cost_card_diamond_line',
  cost_card_color_stone_line = 'cost_card_color_stone_line',
  cost_card_finish_line = 'cost_card_finish_line',
  cost_card_stone_place = 'cost_card_stone_place',
  cost_card_version = 'cost_card_version',

  // Purchase
  js_purchase_request = 'js_purchase_request',
  js_purchase_request_line = 'js_purchase_request_line',
  js_purchase_order = 'js_purchase_order',
  js_purchase_order_line = 'js_purchase_order_line',
  js_po_cost_card = 'js_po_cost_card',
  js_po_cost_card_line = 'js_po_cost_card_line',

  // Requisition
  requisition_flute_entry = 'requisition_flute_entry',
  requisition_flute_entry_line = 'requisition_flute_entry_line',
  requisition_metal_sent = 'requisition_metal_sent',

  // Vendor Shipment
  vendor_shipment = 'vendor_shipment',
  vendor_shipment_line = 'vendor_shipment_line',

  // Reports
  report = 'report'
}

/*
 * Roles which grant access to each top level menu.
 * A menu is shown when the user can view at least one of its roles.
 */
export const MenuRoles: Record<string, UserRoles[]> = {
  properties: [
    UserRoles.properties_diamond_stone,
    UserRoles.properties_diamond_cut,
    UserRoles.properties_diamond_shape,
    UserRoles.properties_diamond_color,
    UserRoles.properties_diamond_size,
    UserRoles.properties_diamond_quality,
    UserRoles.properties_diamond_stone_rate,
    UserRoles.properties_color_stone,
    UserRoles.properties_color_stone_cut,
    UserRoles.properties_color_stone_shape,
    UserRoles.properties_color_stone_color,
    UserRoles.properties_color_stone_size,
    UserRoles.properties_color_stone_quality,
    UserRoles.properties_color_stone_rate
  ],
  master: [
    UserRoles.customer,
    UserRoles.vendor,
    UserRoles.company_contact,
    UserRoles.master_ac_executive,
    UserRoles.master_metal_type,
    UserRoles.master_metal_purity,
    UserRoles.master_metal_rate,
    UserRoles.master_jewelry_category,
    UserRoles.master_jewelry_sub_category,
    UserRoles.master_finding_type,
    UserRoles.master_finding_item,
    UserRoles.master_setting,
    UserRoles.master_labour_setting,
    UserRoles.master_finish_type,
    UserRoles.master_stamp,
    UserRoles.master_duty,
    UserRoles.master_terms,
    UserRoles.master_courier_service,
    UserRoles.cost_card_stone_place
  ],
  cards: [UserRoles.cost_card],
  purchase: [UserRoles.js_purchase_request, UserRoles.js_purchase_order],
  requisition: [
    UserRoles.js_purchase_order,
    UserRoles.requisition_flute_entry,
    UserRoles.requisition_metal_sent
  ],
  'vendor-shipment': [UserRoles.vendor_shipment],
  reports: [UserRoles.report]
};

/*
 * Enumeration of available user permissions within each role group
 */
export enum UserPermissions {
  view = 'view',
  add = 'add',
  change = 'change',
  delete = 'delete'
}

export function userRoleLabel(role: UserRoles): string {
  switch (role) {
    case UserRoles.admin:
      return t`Admin`;
    case UserRoles.build:
      return t`Build Orders`;
    case UserRoles.part:
      return t`Parts`;
    case UserRoles.part_category:
      return t`Part Categories`;
    case UserRoles.purchase_order:
      return t`Purchase Orders`;
    case UserRoles.return_order:
      return t`Return Orders`;
    case UserRoles.transfer_order:
      return t`Transfer Orders`;
    case UserRoles.sales_order:
      return t`Sales Orders`;
    case UserRoles.stock:
      return t`Stock Items`;
    case UserRoles.stock_location:
      return t`Stock Location`;
    default:
      return role as string;
  }
}
