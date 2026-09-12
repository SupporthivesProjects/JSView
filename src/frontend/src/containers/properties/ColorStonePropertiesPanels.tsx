import { t } from "@lingui/core/macro";
import { useMemo } from "react";

import {
  IconAward,
  IconCategory,
  IconColorFilter,
  IconRuler2,
  IconScale,
  IconScissors,
  IconSparkles,
} from "@tabler/icons-react";

import type { PanelType } from "@lib/types/Panel";
import ColorStoneColorTable from "@components/tables/colorStone/ColorStoneColorTable";
import ColorStoneCutTable from "@components/tables/colorStone/ColorStoneCutTable";
import ColorStoneQualityTable from "@components/tables/colorStone/ColorStoneQualityTable";
import ColorStoneRateTable from "@components/tables/colorStone/ColorStoneRateTable";
import ColorStoneShapeTable from "@components/tables/colorStone/ColorStoneShapeTable";
import ColorStoneSizeTable from "@components/tables/colorStone/ColorStoneSizeTable";
import ColorStoneTable from "@components/tables/colorStone/ColorStoneTable";

/** Panels displayed under the "Color Stone Properties" tab of the Properties page */
export function useColorStonePropertyPanels(): PanelType[] {
  return useMemo(() => {
    return [
      {
        name: "stone-types",
        label: t`Stone`,
        icon: <IconSparkles />,
        content: <ColorStoneTable />,
      },
      {
        name: "stone-cut",
        label: t`Cut`,
        icon: <IconScissors />,
        content: <ColorStoneCutTable />,
      },
      {
        name: "stone-shape",
        label: t`Shape`,
        icon: <IconCategory />,
        content: <ColorStoneShapeTable />,
      },
      {
        name: "stone-color",
        label: t`Color`,
        icon: <IconColorFilter />,
        content: <ColorStoneColorTable />,
      },
      {
        name: "stone-size",
        label: t`Size`,
        icon: <IconRuler2 />,
        content: <ColorStoneSizeTable />,
      },
      {
        name: "stone-quality",
        label: t`Quality`,
        icon: <IconAward />,
        content: <ColorStoneQualityTable />,
      },
      {
        name: "stone-rate",
        label: t`Weight / Rate Per Stone`,
        icon: <IconScale />,
        content: <ColorStoneRateTable />,
      },
    ];
  }, []);
}
