import { t } from "@lingui/core/macro";
import { Stack } from "@mantine/core";

import { MenuRoles } from "@lib/enums/Roles";
import PermissionDenied from "@components/shared/errors/PermissionDenied";
import { PageDetail } from "@components/nav/PageDetail";
import { useUserState } from "@store/UserState";

export default function POMailIndex() {
  const user = useUserState();

  if (!user.hasViewAnyRole(MenuRoles["po-mail"])) {
    return <PermissionDenied />;
  }

  return (
    <Stack>
      <PageDetail title={t`P.O. Mail`} />
    </Stack>
  );
}
