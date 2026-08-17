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
import { BooleanColumn, DecimalColumn, DescriptionColumn } from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import { masterCourierService } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

export default function CourierServiceTable() {
  const table = useTable("courier-service");

  const user = useUserState();

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "name",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "contact_person",
        title: t`Contact Person`,
        sortable: true,
        switchable: false,
      },
      {
        accessor: "phone",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "email",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "tracking_url",
        title: t`Tracking Url`,
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
  }, []);

  // --- Create modal ----------------------------------------------------
  const newCourierService = useCreateApiFormModal({
    url: ApiEndpoints.courier_service,
    title: t`Add Courier Service`,
    fields: masterCourierService(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedCourierService, setSelectedCourierService] = useState<
    number | undefined
  >(undefined);

  const editCourierService = useEditApiFormModal({
    url: ApiEndpoints.courier_service,
    pk: selectedCourierService,
    title: t`Edit CourierService`,
    fields: masterCourierService(),
    table: table,
  });

  const deleteCourierService = useDeleteApiFormModal({
    url: ApiEndpoints.courier_service,
    pk: selectedCourierService,
    title: t`Delete CourierService`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedCourierService(record.pk);
            editCourierService.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedCourierService(record.pk);
            deleteCourierService.open();
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
        description: t`Show active courier service`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-courier-service"
        onClick={() => newCourierService.open()}
        tooltip={t`Add Courier Service`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newCourierService.modal}
      {editCourierService.modal}
      {deleteCourierService.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.courier_service)}
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
