import { darken, useMantineColorScheme, useMantineTheme } from '@mantine/core';
import { useMemo } from 'react';

import { vars } from '../../../styles/theme';

/* The `react-select` fields do not follow Mantine theming, so the palette they
 * are given is derived from the Mantine theme here. Shared by every field that
 * renders one, so they all look like the same control.
 */
export function useSelectFieldColors(): any {
  const theme = useMantineTheme();
  const { colorScheme } = useMantineColorScheme();

  return useMemo(() => {
    if (colorScheme === 'dark') {
      return {
        neutral0: vars.colors.dark[6],
        neutral5: vars.colors.dark[4],
        neutral10: vars.colors.dark[4],
        neutral20: vars.colors.dark[4],
        neutral30: vars.colors.dark[3],
        neutral40: vars.colors.dark[2],
        neutral50: vars.colors.dark[1],
        neutral60: vars.colors.dark[0],
        neutral70: vars.colors.dark[0],
        neutral80: vars.colors.dark[0],
        neutral90: vars.colors.dark[0],
        primary: vars.colors.primaryColors[7],
        primary25: vars.colors.primaryColors[6],
        primary50: vars.colors.primaryColors[5],
        primary75: vars.colors.primaryColors[4]
      };
    }

    return {
      neutral0: vars.colors.white,
      neutral5: darken(vars.colors.white, 0.05),
      neutral10: darken(vars.colors.white, 0.1),
      neutral20: darken(vars.colors.white, 0.2),
      neutral30: darken(vars.colors.white, 0.3),
      neutral40: darken(vars.colors.white, 0.4),
      neutral50: darken(vars.colors.white, 0.5),
      neutral60: darken(vars.colors.white, 0.6),
      neutral70: darken(vars.colors.white, 0.7),
      neutral80: darken(vars.colors.white, 0.8),
      neutral90: darken(vars.colors.white, 0.9),
      primary: vars.colors.primaryColors[7],
      primary25: vars.colors.primaryColors[4],
      primary50: vars.colors.primaryColors[5],
      primary75: vars.colors.primaryColors[6]
    };
  }, [theme, colorScheme]);
}

/** Styles shared by every `react-select` field. */
export const selectFieldStyles = {
  menuPortal: (base: any) => ({ ...base, zIndex: 9999 }),
  clearIndicator: (base: any) => ({
    ...base,
    color: 'red',
    ':hover': { color: 'red' }
  })
};
