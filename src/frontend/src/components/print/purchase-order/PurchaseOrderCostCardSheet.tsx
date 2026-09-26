import type { ReactNode } from 'react';

import CompanyLogo from '@assets/images/inventree-component.svg';
import { formatPrintDate, money, text } from './format';
import './purchaseOrderCostCard.css';
import './purchaseOrderPrint.css';
import type {
  PurchaseOrderCostCard,
  PurchaseOrderCostCardStoneLine,
  PurchaseOrderPrintPayload
} from './types';

/** Number of studding columns preceding the "Total :" figures */
const STUDDING_LEAD_COLUMNS = 8;

function StoneRow({
  line
}: { line: PurchaseOrderCostCardStoneLine }): ReactNode {
  return (
    <tr>
      <td>{line.etype}</td>
      <td>{line.shape}</td>
      <td>{line.cut}</td>
      <td>{line.mm_size}</td>
      <td>{line.sieve_size}</td>
      <td>{line.stone}</td>
      <td>{line.colour}</td>
      <td>{text(line.pointer)}</td>
      <td>{text(line.pcs)}</td>
      <td>{text(line.cts)}</td>
      <td>{line.pc}</td>
      <td>{text(line.rate)}</td>
      <td>{money(line.amount)}</td>
      <td>{line.setting}</td>
      <td>{text(line.labour_rate)}</td>
      <td>{money(line.labour_amount)}</td>
    </tr>
  );
}

/**
 * Sum the labour amounts of the studding lines.
 * Returns an empty cell for the vendor format, where every labour amount is
 * stripped by the backend.
 */
function studdingLabourTotal(card: PurchaseOrderCostCard): string {
  const amounts = card.stone_lines
    .map((line) => line.labour_amount)
    .filter((amount) => amount !== null && amount !== undefined);

  if (amounts.length === 0) {
    return '';
  }

  return money(
    amounts.reduce<number>((total, amount) => total + Number(amount), 0)
  );
}

