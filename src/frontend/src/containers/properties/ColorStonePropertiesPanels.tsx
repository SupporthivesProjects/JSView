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
import ColorStoneColorTable from "@components/tables/colorStone/ColorStoneColorTable";
import ColorStoneCutTable from "@components/tables/colorStone/ColorStoneCutTable";
import ColorStoneQualityTable from "@components/tables/colorStone/ColorStoneQualityTable";
import ColorStoneRateTable from "@components/tables/colorStone/ColorStoneRateTable";
import ColorStoneShapeTable from "@components/tables/colorStone/ColorStoneShapeTable";
import ColorStoneSizeTable from "@components/tables/colorStone/ColorStoneSizeTable";
import ColorStoneTable from "@components/tables/colorStone/ColorStoneTable";

/** Panels displayed under the "Color Stone Properties" tab of the Properties page */
export function useColorStonePropertyPanels(): PanelType[] {
  const user = useUserState();

  return useMemo(() => {
    return [
      {
        name: "stone-types",
        hidden: !user.hasViewRole(UserRoles.properties_color_stone),
        label: t`Stone`,
       icon: <IconDiamond />,
        content: <ColorStoneTable />,
      },
      {
        name: "stone-cut",
        hidden: !user.hasViewRole(UserRoles.properties_color_stone_cut),
        label: t`Cut`,
        icon: <IconScissors />,
        content: <ColorStoneCutTable />,
      },
      {
        name: "stone-shape",
        hidden: !user.hasViewRole(UserRoles.properties_color_stone_shape),
        label: t`Shape`,
        icon: <IconShape />,
        content: <ColorStoneShapeTable />,
      },
      {
        name: "stone-color",
        hidden: !user.hasViewRole(UserRoles.properties_color_stone_color),
        label: t`Color`,
           icon: <IconPalette />,
        content: <ColorStoneColorTable />,
      },
      {
        name: "stone-size",
        hidden: !user.hasViewRole(UserRoles.properties_color_stone_size),
        label: t`Size`,
         icon: <IconScale />,
        content: <ColorStoneSizeTable />,
      },
      {
        name: "stone-quality",
        hidden: !user.hasViewRole(UserRoles.properties_color_stone_quality),
        label: t`Quality`,
        icon: <IconCertificate />,
        content: <ColorStoneQualityTable />,
      },
      {
        name: "stone-rate",
        hidden: !user.hasViewRole(UserRoles.properties_color_stone_rate),
        label: t`Weight / Rate Per Stone`,
       icon: <IconCoin />,
        content: <ColorStoneRateTable />,
      },
    ];
  }, [user]);
}
