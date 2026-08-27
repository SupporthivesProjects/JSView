import { t } from "@lingui/core/macro";
import { Stack } from "@mantine/core";
import { useMemo } from "react";

import {
  IconSparkles,
  IconScissors,
  IconCategory,
  IconColorFilter,
  IconRuler2,
  IconAward,
  IconScale,
} from "@tabler/icons-react";

import { UserRoles } from "@lib/enums/Roles";
import type { PanelType } from "@lib/types/Panel";
import PermissionDenied from "@components/shared/errors/PermissionDenied";
import { PageDetail } from "@components/nav/PageDetail";
import { PanelGroup } from "@components/shared/panels/PanelGroup";
import { useUserState } from "@store/UserState";
import ColorStoneTable from "@components/tables/colorStone/ColorStoneTable";
import ColorStoneCutTable from "@components/tables/colorStone/ColorStoneCutTable";
import ColorStoneShapeTable from "@components/tables/colorStone/ColorStoneShapeTable";
import ColorStoneColorTable from "@components/tables/colorStone/ColorStoneColorTable";
import ColorStoneSizeTable from "@components/tables/colorStone/ColorStoneSizeTable";
import ColorStoneQualityTable from "@components/tables/colorStone/ColorStoneQualityTable";
import ColorStoneRateTable from "@components/tables/colorStone/ColorStoneRateTable";

export default function ColorStonePropertiesIndex() {
  const user = useUserState();

  const panels: PanelType[] = useMemo(() => {
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

  if (!user.hasViewRole(UserRoles.part)) {
    return <PermissionDenied />;
  }

  return (
    <Stack>
      <PageDetail title={t`Color Stone Properties`} />
      <PanelGroup pageKey="color-stone-index" panels={panels} />
    </Stack>
  );
}
