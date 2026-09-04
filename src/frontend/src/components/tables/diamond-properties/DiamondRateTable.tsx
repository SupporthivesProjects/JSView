import { t } from "@lingui/core/macro";
import { useCallback, useMemo, useState } from "react";

import { AddItemButton } from "@lib/components/AddItemButton";
import {
  type RowAction,
  RowDeleteAction,
  RowEditAction,
} from "@lib/components/RowActions";
import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { UserRoles } from "@lib/enums/Roles";
import { apiUrl } from "@lib/functions/Api";
import useTable from "@lib/hooks/UseTable";
import type { TableFilter } from "@lib/index";
import type { TableColumn } from "@lib/types/Tables";
import { BooleanColumn, DescriptionColumn } from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import { diamondRateFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useApi } from "@context/ApiContext";
import { useUserState } from "@store/UserState";
import { useQuery, useQueryClient } from "@tanstack/react-query";

const DIAMOND_RATE_LOOKUP_QUERY_KEYS = [
  ["diamond-shape-lookup"],
  ["diamond-size-lookup"],
  ["diamond-stone-lookup"],
  ["diamond-color-lookup"],
  ["diamond-cut-lookup"],
  ["diamond-quality-lookup"],
];

/**
 * Table for displaying, creating, editing and deleting Metal Type records
 */
