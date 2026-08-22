import { t } from "@lingui/core/macro";
import {
  ActionIcon,
  Alert,
  Anchor,
  Badge,
  Button,
  Card,
  Group,
  Loader,
  ScrollArea,
  Stack,
  Text,
  Tooltip,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconTrash } from "@tabler/icons-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { UserRoles } from "@lib/enums/Roles";
import { apiUrl } from "@lib/functions/Api";
import { useApi } from "@context/ApiContext";
import { useUserState } from "@store/UserState";

export function VendorContactsPanel({ vendorId }: { vendorId?: number }) {
  const api = useApi();
  const user = useUserState();
  const queryClient = useQueryClient();
  const [confirmId, setConfirmId] = useState<number | null>(null);

  const query = useQuery({
    queryKey: ["vendor-contacts", vendorId],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.master_vendor_customer_contact), {
          params: { company: vendorId },
        })
        .then((r) => r.data?.results ?? r.data ?? []),
    enabled: !!vendorId,
    staleTime: 5 * 60 * 1000,
  });

  const deleteContact = useMutation({
    mutationFn: (pk: number) =>
      api.delete(apiUrl(ApiEndpoints.master_vendor_customer_contact, pk)),
    onSuccess: () => {
      setConfirmId(null);
      notifications.show({
        title: t`Contact deleted`,
        message: t`The contact was removed`,
        color: "green",
      });
      queryClient.invalidateQueries({ queryKey: ["vendor-contacts", vendorId] });
    },
    onError: (error: any) => {
      notifications.show({
        title: t`Delete failed`,
        message: error?.response?.data?.detail ?? t`Unable to delete contact`,
        color: "red",
      });
    },
  });

  const canDelete = user.hasDeleteRole(UserRoles.part);

  if (!vendorId || query.isLoading) {
    return (
      <Group justify="center" p="md">
        <Loader size="sm" />
      </Group>
    );
  }

  if (query.isError) {
    return <Alert color="red">{t`Unable to load contacts`}</Alert>;
  }

  const contacts: any[] = query.data ?? [];

  if (contacts.length === 0) {
    return <Alert color="blue">{t`No contacts recorded for this vendor`}</Alert>;
  }

  return (
    <ScrollArea.Autosize mah={400}>
      <Stack gap="xs">
        {contacts.map((c) => (
          <Card key={c.pk} withBorder padding="sm" radius="md">
            <Group justify="space-between" wrap="nowrap" align="flex-start">
              <Stack gap={2}>
                <Group gap="xs">
                  <Text fw={600}>{c.name}</Text>
                  {c.role && <Badge variant="light">{c.role}</Badge>}
                </Group>
                {c.email && (
                  <Anchor size="sm" href={`mailto:${c.email}`}>
                    {c.email}
                  </Anchor>
                )}
                {c.phone && (
                  <Text size="sm" c="dimmed">
                    {t`Phone`}: {c.phone}
                  </Text>
                )}
                {c.mobile && (
                  <Text size="sm" c="dimmed">
                    {t`Mobile`}: {c.mobile}
                  </Text>
                )}
              </Stack>

              {canDelete &&
                (confirmId === c.pk ? (
                  <Group gap={4} wrap="nowrap">
                    <Button
                      size="compact-xs"
                      color="red"
                      loading={deleteContact.isPending}
                      onClick={() => deleteContact.mutate(c.pk)}
                    >
                      {t`Confirm`}
                    </Button>
                    <Button
                      size="compact-xs"
                      variant="subtle"
                      onClick={() => setConfirmId(null)}
                    >
                      {t`Cancel`}
                    </Button>
                  </Group>
                ) : (
                  <Tooltip label={t`Delete contact`} position="left">
                    <ActionIcon
                      color="red"
                      variant="subtle"
                      onClick={() => setConfirmId(c.pk)}
                    >
                      <IconTrash size={16} />
                    </ActionIcon>
                  </Tooltip>
                ))}
            </Group>
          </Card>
        ))}
      </Stack>
    </ScrollArea.Autosize>
  );
}