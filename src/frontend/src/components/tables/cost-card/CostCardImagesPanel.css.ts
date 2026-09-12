import { globalStyle, style } from '@vanilla-extract/css';
import { vars } from '../../../styles/theme';

const dark = ':root[data-mantine-color-scheme="dark"] &';

export const card = style({
  overflow: 'hidden',
  transition: 'transform 150ms ease, box-shadow 150ms ease',
  selectors: {
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: vars.shadows.md
    }
  }
});


export const preview = style({
  position: 'relative',
  aspectRatio: '1 / 1',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: vars.spacing.sm,
  backgroundColor: vars.colors.gray[0],
  selectors: {
    [dark]: {
      backgroundColor: vars.colors.dark[6]
    }
  }
});

export const imageWrap = style({
  width: '100%',
  height: '100%',
  minHeight: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center'
});

globalStyle(`${imageWrap} > *`, {
  width: '100%',
  height: '100%',
  minHeight: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center'
});

export const previewImage = style({
  width: 'auto',
  height: 'auto',
  maxWidth: '100%',
  maxHeight: '100%'
});

export const empty = style({
  width: '100%',
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 4,
  cursor: 'pointer',
  padding: 0,
  font: 'inherit',
  backgroundColor: 'transparent',
  border: `1px dashed ${vars.colors.gray[4]}`,
  borderRadius: vars.radius.md,
  color: vars.colors.gray[6],
  transition: 'border-color 150ms ease, color 150ms ease, background-color 150ms ease',
  selectors: {
    '&:hover': {
      borderColor: vars.colors.primaryColors.filled,
      color: vars.colors.primaryColors.filled,
      backgroundColor: vars.colors.primaryColors.light
    },
    [dark]: {
      borderColor: vars.colors.dark[3],
      color: vars.colors.dark[1]
    }
  }
});


export const overlay = style({
  position: 'absolute',
  inset: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: vars.spacing.xs,
  opacity: 0,
  backgroundColor: 'rgba(0, 0, 0, 0.45)',
  backdropFilter: 'blur(1px)',
  transition: 'opacity 150ms ease',
  selectors: {
    [`${card}:hover &`]: {
      opacity: 1
    },
    '&:focus-within': {
      opacity: 1
    }
  }
});

export const footer = style({
  borderTop: `1px solid ${vars.colors.gray[2]}`,
  selectors: {
    [dark]: {
      borderTopColor: vars.colors.dark[4]
    }
  }
});
