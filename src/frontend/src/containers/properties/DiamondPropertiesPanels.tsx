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

import { UserRoles } from "@lib/enums/Roles";
import type { PanelType } from "@lib/types/Panel";
import { useUserState } from "@store/UserState";
import DiamondColorTable from "@components/tables/diamond-properties/DiamondColorTable";
import DiamondCutTable from "@components/tables/diamond-properties/DiamondCutTable";
import DiamondQualityTable from "@components/tables/diamond-properties/DiamondQualityTable";
import DiamondRateTable from "@components/tables/diamond-properties/DiamondRateTable";
import DiamondShapeTable from "@components/tables/diamond-properties/DiamondShapeTable";
import DiamondSizeTable from "@components/tables/diamond-properties/DiamondSizeTable";
import DiamondStoneTable from "@components/tables/diamond-properties/DiamondStoneTable";

/** Panels displayed under the "Diamond Properties" tab of the Properties page */
export function useDiamondPropertyPanels(): PanelType[] {
  const user = useUserState();

  return useMemo(() => {
    return [
      {
        name: "diamond-stone",
        hidden: !user.hasViewRole(UserRoles.properties_diamond_stone),
        label: t`Stone`,
        icon: <IconDiamond />,
        content: <DiamondStoneTable />,
      },
      {
        name: "diamond-cut",
        hidden: !user.hasViewRole(UserRoles.properties_diamond_cut),
        label: t`Cut`,
        icon: <IconScissors />,
        content: <DiamondCutTable />,
      },
      {
        name: "diamond-shape",
        hidden: !user.hasViewRole(UserRoles.properties_diamond_shape),
        label: t`Shape`,
        icon: <IconShape />,
        content: <DiamondShapeTable />,
      },
      {
        name: "diamond-color",
        hidden: !user.hasViewRole(UserRoles.properties_diamond_color),
        label: t`Color`,
        icon: <IconPalette />,
        content: <DiamondColorTable />,
      },
      {
        name: "diamond-size",
        hidden: !user.hasViewRole(UserRoles.properties_diamond_size),
        label: t`Size`,
        icon: <IconScale />,
        content: <DiamondSizeTable />,
      },
      {
        name: "diamond-quality",
        hidden: !user.hasViewRole(UserRoles.properties_diamond_quality),
        label: t`Quality`,
        icon: <IconCertificate />,
        content: <DiamondQualityTable />,
      },
      {
        name: "diamond-rate",
        hidden: !user.hasViewRole(UserRoles.properties_diamond_stone_rate),
        label: t`Weight / Rate Per Stone`,
        icon: <IconCoin />,
        content: <DiamondRateTable />,
      },
    ];
  }, [user]);
}
