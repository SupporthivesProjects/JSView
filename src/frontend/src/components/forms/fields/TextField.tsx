import { Textarea, TextInput } from '@mantine/core';
import { memo, useCallback, useEffect, useId, useMemo, useState } from 'react';
import type { FieldValues, UseControllerReturn } from 'react-hook-form';
import AutoFillRightSection from './AutoFillRightSection';

/*
 * Custom implementation of the mantine <TextInput> component,
 * used for rendering text input fields in forms.
 * Uses a debounced value to prevent excessive re-renders.
 */
function TextField({
  controller,
  fieldName,
  definition,
  placeholderAutofill,
  onChange,
  onKeyDown
}: Readonly<{
  controller: UseControllerReturn<FieldValues, any>;
  definition: any;
  fieldName: string;
  placeholderAutofill?: boolean;
  onChange: (value: any) => void;
  onKeyDown: (value: any) => void;
}>) {
  const fieldId = useId();
  const {
    field,
    fieldState: { error }
  } = controller;

  const { value } = field;

  const [textValue, setTextValue] = useState<string>(value || '');

  const onTextChange = useCallback(
    (value: any) => {
      setTextValue(value);
      onChange(value);
    },
    [onChange]
  );

  useEffect(() => {
    setTextValue(value || '');
  }, [value]);

  /* Construct a "cut-down" version of the definition,
   * which does not include any attributes that the lower components do not recognize
   */
  const fieldDefinition = useMemo(() => {
    return {
      ...definition,
      allow_blank: undefined,
      multiline: undefined,
      minRows: undefined,
      maxRows: undefined
    };
  }, [definition]);

  // Fields marked as 'multiline' render as a <Textarea> rather than a single
  // line <TextInput> - used for free-form notes / instruction fields.
  const InputComponent = definition.multiline ? Textarea : TextInput;

  const multilineProps = definition.multiline
    ? {
        autosize: true,
        minRows: definition.minRows ?? 3,
        maxRows: definition.maxRows ?? 8
      }
    : { type: definition.field_type };

  return (
    <InputComponent
      {...fieldDefinition}
      {...multilineProps}
      ref={field.ref}
      id={fieldId}
      aria-label={`text-field-${field.name}`}
      value={textValue || ''}
      error={definition.error ?? error?.message}
      radius='sm'
      onChange={(event) => onTextChange(event.currentTarget.value)}
      onBlur={(event) => {
        if (event.currentTarget.value != textValue) {
          onTextChange(event.currentTarget.value);
        }
      }}
      onKeyDown={(event) => {
        if (event.code === 'Enter') {
          // In a multiline field Enter inserts a newline, so it must not
          // reach the form-level "submit on Enter" handler (mod+Enter
          // still submits the form).
          if (definition.multiline) {
            return;
          }
          // Bypass debounce on enter key
          onTextChange(event.currentTarget.value);
        }
        onKeyDown(event.code);
      }}
      rightSection={
        placeholderAutofill && (
          <AutoFillRightSection
            value={textValue}
            fieldName={field.name}
            definition={definition}
            onChange={onChange}
          />
        )
      }
    />
  );
}

export default memo(TextField);
