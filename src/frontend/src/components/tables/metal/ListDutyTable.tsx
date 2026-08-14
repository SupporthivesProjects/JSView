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
import {
  BooleanColumn,
  DecimalColumn,
  DescriptionColumn,
} from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import { ListDutyFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useApi } from "@context/ApiContext";
import { useUserState } from "@store/UserState";

export default function ListDutyTable() {
  const table = useTable("list-duty");

  const user = useUserState();
  const api = useApi();

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
      DecimalColumn({
        accessor: "duty",
        title: t`Duty (%)`,
        sortable: true,
      }),
      {
        accessor: "markup",
        sortable: true,
        switchable: false,
      },
      DescriptionColumn({}),
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
  const newListDuty = useCreateApiFormModal({
    url: ApiEndpoints.list_duty,
    title: t`Add List Duty`,
    fields: ListDutyFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedListDuty, setSelectedListDuty] = useState<number | undefined>(
    undefined,
  );

  const editListDuty = useEditApiFormModal({
    url: ApiEndpoints.list_duty,
    pk: selectedListDuty,
    title: t`Edit List Duty`,
    fields: ListDutyFields(),
    table: table,
  });

  const deleteListDuty = useDeleteApiFormModal({
    url: ApiEndpoints.list_duty,
    pk: selectedListDuty,
    title: t`Delete List Duty`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedListDuty(record.pk);
            editListDuty.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedListDuty(record.pk);
            deleteListDuty.open();
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
        description: t`Show active duty list`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-metal-purity"
        onClick={() => newListDuty.open()}
        tooltip={t`Add Metal Purity`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newListDuty.modal}
      {editListDuty.modal}
      {deleteListDuty.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.list_duty)}
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
