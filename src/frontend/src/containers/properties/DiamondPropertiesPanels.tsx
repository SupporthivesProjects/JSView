import { t } from "@lingui/core/macro";
import { useMemo } from "react";

import {
  IconCertificate,
  IconCoin,
  IconDiamond,
  IconPalette,
  IconScale,
  IconScissors,
  IconShape,
} from "@tabler/icons-react";

import type { PanelType } from "@lib/types/Panel";
import DiamondColorTable from "@components/tables/diamond-properties/DiamondColorTable";
import DiamondCutTable from "@components/tables/diamond-properties/DiamondCutTable";
import DiamondQualityTable from "@components/tables/diamond-properties/DiamondQualityTable";
import DiamondRateTable from "@components/tables/diamond-properties/DiamondRateTable";
import DiamondShapeTable from "@components/tables/diamond-properties/DiamondShapeTable";
import DiamondSizeTable from "@components/tables/diamond-properties/DiamondSizeTable";
import DiamondStoneTable from "@components/tables/diamond-properties/DiamondStoneTable";

/** Panels displayed under the "Diamond Properties" tab of the Properties page */
export function useDiamondPropertyPanels(): PanelType[] {
  return useMemo(() => {
    return [
      {
        name: "diamond-stone",
        label: t`Stone`,
        icon: <IconDiamond />,
        content: <DiamondStoneTable />,
      },
      {
        name: "diamond-cut",
        label: t`Cut`,
        icon: <IconScissors />,
        content: <DiamondCutTable />,
      },
      {
        name: "diamond-shape",
        label: t`Shape`,
        icon: <IconShape />,
        content: <DiamondShapeTable />,
      },
      {
        name: "diamond-color",
        label: t`Color`,
        icon: <IconPalette />,
        content: <DiamondColorTable />,
      },
      {
        name: "diamond-size",
        label: t`Size`,
        icon: <IconScale />,
        content: <DiamondSizeTable />,
      },
      {
        name: "diamond-quality",
        label: t`Quality`,
        icon: <IconCertificate />,
        content: <DiamondQualityTable />,
      },
      {
        name: "diamond-rate",
        label: t`Weight / Rate Per Stone`,
        icon: <IconCoin />,
        content: <DiamondRateTable />,
      },
    ];
  }, []);
}
