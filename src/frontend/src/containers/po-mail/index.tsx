import { t } from "@lingui/core/macro";
import {
  Alert,
  Box,
  Button,
  Checkbox,
  Fieldset,
  Group,
  Paper,
  Stack,
  Text,
  TextInput,
  Textarea,
} from "@mantine/core";
import { useDebouncedValue } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { IconSend } from "@tabler/icons-react";
import { useQuery } from "@tanstack/react-query";
import { useEffect, useId, useState } from "react";
import Select from "react-select";

import { PageDetail } from "@components/nav/PageDetail";
import {
  selectFieldStyles,
  useSelectFieldColors,
} from "@components/forms/fields/SelectFieldTheme";
import PermissionDenied from "@components/shared/errors/PermissionDenied";
import { useApi } from "@context/ApiContext";
import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { MenuRoles } from "@lib/enums/Roles";
import { apiUrl } from "@lib/functions/Api";
import { useUserState } from "@store/UserState";

const EMPTY_EMAIL = "@gmail.com";

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const DEFAULT_FORMATS: POMailFormat[] = [
  { key: "vendor", label: "Vendor" },
  { key: "diamond_office", label: "Diamond Office" },
  { key: "color_stone_office", label: "Color Stone Office" },
  { key: "new_york_office", label: "New York Office" },
].map((format) => ({
  ...format,
  active: true,
  subject: "",
  email: "",
  attachments: "",
}));

interface POMailOrderOption {
  value: string;
  label: string;
}

interface POMailFormat {
  key: string;
  label: string;
  active: boolean;
  subject: string;
  email: string;
  attachments: string;
}

interface POMailOrderDetail {
  order: number;
  po_number: string;
  mail: number | null;
  formats: POMailFormat[];
}

interface POMailRow extends POMailFormat {
  checked: boolean;
  message: string;
}

