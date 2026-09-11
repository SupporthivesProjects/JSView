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
import { BooleanColumn } from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import { findingTypeItems } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";
import { useApi } from "@context/ApiContext";
import { useQuery } from "@tanstack/react-query";

export default function FindingItemTable() {
  const table = useTable("finding-item");
  const user = useUserState();

  const api = useApi();

  const findingTypesQuery = useQuery({
    queryKey: ["finding-type-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.finding_type), { params: { limit: 1000 } })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
  });

  const findingTypeNameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (findingTypesQuery.data ?? []).forEach((findingType: any) => {
      map[findingType.pk] = findingType.name;
    });
    return map;
  }, [findingTypesQuery.data]);

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "finding_type",
        sortable: true,
        switchable: false,
        render: (record: any) =>
          findingTypeNameByPk[record.finding_type] ?? record.finding_type,
      },
      {
        accessor: "name",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "type",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "weight",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "metal",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "price",
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
  }, [findingTypeNameByPk]);

  // --- Create modal ----------------------------------------------------
  const newFindingItem = useCreateApiFormModal({
    url: ApiEndpoints.finding_item,
    title: t`Add Finding Item`,
    fields: findingTypeItems(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedFindingItem, setSelectedFindingItem] = useState<
    number | undefined
  >(undefined);

  const editFindingItem = useEditApiFormModal({
    url: ApiEndpoints.finding_item,
    pk: selectedFindingItem,
    title: t`Edit Finding Item`,
    fields: findingTypeItems(),
    table: table,
  });

  const deleteFindingItem = useDeleteApiFormModal({
    url: ApiEndpoints.finding_item,
    pk: selectedFindingItem,
    title: t`Delete Finding Item`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedFindingItem(record.pk);
            editFindingItem.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedFindingItem(record.pk);
            deleteFindingItem.open();
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
        description: t`Show active finding item`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-finding-item"
        onClick={() => newFindingItem.open()}
        tooltip={t`Add Finding Item`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newFindingItem.modal}
      {editFindingItem.modal}
      {deleteFindingItem.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.finding_item)}
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
