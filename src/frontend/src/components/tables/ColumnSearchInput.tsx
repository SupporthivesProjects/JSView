import { t } from "@lingui/core/macro";
import { useEffect, useRef, useState } from "react";

import { ActionIcon, Stack, Text, TextInput } from "@mantine/core";
import { IconSearch, IconX } from "@tabler/icons-react";

/*
 * Search box rendered inside a column header filter popover.
 *
 * The typed value is held locally and pushed upwards after a short delay, so
 * that re-rendering the (filtered) table does not interfere with typing.
 */
export function ColumnSearchInput({
  label,
  placeholder,
  value,
  onChange,
}: Readonly<{
  label: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
}>) {
  const [text, setText] = useState<string>(value);

  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  useEffect(() => {
    if (text === value) {
      return;
    }

    const timer = setTimeout(() => onChangeRef.current(text), 250);

    return () => clearTimeout(timer);
  }, [text, value]);

  return (
    <Stack gap={5} p={3} miw={230}>
      <Text size="sm" fw={600}>
        {label}
      </Text>
      <TextInput
        autoFocus
        value={text}
        placeholder={placeholder ?? t`Search`}
        aria-label={`column-search-${label}`}
        leftSection={<IconSearch size={14} />}
        onChange={(event) => setText(event.currentTarget.value)}
        rightSection={
          text ? (
            <ActionIcon
              color="red"
              variant="transparent"
              size="sm"
              aria-label="clear-column-search"
              onClick={() => setText("")}
            >
              <IconX size={14} />
            </ActionIcon>
          ) : null
        }
      />
    </Stack>
  );
}
