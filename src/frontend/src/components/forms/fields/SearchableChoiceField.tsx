import { t } from '@lingui/core/macro';
import { Group, Input } from '@mantine/core';
import { useId } from '@mantine/hooks';
import { memo, useCallback, useMemo } from 'react';
import type { FieldValues, UseControllerReturn } from 'react-hook-form';
import Select from 'react-select';

import type { ApiFormFieldType } from '@lib/types/Forms';
import Expand from '../../ui/items/Expand';
import { selectFieldStyles, useSelectFieldColors } from './SelectFieldTheme';

/**
 * Render a 'choice' field using the same searchable select control as a
 * related field, so a choice field sitting alongside related fields (such as
 * the Sieve Size / MM Size pair on a cost card stone line) matches them.
 *
 * The choices are static - unlike a related field there is nothing to search
 * for against the API - and the raw choice value is stored, not a primary key.
 */
function SearchableChoiceFieldComponent({
  controller,
  definition
}: Readonly<{
  controller: UseControllerReturn<FieldValues, any>;
  definition: ApiFormFieldType;
  fieldName: string;
}>) {
  const fieldId = useId();

  const {
    field,
    fieldState: { error }
  } = controller;

  const { value } = field;

  const options: any[] = useMemo(() => {
    return (definition.choices ?? []).map((choice) => ({
      value: choice.value.toString(),
      label: choice.display_name ?? choice.value.toString()
    }));
  }, [definition.choices]);

  const currentValue = useMemo(() => {
    if (value === undefined || value === null || value === '') {
      return null;
    }

    return options.find((option) => option.value === value.toString()) ?? null;
  }, [options, value]);

  const onChange = useCallback(
    (option: any) => {
      const newValue = option?.value ?? null;

      // Prevent blank values if the field is required
      if (definition.required && !newValue) {
        return;
      }

      field.onChange(newValue);

      // Run custom callback for this field (if provided)
      definition.onValueChange?.(newValue);
    },
    [field.onChange, definition]
  );

  const colors = useSelectFieldColors();

  return (
    <Input.Wrapper
      label={definition.label}
      description={definition.description}
      required={definition.required}
      error={definition.error ?? error?.message}
      styles={{ description: { paddingBottom: '5px' } }}
    >
      <Group justify='space-between' wrap='nowrap' gap={3}>
        <Expand>
          <Select
            id={fieldId}
            aria-label={`choice-field-${field.name}`}
            ref={field.ref}
            options={options}
            value={currentValue}
            onChange={onChange}
            isClearable={(definition.clearable ?? true) && !definition.required}
            isDisabled={definition.disabled}
            isSearchable={true}
            placeholder={definition.placeholder || `${t`Search`}...`}
            menuPortalTarget={document.body}
            noOptionsMessage={() => t`No results found`}
            menuPosition='fixed'
            styles={selectFieldStyles}
            theme={(theme) => {
              return {
                ...theme,
                colors: {
                  ...theme.colors,
                  ...colors
                }
              };
            }}
          />
        </Expand>
      </Group>
    </Input.Wrapper>
  );
}

export const SearchableChoiceField = memo(SearchableChoiceFieldComponent);
