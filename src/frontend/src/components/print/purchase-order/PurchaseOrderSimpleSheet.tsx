import type { ReactNode } from 'react';

import CompanyLogo from '@assets/images/inventree-component.svg';
import { formatPrintDate, splitList } from './format';
import './purchaseOrderPrint.css';
import type {
  PurchaseOrderPrintLine,
  PurchaseOrderPrintPayload
} from './types';

/*
 * Static letterhead for the printed sheet.
 * The print API returns order data only, so the company block is fixed here.
 */
const COMPANY = {
  name: 'Jewel Source Inc.',
  address: '45 West- 45th street, 9th Floor. New York, N Y 10036, U S A',
  contact:
    'Phone: 1-212-3910312 Fax: 1-212-3910313 E-mail: sarju@jewelsourceinc.com'
};

function LineRows({ line }: { line: PurchaseOrderPrintLine }): ReactNode {
  const sizes = splitList(line.size);
  const pieces = splitList(line.size_pcs);
  const hasBreakdown = sizes.length > 0 || pieces.length > 0;
  const columns = Math.max(sizes.length, pieces.length);

  return (
    <>
      <tr>
        <td className='po-col-sr' rowSpan={hasBreakdown ? 2 : 1}>
          {line.sr}
        </td>
        <td>{line.style_no}</td>
        <td>{line.v_style_no}</td>
        <td>{line.qty}</td>
        <td>{line.metal_color_kt}</td>
        <td rowSpan={hasBreakdown ? 2 : 1} />
      </tr>
      {hasBreakdown && (
        <tr>
          <td className='po-breakdown-cell' colSpan={4}>
            <table className='po-breakdown-table'>
              <tbody>
                <tr>
                  <td className='po-breakdown-label'>Size</td>
                  {Array.from({ length: columns }).map((_entry, index) => (
                    <td key={`size-${index}`}>{sizes[index] ?? ''}</td>
                  ))}
                </tr>
                <tr>
                  <td className='po-breakdown-label'>Breakdown</td>
                  {Array.from({ length: columns }).map((_entry, index) => (
                    <td key={`pcs-${index}`}>{pieces[index] ?? ''}</td>
                  ))}
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
      )}
    </>
  );
}

/**
 * Printable purchase order sheet for the two "simple" formats.
 *
 * `vendor` and `self` share the same layout; the only difference is that the
 * `self` payload also carries the order value, which the vendor sheet must
 * never show.
 */
export default function PurchaseOrderSimpleSheet({
  data
}: { data: PurchaseOrderPrintPayload }): ReactNode {
  const po = data.po;
  const lines = data.lines ?? [];
  const totals = data.totals;

  return (
    <div className='po-print-sheet'>
      <table className='po-letterhead-table'>
        <tbody>
          <tr>
            <td className='po-logo-cell'>
              <img src={CompanyLogo} alt='' />
            </td>
            <td className='po-company-cell'>
              <div className='po-company-name'>{COMPANY.name}</div>
              <div className='po-company-line'>{COMPANY.address}</div>
              <div className='po-company-line'>{COMPANY.contact}</div>
            </td>
          </tr>
          <tr>
            <td className='po-doc-title' colSpan={2}>
              PURCHASE ORDER
            </td>
          </tr>
        </tbody>
      </table>

      <table className='po-fields-table'>
        <colgroup>
          <col style={{ width: '18%' }} />
          <col style={{ width: '11%' }} />
          <col style={{ width: '11%' }} />
          <col style={{ width: '17%' }} />
          <col style={{ width: '9%' }} />
          <col style={{ width: '10%' }} />
          <col style={{ width: '12%' }} />
          <col style={{ width: '12%' }} />
        </colgroup>
        <tbody>
          <tr className='po-field-head'>
            <th>P. O. No</th>
            <th>PO Date</th>
            <th>Due Date</th>
            <th>Vendor</th>
            <th>Customer</th>
            <th>P. O. By</th>
            <th>A/c Executive</th>
            <th>Category</th>
          </tr>
          <tr className='po-field-value'>
            <td>{po.pono}</td>
            <td>{formatPrintDate(po.podate)}</td>
            <td>{formatPrintDate(po.ddate)}</td>
            <td>{po.vendor}</td>
            <td>{po.customer}</td>
            <td>{po.prepby}</td>
            <td>{po.acexe}</td>
            <td>{po.pocategory}</td>
          </tr>
        </tbody>
      </table>

      <table className='po-meta-table'>
        <tbody>
          <tr>
            <td className='po-meta-label'>Vendor Address</td>
            <td className='po-meta-value'>{po.vendor_address}</td>
            <td className='po-stamp-head'>Stamp Image</td>
          </tr>
          <tr>
            <td className='po-meta-label'>Terms</td>
            <td className='po-meta-value'>{po.terms}</td>
            <td className='po-stamp-image' rowSpan={3}>
              {po.stamp_image ? <img src={po.stamp_image} alt='' /> : null}
            </td>
          </tr>
          <tr>
            <td className='po-meta-label'>Special Remark</td>
            <td className='po-meta-value'>{po.rem}</td>
          </tr>
          <tr>
            <td className='po-meta-label'>Stamp Detail</td>
            <td className='po-meta-value'>{po.stamp}</td>
          </tr>
        </tbody>
      </table>

      <table className='po-lines-table'>
        <thead>
          <tr>
            <th className='po-col-sr'>#</th>
            <th className='po-col-style'>Style No.</th>
            <th className='po-col-vstyle'>V. Style</th>
            <th className='po-col-qty'>Qty</th>
            <th>Metal Color &amp; KT</th>
            <th className='po-col-trailing' />
          </tr>
        </thead>
        <tbody>
          {lines.map((line) => (
            <LineRows key={line.sr} line={line} />
          ))}
        </tbody>
      </table>

      {totals && (
        <table className='po-totals-table'>
          <tbody>
            <tr>
              <td className='po-totals-label'>Total Qty</td>
              <td>{totals.total_qty}</td>
              <td className='po-totals-label'>Metal Value</td>
              <td>{totals.metal_value}</td>
              <td className='po-totals-label'>Labour Value</td>
              <td>{totals.labour_value}</td>
              {/* Only returned for the `self` format */}
              {totals.order_value !== undefined && (
                <>
                  <td className='po-totals-label'>Order Value</td>
                  <td>{totals.order_value}</td>
                </>
              )}
            </tr>
          </tbody>
        </table>
      )}
    </div>
  );
}