export default function DiamondRateTable() {
  const table = useTable("diamond-rate");

  const api = useApi();
  const user = useUserState();
  const queryClient = useQueryClient();

  const refreshLookupTables = useCallback(() => {
    DIAMOND_RATE_LOOKUP_QUERY_KEYS.forEach((queryKey) => {
      queryClient.invalidateQueries({ queryKey });
    });
  }, [queryClient]);

  // Diamond Shape
  const diamondShapeQuery = useQuery({
    queryKey: ["diamond-shape-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.diamond_shape_list), {
          params: { limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
    refetchOnMount: "always",
  });
  const diamondShapeNameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (diamondShapeQuery.data ?? []).forEach((diamondShape: any) => {
      map[diamondShape.pk] = diamondShape.name;
    });
    return map;
  }, [diamondShapeQuery.data]);

  // Diamond Size
  const diamondSizeQuery = useQuery({
    queryKey: ["diamond-size-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.diamond_size_list), {
          params: { limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
    refetchOnMount: "always",
  });
  const diamondSizeNameByPk = useMemo(() => {
    const map: Record<number, string> = {};

    (diamondSizeQuery.data ?? []).forEach((diamondSize: any) => {
      map[diamondSize.pk] = diamondSize.mm_size;
    });

    return map;
  }, [diamondSizeQuery.data]);

  // Diamond Diamond
  const diamondStoneQuery = useQuery({
    queryKey: ["diamond-stone-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.diamond_stone_list), {
          params: { limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
    refetchOnMount: "always",
  });
  const diamondStoneNameByPk = useMemo(() => {
    const map: Record<number, string> = {};

    (diamondStoneQuery.data ?? []).forEach((diamondStone: any) => {
      map[diamondStone.pk] = diamondStone.name;
    });

    return map;
  }, [diamondStoneQuery.data]);

  // Diamond Color
  const diamondColorQuery = useQuery({
    queryKey: ["diamond-color-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.diamond_color_list), {
          params: { limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
    refetchOnMount: "always",
  });
  const diamondColorNameByPk = useMemo(() => {
    const map: Record<number, string> = {};

    (diamondColorQuery.data ?? []).forEach((diamondColor: any) => {
      map[diamondColor.pk] = diamondColor.name;
    });

    return map;
  }, [diamondColorQuery.data]);

  // Diamond Cut
  const diamondCutQuery = useQuery({
    queryKey: ["diamond-cut-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.diamond_cut_list), {
          params: { limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
    refetchOnMount: "always",
  });
  const diamondCutNameByPk = useMemo(() => {
    const map: Record<number, string> = {};

    (diamondCutQuery.data ?? []).forEach((diamondCut: any) => {
      map[diamondCut.pk] = diamondCut.name;
    });

    return map;
  }, [diamondCutQuery.data]);

  // Diamond Quality
  const diamondQualityQuery = useQuery({
    queryKey: ["diamond-quality-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.diamond_quality_list), {
          params: { limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
    refetchOnMount: "always",
  });
  const diamondQualityNameByPk = useMemo(() => {
    const map: Record<number, string> = {};

    (diamondQualityQuery.data ?? []).forEach((diamondQuality: any) => {
      map[diamondQuality.pk] = diamondQuality.name;
    });

    return map;
  }, [diamondQualityQuery.data]);

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "shape",
        sortable: true,
        switchable: false,
        render: (record: any) =>
          diamondShapeNameByPk[record.shape] ?? record.shape,
      },
      {
        accessor: "mm_size",
        title: t`Size in mm`,
        sortable: true,
        switchable: false,
        render: (record: any) =>
          diamondSizeNameByPk[record.mm_size] ?? record.mm_size,
      },
      {
        accessor: "Diamond Stone",
        sortable: true,
        switchable: false,
        render: (record: any) =>
          diamondStoneNameByPk[record.stone] ?? record.stone,
      },
      {
        accessor: "color",
        sortable: true,
        switchable: false,
        render: (record: any) =>
          diamondColorNameByPk[record.color] ?? record.color,
      },
      {
        accessor: "cut",
        sortable: true,
        switchable: false,
        render: (record: any) => diamondCutNameByPk[record.cut] ?? record.cut,
      },
      {
        accessor: "quality",
        sortable: true,
        switchable: false,
        render: (record: any) =>
          diamondQualityNameByPk[record.quality] ?? record.quality,
      },
      {
        accessor: "pointer",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "rate",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "pc",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "customers",
        sortable: true,
        switchable: false,
      },
      BooleanColumn({
        accessor: "active",
      }),
      {
        accessor: "created_at",
        title: t`Created`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "updated_at",
        title: t`Updated`,
        sortable: true,
        switchable: true,
      },
    ];
  }, [
    diamondShapeNameByPk,
    diamondSizeNameByPk,
    diamondStoneNameByPk,
    diamondColorNameByPk,
    diamondCutNameByPk,
    diamondQualityNameByPk,
  ]);

  // --- Create modal ----------------------------------------------------
  const newDiamondRate = useCreateApiFormModal({
    url: ApiEndpoints.diamond_rate_list,
    title: t`Add Diamond Rate`,
    fields: diamondRateFields(),
    table: table,
    onFormSuccess: () => {
      refreshLookupTables();
    },
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedDiamondRate, setSelectedDiamondRate] = useState<
    number | undefined
  >(undefined);

  const editDiamondRate = useEditApiFormModal({
    url: ApiEndpoints.diamond_rate_list,
    pk: selectedDiamondRate,
    title: t`Edit Diamond Rate`,
    fields: diamondRateFields(),
    table: table,
    onFormSuccess: () => {
      refreshLookupTables();
    },
  });

  const deleteDiamondRate = useDeleteApiFormModal({
    url: ApiEndpoints.diamond_rate_list,
    pk: selectedDiamondRate,
    title: t`Delete Diamond Rate`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedDiamondRate(record.pk);
            editDiamondRate.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedDiamondRate(record.pk);
            deleteDiamondRate.open();
          },
        }),
      ];
    },
    [user],
  );

  // --- Table-level filters ----------------------------------------------
  const tableFilters: TableFilter[] = useMemo(() => {
    return [
      {
        name: "active",
        label: t`Active`,
        description: t`Show active diamond qualities`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-diamond-rate"
        onClick={() => newDiamondRate.open()}
        tooltip={t`Add Diamond Rate`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newDiamondRate.modal}
      {editDiamondRate.modal}
      {deleteDiamondRate.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.diamond_rate_list)}
        tableState={table}
        columns={columns}
        props={{
          rowActions: rowActions,
          tableActions: tableActions,
          tableFilters: tableFilters,
          enableDownload: true,
        }}
      />
    </>
  );
}
