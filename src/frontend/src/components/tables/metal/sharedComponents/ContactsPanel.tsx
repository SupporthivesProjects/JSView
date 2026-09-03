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
  SimpleGrid,
  Stack,
  Text,
  TextInput,
  Tooltip,
} from "@mantine/core";
import { notifications } from "@mantine/notifications";
import { IconEdit, IconMailForward, IconTrash } from "@tabler/icons-react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { UserRoles } from "@lib/enums/Roles";
import { apiUrl } from "@lib/functions/Api";
import { useApi } from "@context/ApiContext";
import { useUserState } from "@store/UserState";

type ContactDraft = {
  name: string;
  role: string;
  email: string;
  phone: string;
  mobile: string;
};

const EMPTY_DRAFT: ContactDraft = {
  name: "",
  role: "",
  email: "",
  phone: "",
  mobile: "",
};

export function ContactsPanel({
  id,
  queryKey,
}: {
  id?: number;
  queryKey: string;
}) {
  const api = useApi();
  const user = useUserState();
  const queryClient = useQueryClient();

  const [confirmId, setConfirmId] = useState<number | null>(null);
  const [editId, setEditId] = useState<number | null>(null);
  const [draft, setDraft] = useState<ContactDraft>(EMPTY_DRAFT);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const query = useQuery({
    queryKey: [queryKey, id],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.master_vendor_customer_contact), {
          params: { company: id },
        })
        .then((r) => r.data?.results ?? r.data ?? []),
    enabled: !!id,
    staleTime: 5 * 60 * 1000,
  });

  const startEdit = (contact: any) => {
    setConfirmId(null);
    setErrors({});
    setEditId(contact.pk);
    setDraft({
      name: contact.name ?? "",
      role: contact.role ?? "",
      email: contact.email ?? "",
      phone: contact.phone ?? "",
      mobile: contact.mobile ?? "",
    });
  };

  const cancelEdit = () => {
    setEditId(null);
    setDraft(EMPTY_DRAFT);
    setErrors({});
  };

  const updateContact = useMutation({
    mutationFn: ({ pk, values }: { pk: number; values: ContactDraft }) =>
      api.patch(
        apiUrl(ApiEndpoints.master_vendor_customer_contact, pk),
        values,
      ),
    onSuccess: () => {
      cancelEdit();
      notifications.show({
        title: t`Contact updated`,
        message: t`The contact was saved`,
        color: "green",
      });
      queryClient.invalidateQueries({ queryKey: [queryKey, id] });
    },
    onError: (error: any) => {
      const data = error?.response?.data;

      // DRF returns { field: ["message", ...] } on a 400
      if (data && typeof data === "object" && !Array.isArray(data)) {
        const fieldErrors: Record<string, string> = {};
        Object.entries(data).forEach(([field, messages]) => {
          fieldErrors[field] = Array.isArray(messages)
            ? String(messages[0])
            : String(messages);
        });
        setErrors(fieldErrors);
      }

      notifications.show({
        title: t`Update failed`,
        message: data?.detail ?? t`Unable to save contact`,
        color: "red",
      });
    },
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
      queryClient.invalidateQueries({ queryKey: [queryKey, id] });
    },
    onError: (error: any) => {
      notifications.show({
        title: t`Delete failed`,
        message: error?.response?.data?.detail ?? t`Unable to delete contact`,
        color: "red",
      });
    },
  });

  const canChange = user.hasChangeRole(UserRoles.part);
  const canDelete = user.hasDeleteRole(UserRoles.part);

  if (!id || query.isLoading) {
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
    return <Alert color="blue">{t`No contacts recorded yet`}</Alert>;
  }

  return (
    <ScrollArea.Autosize mah={400}>
      <Stack gap="xs">
        {contacts.map((c) => {
          const isEditing = editId === c.pk;

          return (
            <Card key={c.pk} withBorder padding="sm" radius="md">
              {isEditing ? (
                <Stack gap="xs">
                  <SimpleGrid cols={2} spacing="xs">
                    <TextInput
                      label={t`Name`}
                      value={draft.name}
                      error={errors.name}
                      onChange={(e) =>
                        setDraft({ ...draft, name: e.currentTarget.value })
                      }
                    />
                    <TextInput
                      label={t`Role`}
                      value={draft.role}
                      error={errors.role}
                      onChange={(e) =>
                        setDraft({ ...draft, role: e.currentTarget.value })
                      }
                    />
                    <TextInput
                      label={t`Email`}
                      value={draft.email}
                      error={errors.email}
                      onChange={(e) =>
                        setDraft({ ...draft, email: e.currentTarget.value })
                      }
                    />
                    <TextInput
                      label={t`Phone`}
                      value={draft.phone}
                      error={errors.phone}
                      onChange={(e) =>
                        setDraft({ ...draft, phone: e.currentTarget.value })
                      }
                    />
                    <TextInput
                      label={t`Mobile`}
                      value={draft.mobile}
                      error={errors.mobile}
                      onChange={(e) =>
                        setDraft({ ...draft, mobile: e.currentTarget.value })
                      }
                    />
                  </SimpleGrid>

                  <Group gap={6} justify="flex-end">
                    <Button
                      size="compact-sm"
                      loading={updateContact.isPending}
                      onClick={() =>
                        updateContact.mutate({ pk: c.pk, values: draft })
                      }
                    >
                      {t`Save`}
                    </Button>
                    <Button
                      size="compact-sm"
                      variant="subtle"
                      onClick={cancelEdit}
                    >
                      {t`Cancel`}
                    </Button>
                  </Group>
                </Stack>
              ) : (
                <Group justify="space-between" wrap="nowrap" align="flex-start">
                  <Stack gap={2}>
                    <Group gap="xs">
                      <Text fw={600}>{c.name}</Text>
                      {c.role && <Badge variant="light">{c.role}</Badge>}
                    </Group>
                    {c.email && (
                      <Group gap="2px">
                      <Anchor size="sm" href={`mailto:${c.email}`}>
                        {c.email} 
                      </Anchor>
                      <Anchor size="sm" href={`mailto:${c.email}`} display="flex">
                        <IconMailForward stroke={1} width={18} />
                      </Anchor>
                      </Group>
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

                  {confirmId === c.pk ? (
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
                    <Group gap={2} wrap="nowrap">
                      {canChange && (
                        <Tooltip label={t`Edit contact`} position="left">
                          <ActionIcon
                            color="blue"
                            variant="subtle"
                            onClick={() => startEdit(c)}
                          >
                            <IconEdit size={16} />
                          </ActionIcon>
                        </Tooltip>
                      )}
                      {canDelete && (
                        <Tooltip label={t`Delete contact`} position="left">
                          <ActionIcon
                            color="red"
                            variant="subtle"
                            onClick={() => {
                              cancelEdit();
                              setConfirmId(c.pk);
                            }}
                          >
                            <IconTrash size={16} />
                          </ActionIcon>
                        </Tooltip>
                      )}
                    </Group>
                  )}
                </Group>
              )}
            </Card>
          );
        })}
      </Stack>
    </ScrollArea.Autosize>
  );
}