/** Recipients may be separated by a comma or a semicolon */
function splitEmails(value: string): string[] {
  return value
    .split(/[;,]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function emailError(value: string): string {
  const emails = splitEmails(value);

  if (emails.length === 0) {
    return t`E-mail ID is required`;
  }

  if (emails.some((email) => !EMAIL_PATTERN.test(email))) {
    return t`Enter a valid E-mail ID`;
  }

  return "";
}

export default function POMailIndex() {
  const user = useUserState();
  const api = useApi();

  const [order, setOrder] = useState<POMailOrderOption | null>(null);
  const [search, setSearch] = useState<string>("");
  const [debouncedSearch] = useDebouncedValue(search, 300);
  const colors = useSelectFieldColors();
  const orderFieldId = useId();
  const orderId = order?.value ?? null;
  const [rows, setRows] = useState<POMailRow[]>([]);
  const [submitted, setSubmitted] = useState<boolean>(false);
  const [sending, setSending] = useState<boolean>(false);

  const allowed = user.hasViewAnyRole(MenuRoles["po-mail"]);

  const ordersQuery = useQuery({
    enabled: allowed,
    queryKey: ["po-mail-orders", debouncedSearch],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.po_mail_orders), {
          params: { search: debouncedSearch, type: "ORDER" },
        })
        .then(
          (response: any) =>
            (response.data ?? []).map((item: any) => ({
              value: String(item.id),
              label: item.po_number,
            })) as POMailOrderOption[],
        ),
  });

  const detailQuery = useQuery({
    enabled: allowed && !!orderId,
    queryKey: ["po-mail-order", orderId],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.po_mail_order, orderId))
        .then((response: any) => response.data as POMailOrderDetail),
  });

  const selectTheme = (theme: any) => ({
    ...theme,
    colors: { ...theme.colors, ...colors },
  });

  // Prefill the formats whenever a purchase order is loaded
  useEffect(() => {
    setSubmitted(false);
    setRows(
      (detailQuery.data?.formats ?? DEFAULT_FORMATS).map((format) => ({
        ...format,
        email: format.email || EMPTY_EMAIL,
        checked: format.active,
        message: "",
      })),
    );
  }, [detailQuery.data]);

  if (!allowed) {
    return <PermissionDenied />;
  }

  const updateRow = (key: string, changes: Partial<POMailRow>) => {
    setRows((current) =>
      current.map((row) => (row.key === key ? { ...row, ...changes } : row)),
    );
  };

  const checkedRows = rows.filter((row) => row.checked);

  const sendMail = () => {
    const detail = detailQuery.data;

    if (!detail) {
      return;
    }

    setSubmitted(true);

    if (checkedRows.some((row) => emailError(row.email))) {
      return;
    }

    setSending(true);

    const labels = Object.fromEntries(rows.map((row) => [row.key, row.label]));
    const failures = (failed: any[] = []) =>
      failed
        .map((item) => `${labels[item.key] ?? item.key}: ${item.error}`)
        .join("\n");

    api
      .post(apiUrl(ApiEndpoints.po_mail_send), {
        po_number: detail.order,
        mail: detail.mail,
        formats: checkedRows.map((row) => ({
          key: row.key,
          email: splitEmails(row.email).join(","),
          subject: row.subject,
          message: row.message,
        })),
      })
      .then((response: any) => {
        const failed = response.data?.failed ?? [];

        notifications.show({
          title: t`P.O. Mail sent`,
          message: t`Mail sent for ${detail.po_number}`,
          color: "green",
        });

        if (failed.length > 0) {
          notifications.show({
            title: t`Some mails were not sent`,
            message: failures(failed),
            color: "red",
            style: { whiteSpace: "pre-line" },
          });
        }
      })
      .catch((error: any) => {
        const data = error?.response?.data;

        notifications.show({
          title: t`P.O. Mail not sent`,
          message:
            data?.detail ||
            failures(data?.failed) ||
            t`Could not send the mail`,
          color: "red",
          style: { whiteSpace: "pre-line" },
        });
      })
      .finally(() => setSending(false));
  };

  return (
    <Stack>
      <PageDetail title={t`P.O. Mail`} />
      <Paper p="md" withBorder>
        <Stack gap="lg">
          <Box maw={460}>
            <Text component="label" htmlFor={orderFieldId} size="sm" fw={500}>
              {t`P.O. No`}
            </Text>
            <Select
              inputId={orderFieldId}
              isClearable
              options={ordersQuery.data ?? []}
              value={order}
              onChange={(option: any) => setOrder(option ?? null)}
              inputValue={search}
              onInputChange={(input, { action }) => {
                // Keep the typed search when the menu closes on a selection
                if (action === "input-change") setSearch(input);
              }}
              filterOption={null}
              isLoading={ordersQuery.isFetching}
              placeholder={t`Select P.O. No`}
              noOptionsMessage={() => t`No P.O. found`}
              menuPortalTarget={document.body}
              menuPosition="fixed"
              styles={selectFieldStyles}
              theme={selectTheme}
            />
          </Box>

          {orderId && detailQuery.isError && !detailQuery.isFetching && (
            <Alert color="red" title={t`Error`}>
              {t`Could not load the mail details for this purchase order`}
            </Alert>
          )}

          {rows.map((row, index) => (
            <Fieldset
              key={row.key}
              radius="md"
              legend={
                <Checkbox
                  px="xs"
                  checked={row.checked}
                  disabled={!row.active}
                  onChange={(event) =>
                    updateRow(row.key, {
                      checked: event.currentTarget.checked,
                    })
                  }
                  label={
                    <Group gap={6} align="baseline" wrap="nowrap">
                      <Text fw={500}>{row.label}</Text>
                      <Text size="xs" c="dimmed">
                        {t`Format`} {index + 1}
                      </Text>
                    </Group>
                  }
                />
              }
            >
              <Stack gap="sm">
                {!row.active && (
                  <Text size="sm" c="red">
                    {t`No active template is set for this format`}
                  </Text>
                )}
                <TextInput
                  label={t`E-mail ID`}
                  description={t`Separate multiple E-mail IDs with a comma`}
                  withAsterisk
                  disabled={!row.checked}
                  value={row.email}
                  error={submitted && row.checked ? emailError(row.email) : ""}
                  onChange={(event) =>
                    updateRow(row.key, { email: event.currentTarget.value })
                  }
                />
                <TextInput
                  label={t`Attachment Format`}
                  value={row.attachments}
                  disabled={!row.checked}
                  readOnly
                />
                <Textarea
                  label={t`Message`}
                  placeholder={t`Message`}
                  autosize
                  minRows={3}
                  maxRows={8}
                  disabled={!row.checked}
                  value={row.message}
                  onChange={(event) =>
                    updateRow(row.key, {
                      message: event.currentTarget.value,
                    })
                  }
                />
              </Stack>
            </Fieldset>
          ))}

          {rows.length > 0 && (
            <Group justify="center">
              <Button
                leftSection={<IconSend size={16} />}
                onClick={sendMail}
                loading={sending || detailQuery.isFetching}
                disabled={!detailQuery.data || checkedRows.length === 0}
                miw={140}
              >
                {t`Send`}
              </Button>
            </Group>
          )}
        </Stack>
      </Paper>
    </Stack>
  );
}
