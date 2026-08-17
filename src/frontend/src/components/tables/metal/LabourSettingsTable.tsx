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
import { LabourSettingFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";
import { useApi } from "@context/ApiContext";
import { useQuery } from "@tanstack/react-query";

export default function LabourSettingTable() {
  const table = useTable("labour-settings");
  const user = useUserState();

  const api = useApi();

  const settingsQuery = useQuery({
    queryKey: ["setting-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.master_setting), { params: { limit: 1000 } })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
  });

  const settingNameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (settingsQuery.data ?? []).forEach((setting: any) => {
      map[setting.pk] = setting.name;
    });
    return map;
  }, [settingsQuery.data]);

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "name",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "setting",
        title: t`Setting`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "charge_type",
        title: t`Charge Type`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "rate",
        title: t`Rate`,
        sortable: true,
        switchable: true,
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
  }, [settingNameByPk]);

  // --- Create modal ----------------------------------------------------
  const newLabourSettings = useCreateApiFormModal({
    url: ApiEndpoints.labour_setting,
    title: t`Add Labour Setting`,
    fields: LabourSettingFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedLabourSetting, setSelectedLabourSetting] = useState<
    number | undefined
  >(undefined);

  const editLabourSetting = useEditApiFormModal({
    url: ApiEndpoints.labour_setting,
    pk: selectedLabourSetting,
    title: t`Edit Labour Setting`,
    fields: LabourSettingFields(),
    table: table,
  });

  const deleteLabourSetting = useDeleteApiFormModal({
    url: ApiEndpoints.labour_setting,
    pk: selectedLabourSetting,
    title: t`Delete Labour Setting`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedLabourSetting(record.pk);
            editLabourSetting.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedLabourSetting(record.pk);
            deleteLabourSetting.open();
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
        description: t`Show active labour setting`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-labour-setting"
        onClick={() => newLabourSettings.open()}
        tooltip={t`Add Labour Setting`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newLabourSettings.modal}
      {editLabourSetting.modal}
      {deleteLabourSetting.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.labour_setting)}
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
