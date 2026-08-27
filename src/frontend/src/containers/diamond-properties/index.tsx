import { t } from "@lingui/core/macro";
import { Stack } from "@mantine/core";
import { useMemo } from "react";

import {
  IconDiamond,
  IconScissors,
  IconShape,
  IconPalette,
  IconScale,
  IconCertificate,
  IconCoin,
} from "@tabler/icons-react";

import { UserRoles } from "@lib/enums/Roles";
import type { PanelType } from "@lib/types/Panel";
import PermissionDenied from "@components/shared/errors/PermissionDenied";
import { PageDetail } from "@components/nav/PageDetail";
import { PanelGroup } from "@components/shared/panels/PanelGroup";
import { useUserState } from "@store/UserState";
import DiamondCutTable from "@components/tables/diamond-properties/DiamondCutTable";
import DiamondShapeTable from "@components/tables/diamond-properties/DiamondShapeTable";
import DiamondColorTable from "@components/tables/diamond-properties/DiamondColorTable";
import DiamondSizeTable from "@components/tables/diamond-properties/DiamondSizeTable";
import DiamondQualityTable from "@components/tables/diamond-properties/DiamondQualityTable";
import DiamondRateTable from "@components/tables/diamond-properties/DiamondRateTable";
import DiamondStoneTable from "@components/tables/diamond-properties/DiamondStoneTable";

export default function DiamondPropertiesIndex() {
  const user = useUserState();

  const panels: PanelType[] = useMemo(() => {
    return [
      {
        name: "diamond-stone",
        label: t`Diamond Stone`,
        icon: <IconDiamond />,
        content: <DiamondStoneTable />,
      },
      {
        name: "diamond-cut",
        label: t`Diamond Cut`,
        icon: <IconScissors />,
        content: <DiamondCutTable />,
      },
      {
        name: "diamond-shape",
        label: t`Diamond Shape`,
        icon: <IconShape />,
        content: <DiamondShapeTable />,
      },
      {
        name: "diamond-color",
        label: t`Diamond Color`,
        icon: <IconPalette />,
        content: <DiamondColorTable />,
      },
      {
        name: "diamond-size",
        label: t`Diamond Size`,
        icon: <IconScale />,
        content: <DiamondSizeTable />,
      },
      {
        name: "diamond-quality",
        label: t`Diamond Quality`,
        icon: <IconCertificate />,
        content: <DiamondQualityTable />,
      },
      {
        name: "diamond-rate",
        label: t`Diamond Rate`,
        icon: <IconCoin />,
        content: <DiamondRateTable />,
      },
    ];
  }, []);

  if (!user.hasViewRole(UserRoles.part)) {
    return <PermissionDenied />;
  }

  return (
    <Stack>
      <PageDetail title={t`Diamond Stone`} />
      <PanelGroup pageKey="diamond-stone-index" panels={panels} />
    </Stack>
  );
}
