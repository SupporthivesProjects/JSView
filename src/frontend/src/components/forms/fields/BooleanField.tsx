import { t } from '@lingui/core/macro';
import { isTrue } from '@lib/functions/Conversion';
import type { ApiFormFieldType } from '@lib/types/Forms';
import { Group, Paper, Stack, Switch, Text } from '@mantine/core';
import { useId } from '@mantine/hooks';
import { IconCheck, IconX } from '@tabler/icons-react';
import { memo, useCallback, useEffect, useMemo } from 'react';
import type { FieldValues, UseControllerReturn } from 'react-hook-form';

function BooleanFieldComponent({
  controller,
  definition,
  fieldName,
  onChange
}: Readonly<{
  controller: UseControllerReturn<FieldValues, any>;
  definition: ApiFormFieldType;
  fieldName: string;
  onChange: (value: boolean) => void;
}>) {
  const fieldId = useId();

  const {
    field,
    fieldState: { error }
  } = controller;

  const { value } = field;

  // Set default value if value is undefined or otherwise empty
  useEffect(() => {
    if (value === undefined || value === null || value === '') {
      onChange(definition.default ?? false);
    }
  }, [value, definition]);

  // Coerce the value to a (stringified) boolean value
  const booleanValue: boolean = useMemo(() => {
    return isTrue(value ?? definition.default ?? false);
  }, [value]);

  const handleChange = useCallback(
    (event: any) => onChange(event.currentTarget.checked || false),
    [onChange]
  );

  const errorMessage = definition.error ?? error?.message;

  /* A bare <Switch> sits awkwardly next to full-height inputs when a form
   * lays its fields out in a grid, so 'boxed' fields render the switch inside
   * a bordered panel - label and description on the left, switch on the
   * right - which lines up with the neighbouring input boxes.
   */
  if (definition.boxed) {
    const { label, description, ...switchProps } = definition;

    return (
      <Paper
        withBorder
        radius='sm'
        p='xs'
        bg={
          booleanValue
            ? 'var(--mantine-color-default)'
            : 'var(--mantine-color-default)'
        }
        style={{
          // borderColor: booleanValue
          //   ? 'var(--mantine-color-green-filled)'
          //   : undefined,
          transition: 'background-color 150ms ease, border-color 150ms ease'
        }}
      >
        <Group justify='space-between' wrap='nowrap' gap='sm'>
          <Stack gap={2}>
            {label && (
              <Text size='sm' fw={500}>
                {label}
              </Text>
            )}
            <Text size='xs' c={booleanValue ? 'green' : 'dimmed'}>
              {booleanValue ? t`Enabled` : t`Disabled`}
            </Text>
            {description && (
              <Text size='xs' c='dimmed'>
                {description}
              </Text>
            )}
            {errorMessage && (
              <Text size='xs' c='red'>
                {errorMessage}
              </Text>
            )}
          </Stack>
          <Switch
            {...switchProps}
            defaultValue={undefined}
            checked={booleanValue}
            id={fieldId}
            aria-label={`boolean-field-${fieldName}`}
            radius='lg'
            size='md'
            color='green'
            thumbIcon={
              booleanValue ? (
                <IconCheck size={12} color='var(--mantine-color-green-6)' />
              ) : (
                <IconX size={12} color='var(--mantine-color-gray-6)' />
              )
            }
            error={!!errorMessage}
            onChange={handleChange}
          />
        </Group>
      </Paper>
    );
  }

  return (
    <Switch
      {...definition}
      defaultValue={undefined}
      checked={booleanValue}
      id={fieldId}
      aria-label={`boolean-field-${fieldName}`}
      radius='lg'
      size='sm'
      error={errorMessage}
      onChange={handleChange}
    />
  );
}

export const BooleanField = memo(BooleanFieldComponent);
