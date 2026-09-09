import { style } from '@vanilla-extract/css';
import { vars } from '../../../styles/theme';

export const selectedPanelTab = style({
  selectors: {
    '&[data-active]': {
      background: vars.colors.primaryColors.light
    }
  }
});

/* Layout for a panel group which fills the remaining viewport height
 * (see the `fillHeight` prop): the group itself never scrolls, the tab
 * sidebar and the panel content each scroll inside their own column.
 */
export const fillHeightGroup = style({
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden'
});

export const fillHeightTabs = style({
  flex: 1,
  minHeight: 0
});

export const fillHeightTabList = style({
  flexWrap: 'nowrap',
  flexShrink: 0,
  minHeight: 0,
  overflowY: 'auto',
  overflowX: 'hidden',
  /* The sidebar still scrolls, but without a visible scrollbar. */
  scrollbarWidth: 'none',
  msOverflowStyle: 'none',
  '::-webkit-scrollbar': {
    display: 'none'
  },
  /* Never let the sidebar be squeezed narrower than its longest label. */
  minWidth: 'max-content'
});

export const fillHeightPanel = style({
  minHeight: 0,
  overflowY: 'auto'
});
