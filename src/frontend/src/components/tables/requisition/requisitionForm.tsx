import React, { useState } from 'react';
import { Select, TextInput, Button, Group, Stack, Paper } from '@mantine/core';

export interface RequisitionFormData {
  viewType: string | null;
  stonePlace: string | null;
  stoneType: string | null;
  showRate: string | null;
  poNumber: string;
}

export interface RequisitionFormProps {
  onFetchData?: (data: RequisitionFormData) => void;
}

export function RequisitionForm({ onFetchData }: RequisitionFormProps) {
  const [viewType, setViewType] = useState<string | null>('Summary');
  const [stonePlace, setStonePlace] = useState<string | null>('');
  const [stoneType, setStoneType] = useState<string | null>('Diamond');
  const [showRate, setShowRate] = useState<string | null>('No');
  const [poNumber, setPoNumber] = useState<string>('');

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (onFetchData) {
      onFetchData({
        viewType,
        stonePlace,
        stoneType,
        showRate,
        poNumber,
      });
    }
  };

  return (
    <Paper p="md" radius="sm" withBorder>
      <form onSubmit={handleSubmit}>
        <Group align="flex-start" justify="space-between" gap="md">
          {/* Main Controls Grid */}
          <Stack gap="xs" style={{ flex: 1 }}>
            {/* Top Row: Dropdowns */}
            <Group grow gap="xs">
              <Select
                label="View Type"
                placeholder="Select View"
                data={['Summary', 'Details']}
                value={viewType}
                onChange={setViewType}
                variant="filled"
                styles={{
                  input: { backgroundColor: '#fff', border: '1px solid #ced4da' },
                }}
              />

              <Select
                label="Stone Place"
                placeholder="Stone Place"
                data={['None', 'Side', 'Center']}
                value={stonePlace}
                onChange={setStonePlace}
                variant="filled"
                styles={{
                  input: { backgroundColor: '#fff', border: '1px solid #ced4da' },
                }}
              />

              <Select
                label="Stone Type"
                placeholder="Select Type"
                data={['Diamond', 'Color Stone']}
                value={stoneType}
                onChange={setStoneType}
                variant="filled"
                styles={{
                  input: { backgroundColor: '#fff', border: '1px solid #ced4da' },
                }}
              />

              <Select
                label="Show Rate"
                placeholder="Select"
                data={['Yes', 'No']}
                value={showRate}
                onChange={setShowRate}
                variant="filled"
                styles={{
                  input: { backgroundColor: '#fff', border: '1px solid #ced4da' },
                }}
              />
            </Group>

            {/* Bottom Row: Purchase Order Text Input */}
            <TextInput
              placeholder="P.O."
              value={poNumber}
              onChange={(e) => setPoNumber(e.currentTarget.value)}
              styles={{
                input: { backgroundColor: '#fff', border: '1px solid #ced4da' },
              }}
            />
          </Stack>

          {/* Action Button */}
          <Button
            type="submit"
            size="md"
            style={{
              backgroundColor: '#1b5e83', // InvenTree signature dark teal/blue
              height: '84px', // Matches height of double-stacked row
              alignSelf: 'stretch',
              paddingLeft: '24px',
              paddingRight: '24px',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}
          >
            Get Data
          </Button>
        </Group>
      </form>
    </Paper>
  );
}