function CostCardSheet({ card }: { card: PurchaseOrderCostCard }): ReactNode {
  const summary = card.summary;

  // The vendor format hides the pricing build-up, so only render what is there
  const showStudding = summary.studding !== undefined;
  const showPricing = summary.fob !== undefined;

  return (
    <div className='cc-sheet'>
      <div className='cc-sheet-head'>
        <img className='cc-logo' src={CompanyLogo} alt='' />
        <div className='cc-title'>COST BREAKDWON SHEET</div>
      </div>

      <div className='cc-top'>
        <table className='cc-info-table cc-info-left'>
          <tbody>
            <tr>
              <td className='cc-info-label'>CC No :</td>
              <td className='cc-info-value'>{card.cc_no}</td>
            </tr>
            <tr>
              <td className='cc-info-label'>Customer :</td>
              <td className='cc-info-value'>{card.customer}</td>
            </tr>
            <tr>
              <td className='cc-info-label'>Vendor :</td>
              <td className='cc-info-value'>{card.vendor}</td>
            </tr>
            <tr>
              <td className='cc-info-label'>V. Style :</td>
              <td className='cc-info-value'>{card.v_style_no}</td>
            </tr>
          </tbody>
        </table>

        <table className='cc-info-table cc-info-middle'>
          <tbody>
            <tr>
              <td className='cc-info-label'>Style :</td>
              <td className='cc-info-value'>{card.style_no}</td>
            </tr>
            <tr>
              <td className='cc-info-label'>Category :</td>
              <td className='cc-info-value'>{card.category}</td>
            </tr>
            <tr>
              <td className='cc-info-label'>Sub Category :</td>
              <td className='cc-info-value'>{card.sub_category}</td>
            </tr>
            <tr>
              <td className='cc-info-label'>Date :</td>
              <td className='cc-info-value'>{formatPrintDate(card.date)}</td>
            </tr>
            <tr>
              <td className='cc-info-label'>Modified By :</td>
              <td className='cc-info-value'>{card.modified_by}</td>
            </tr>
          </tbody>
        </table>

        <table className='cc-images-table'>
          <tbody>
            <tr>
              <td>
                {card.images.front ? (
                  <img src={card.images.front} alt='Front View' />
                ) : (
                  'Front View'
                )}
              </td>
              <td>
                {card.images.side ? (
                  <img src={card.images.side} alt='Side View' />
                ) : (
                  'Side View'
                )}
              </td>
              <td>
                {card.images.back ? (
                  <img src={card.images.back} alt='Back View' />
                ) : (
                  'Back View'
                )}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <table className='cc-metal-table'>
        <colgroup>
          <col style={{ width: '37%' }} />
          <col style={{ width: '9%' }} />
          <col style={{ width: '7.7%' }} />
          <col style={{ width: '12.6%' }} />
          <col style={{ width: '11.9%' }} />
          <col style={{ width: '21.8%' }} />
        </colgroup>
        <tbody>
          <tr>
            <th>Type</th>
            <th>Tr. Oz</th>
            <th>KT</th>
            <th>Net Wt.</th>
            <th>Loss %</th>
            <th>Metal Amount</th>
          </tr>
          <tr>
            <td>{card.metal.type}</td>
            <td>{text(card.metal.troy_oz)}</td>
            <td>{text(card.metal.kt)}</td>
            <td>{text(card.metal.net_wt)}</td>
            <td>{text(card.metal.loss_pct)}</td>
            <td>{money(card.metal.metal_amount)}</td>
          </tr>
        </tbody>
      </table>

      <table className='cc-studding-table'>
        <colgroup>
          <col style={{ width: '8.2%' }} />
          <col style={{ width: '7%' }} />
          <col style={{ width: '8.8%' }} />
          <col style={{ width: '8.2%' }} />
          <col style={{ width: '8.7%' }} />
          <col style={{ width: '8.8%' }} />
          <col style={{ width: '6%' }} />
          <col style={{ width: '5.4%' }} />
          <col style={{ width: '3.8%' }} />
          <col style={{ width: '5.1%' }} />
          <col style={{ width: '3.3%' }} />
          <col style={{ width: '3.6%' }} />
          <col style={{ width: '6.6%' }} />
          <col style={{ width: '6.1%' }} />
          <col style={{ width: '4.1%' }} />
          <col style={{ width: '6.3%' }} />
        </colgroup>
        <tbody>
          <tr>
            <td className='cc-section-label' colSpan={13}>
              Studding Details
            </td>
            <td className='cc-section-label cc-section-centered' colSpan={3}>
              Labour
            </td>
          </tr>
          <tr className='cc-studding-head'>
            <th>Type</th>
            <th>Shape</th>
            <th>Cut</th>
            <th>MM Size</th>
            <th>Sieve Size</th>
            <th>Stone Type</th>
            <th>Colour</th>
            <th>Pointer</th>
            <th>Pcs</th>
            <th>Carats</th>
            <th>P/C</th>
            <th>Rate</th>
            <th>Amount</th>
            <th>Setting</th>
            <th>Rate</th>
            <th>Amount</th>
          </tr>
          {card.stone_lines.map((line, index) => (
            <StoneRow key={`${line.etype}-${index}`} line={line} />
          ))}
          <tr>
            <td className='cc-total-label' colSpan={STUDDING_LEAD_COLUMNS}>
              Total :
            </td>
            <td>{text(card.stone_totals.total_pcs)}</td>
            <td>{text(card.stone_totals.total_cts)}</td>
            <td />
            <td />
            <td>{money(card.stone_totals.total_amount)}</td>
            <td colSpan={2} />
            <td>{studdingLabourTotal(card)}</td>
          </tr>
        </tbody>
      </table>

      <div className='cc-bottom'>
        <div className='cc-bottom-left'>
          <div className='cc-block-title'>Labour Details</div>
          <table className='cc-labour-table'>
            <tbody>
              <tr>
                <td className='cc-labour-label'>FINISH</td>
                <td className='cc-labour-value'>{money(card.labour.finish)}</td>
              </tr>
              <tr>
                <td className='cc-labour-label'>DIAMOND</td>
                <td className='cc-labour-value'>
                  {money(card.labour.diamond)}
                </td>
              </tr>
              <tr>
                <td className='cc-labour-label'>COLOR STONE</td>
                <td className='cc-labour-value'>
                  {money(card.labour.colorstone)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className='cc-bottom-right'>
          <div className='cc-block-title cc-block-title-spacer'>&nbsp;</div>
          <table className='cc-summary-table'>
            <tbody>
              <tr>
                <th>Metal</th>
                {showStudding && <th>Studding</th>}
                <th>Labour</th>
                <th>Other</th>
                {showPricing && (
                  <>
                    <th>F O B</th>
                    <th>Markup %</th>
                    <th>With Markup</th>
                    <th>Duty %</th>
                    <th>With Duty</th>
                    <th>Margin %</th>
                    <th>Final Price</th>
                  </>
                )}
              </tr>
              <tr>
                <td>{money(summary.metal)}</td>
                {showStudding && <td>{money(summary.studding)}</td>}
                <td>{money(summary.labour)}</td>
                <td>{money(summary.none)}</td>
                {showPricing && (
                  <>
                    <td>{money(summary.fob)}</td>
                    <td>{text(summary.markup_pct)}</td>
                    <td>{money(summary.with_markup)}</td>
                    <td>{text(summary.duty_pct)}</td>
                    <td>{money(summary.with_duty)}</td>
                    <td>{text(summary.margin_pct)}</td>
                    <td>{money(summary.final_price)}</td>
                  </>
                )}
              </tr>
            </tbody>
          </table>

          <table className='cc-design-table'>
            <tbody>
              <tr>
                <td className='cc-design-label'>Design Instruction</td>
                <td className='cc-design-value'>{card.design_instruction}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}


export default function PurchaseOrderCostCardSheet({
  data
}: { data: PurchaseOrderPrintPayload }): ReactNode {
  const costcards = data.costcards ?? [];

  return (
    <div className='po-print-sheet po-print-sheet-wide cc-sheet-set'>
      {costcards.map((card, index) => (
        <CostCardSheet key={`${card.cc_no}-${index}`} card={card} />
      ))}
    </div>
  );
}
