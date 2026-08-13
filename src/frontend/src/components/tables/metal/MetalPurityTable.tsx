import { t } from "@lingui/core/macro";
import { useCallback, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

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
import { BooleanColumn, DecimalColumn } from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import { metalPurityFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useApi } from "@context/ApiContext";
import { useUserState } from "@store/UserState";

/**
 * Table for displaying, creating, editing and deleting Metal Purity records
 */
export default function MetalPurityTable() {
  const table = useTable("metal-purities");

  const user = useUserState();
  const api = useApi();

  // The list endpoint only returns the related MetalType's primary key
  // (no nested "metal_type_detail" is provided by the backend serializer,
  // and we're not changing the backend to add one) - so fetch the small
  // list of metal types once ourselves and build a pk -> name lookup for
  // the column below, instead of showing a bare numeric id.
  const metalTypesQuery = useQuery({
    queryKey: ["metal-types-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.metal_type_list), { params: { limit: 1000 } })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
  });

  const metalTypeNameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (metalTypesQuery.data ?? []).forEach((metalType: any) => {
      map[metalType.pk] = metalType.name;
    });
    return map;
  }, [metalTypesQuery.data]);

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "metal_type",
        title: t`Metal Type`,
        sortable: true,
        switchable: false,
        render: (record: any) =>
          metalTypeNameByPk[record.metal_type] ?? record.metal_type,
      },
      {
        accessor: "name",
        sortable: true,
        switchable: false,
      },
      DecimalColumn({
        accessor: "purity",
        title: t`Purity (%)`,
        sortable: true,
      }),
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
  }, [metalTypeNameByPk]);

  // --- Create modal ----------------------------------------------------
  const newMetalPurity = useCreateApiFormModal({
    url: ApiEndpoints.metal_purity_list,
    title: t`Add Metal Purity`,
    fields: metalPurityFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedMetalPurity, setSelectedMetalPurity] = useState<
    number | undefined
  >(undefined);

  const editMetalPurity = useEditApiFormModal({
    url: ApiEndpoints.metal_purity_list,
    pk: selectedMetalPurity,
    title: t`Edit Metal Purity`,
    fields: metalPurityFields(),
    table: table,
  });

  const deleteMetalPurity = useDeleteApiFormModal({
    url: ApiEndpoints.metal_purity_list,
    pk: selectedMetalPurity,
    title: t`Delete Metal Purity`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedMetalPurity(record.pk);
            editMetalPurity.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedMetalPurity(record.pk);
            deleteMetalPurity.open();
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
        description: t`Show active metal purity grades`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-metal-purity"
        onClick={() => newMetalPurity.open()}
        tooltip={t`Add Metal Purity`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newMetalPurity.modal}
      {editMetalPurity.modal}
      {deleteMetalPurity.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.metal_purity_list)}
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
