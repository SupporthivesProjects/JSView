import { t } from "@lingui/core/macro";
import { showNotification } from "@mantine/notifications";
import { useQuery } from "@tanstack/react-query";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { apiUrl } from "@lib/functions/Api";
import type { ApiFormFieldSet } from "@lib/types/Forms";
import { useApi } from "@context/ApiContext";
import { showApiErrorMessage } from "@helpers/notifications";
import {
  PURCHASE_REQUEST_FORM_GRID_COLUMNS,
  picturePresentationFields,
} from "../../forms/CommonForms";
import { useCreateApiFormModal } from "../../../hooks/UseForm";
import useDataOutput from "../../../hooks/UseDataOutput";
import useNameLookup from "../../../hooks/UseNameLookup";

/*
 * Pricing inputs on the Presentation form which both exports accept as
 * overrides. The Picture Presentation export picks them up from the submitted
 * form data; the Cost Card Representation export runs outside the submit, so
 * their current values are mirrored into component state as they are edited.
 */
const PRESENTATION_OVERRIDE_FIELDS = [
  "gold_troy_ounce",
  "silver_troy_ounce",
  "duty_pct",
  "margin_pct",
] as const;

/*
 * Resolved display names for the property tables a stone line points at.
 *
 * Diamond lines and color stone lines reference different sets of tables
 * (DiamondShape vs ColorStoneShape, and so on), so each kind of line is
 * rendered with its own maps.
 */
type StoneNameMaps = {
  stone: Record<number, string>;
  shape: Record<number, string>;
  mm_size: Record<number, string>;
  color: Record<number, string>;
  cut: Record<number, string>;
  quality: Record<number, string>;
};

/*
 * Turn one diamond / color stone line into a row of the Picture Presentation
 * stone listing: the foreign keys on the line are swapped for the names they
 * point at, and the cost card's style number is carried along so that rows
 * coming from different cards can be told apart.
 *
 * `id` is what the form's table field keys the row on, so it has to stay
 * unique across both line types (their primary keys are independent).
 */
function picturePresentationStoneRow(
  line: any,
  names: StoneNameMaps,
  styleNo: string,
  id: string,
) {
  const label = (field: keyof StoneNameMaps) =>
    names[field][line[field]] ?? line[field] ?? "";

  return {
    id: id,
    style_no: styleNo,
    shape: label("shape"),
    mm_size: label("mm_size"),
    sieve_size: line.sieve_size ?? "",
    stone: label("stone"),
    color: label("color"),
    cut: label("cut"),
    quality: label("quality"),
    pointer: line.pointer ?? "",
    rate: line.rate ?? "",
  };
}

export type PicturePresentationSeed = {
  // Cost card records the form starts out with - their PKs fill the style
  // picker and their figures pre-fill the pricing inputs
  records: any[];
  // Purchase order the form starts out with, if any
  po?: number | null;
};

/**
 * The Presentation modal (Picture Presentation / Cost Card Representation
 * exports), shared by the cost card listing and the Picture Presentation
 * report so both open the same form.
 *
 * @param knownCards - Cost card records the caller already holds; any card
 * picked on the form which is not among these (or the seed records) is
 * fetched individually so its stone lines can be listed.
 */
export default function usePicturePresentation({
  knownCards = [],
}: Readonly<{ knownCards?: any[] }> = {}) {
  const api = useApi();

  // Metal purity - only needed to tell gold apart from silver when pre-filling
  // the troy ounce price on the Picture Presentation form
  const metalPurityQuery = useQuery({
    queryKey: ["cost-card-metal-purity-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.metal_purity_list), {
          params: { limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
  });
  const metalPurityNameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (metalPurityQuery.data ?? []).forEach((purity: any) => {
      map[purity.pk] = purity.name;
    });
    return map;
  }, [metalPurityQuery.data]);

  /*
   * Stone line properties, used to render the Picture Presentation stone
   * listing: the lines nested on a cost card record hold primary keys, so the
   * names they point at are pulled in separately. The query keys are shared
   * with the cost card Diamond / Color Stone tabs, so the lookups are only
   * fetched once between them.
   */
  const { nameByPk: diamondStoneByPk } = useNameLookup(
    ApiEndpoints.diamond_stone_list,
    "cost-card-diamond-stone-lookup",
  );
  const { nameByPk: diamondShapeByPk } = useNameLookup(
    ApiEndpoints.diamond_shape_list,
    "cost-card-diamond-shape-lookup",
  );
  const { nameByPk: diamondSizeByPk } = useNameLookup(
    ApiEndpoints.diamond_size_list,
    "cost-card-diamond-size-lookup",
    "mm_size",
  );
  const { nameByPk: diamondColorByPk } = useNameLookup(
    ApiEndpoints.diamond_color_list,
    "cost-card-diamond-color-lookup",
  );
  const { nameByPk: diamondCutByPk } = useNameLookup(
    ApiEndpoints.diamond_cut_list,
    "cost-card-diamond-cut-lookup",
  );
  const { nameByPk: diamondQualityByPk } = useNameLookup(
    ApiEndpoints.diamond_quality_list,
    "cost-card-diamond-quality-lookup",
  );

  const { nameByPk: colorStoneByPk } = useNameLookup(
    ApiEndpoints.color_stone_type_list,
    "cost-card-colorstone-stone-lookup",
  );
  const { nameByPk: colorStoneShapeByPk } = useNameLookup(
    ApiEndpoints.color_stone_shape_list,
    "cost-card-colorstone-shape-lookup",
  );
  const { nameByPk: colorStoneSizeByPk } = useNameLookup(
    ApiEndpoints.color_stone_size_list,
    "cost-card-colorstone-size-lookup",
  );
  const { nameByPk: colorStoneColorByPk } = useNameLookup(
    ApiEndpoints.color_stone_color_list,
    "cost-card-colorstone-color-lookup",
  );
  const { nameByPk: colorStoneCutByPk } = useNameLookup(
    ApiEndpoints.color_stone_cut_list,
    "cost-card-colorstone-cut-lookup",
  );
  const { nameByPk: colorStoneQualityByPk } = useNameLookup(
    ApiEndpoints.color_stone_quality_list,
    "cost-card-colorstone-quality-lookup",
  );

  const diamondStoneNames: StoneNameMaps = useMemo(
    () => ({
      stone: diamondStoneByPk,
      shape: diamondShapeByPk,
      mm_size: diamondSizeByPk,
      color: diamondColorByPk,
      cut: diamondCutByPk,
      quality: diamondQualityByPk,
    }),
    [
      diamondStoneByPk,
      diamondShapeByPk,
      diamondSizeByPk,
      diamondColorByPk,
      diamondCutByPk,
      diamondQualityByPk,
    ],
  );

  const colorStoneNames: StoneNameMaps = useMemo(
    () => ({
      stone: colorStoneByPk,
      shape: colorStoneShapeByPk,
      mm_size: colorStoneSizeByPk,
      color: colorStoneColorByPk,
      cut: colorStoneCutByPk,
      quality: colorStoneQualityByPk,
    }),
    [
      colorStoneByPk,
      colorStoneShapeByPk,
      colorStoneSizeByPk,
      colorStoneColorByPk,
      colorStoneCutByPk,
      colorStoneQualityByPk,
    ],
  );

  const [exportId, setExportId] = useState<number | undefined>(undefined);

  useDataOutput({
    title: t`Exporting Picture Presentation`,
    id: exportId,
  });

  const [representationId, setRepresentationId] = useState<number | undefined>(
    undefined,
  );

  useDataOutput({
    title: t`Exporting Cost Card Representation`,
    id: representationId,
  });

  // `cost_card_ids` is not set here: it is assembled at submit time from the
  // style numbers shown on the form (which are pre-filled from the seed).
  const picturePresentationParams = useMemo(
    () => new URLSearchParams({ export: "true", export_format: "xlsx" }),
    [],
  );

  const [picturePresentationOpen, setPicturePresentationOpen] =
    useState<boolean>(false);

  // The cost card records the form was opened with
  const [seedRecords, setSeedRecords] = useState<any[]>([]);

  const seedPks = useMemo(
    () => seedRecords.map((record: any) => Number(record.pk)),
    [seedRecords],
  );

  // The cost cards the modal is currently working with. Seeded when the form
  // is opened, and kept in step with the style-number picker afterwards, so
  // the stone preview always matches what will be exported.
  const [picturePresentationCards, setPicturePresentationCards] = useState<
    number[]
  >([]);

  // The purchase order selected on the form (if any). It restricts the
  // style-number picker to the cost cards linked to that order.
  const [picturePresentationPo, setPicturePresentationPo] = useState<
    number | null
  >(null);

  // The purchase order the form was opened with, used to pre-fill the field
  const [seedPo, setSeedPo] = useState<number | null>(null);

  // The pricing overrides as they currently stand on the form. Seeded when the
  // form is opened, then kept in step with the inputs so the Cost Card
  // Representation export sends what is on screen.
  const [presentationOverrides, setPresentationOverrides] = useState<
    Record<string, any>
  >({});

  const loadedCards = useMemo(
    () => [...knownCards, ...seedRecords],
    [knownCards, seedRecords],
  );

  /*
   * Cost cards picked on the form which the caller has not loaded. The style
   * picker is filtered independently of the caller (and, with a P.O. selected,
   * lists that order's line items instead), so it can offer cards which are
   * not already held - fetch those individually so their stone lines are
   * listed too. A card which cannot be fetched is simply left out.
   */
  const missingCardPks = useMemo(() => {
    const loaded = new Set(loadedCards.map((record: any) => record.pk));
    return picturePresentationCards.filter((pk) => !loaded.has(pk));
  }, [loadedCards, picturePresentationCards]);

  const missingCardsQuery = useQuery({
    queryKey: ["picture-presentation-cards", missingCardPks.join(",")],
    enabled: picturePresentationOpen && missingCardPks.length > 0,
    staleTime: 60 * 1000,
    queryFn: () =>
      Promise.all(
        missingCardPks.map((pk) =>
          api
            .get(apiUrl(ApiEndpoints.cost_card, pk))
            .then((response) => response.data)
            .catch(() => null),
        ),
      ).then((records) => records.filter((record) => !!record)),
  });

  /*
   * Every stone line on the selected cost cards, one row each.
   *
   * The export endpoint also returns a stone summary, but it pools the lines
   * and keeps only one row per distinct combination - two cards carrying the
   * same stone would show up once. The rows are built here instead, from the
   * lines the cost card records already carry, so nothing is collapsed.
   */
  const picturePresentationStones = useMemo(() => {
    const cardByPk: Record<number, any> = {};

    for (const record of [...loadedCards, ...(missingCardsQuery.data ?? [])]) {
      cardByPk[record.pk] = record;
    }

    const rows: any[] = [];

    for (const pk of picturePresentationCards) {
      const card = cardByPk[pk];

      if (!card) {
        continue;
      }

      const styleNo = card.our_style_no ?? "";

      (card.diamond_lines ?? []).forEach((line: any, index: number) =>
        rows.push(
          picturePresentationStoneRow(
            line,
            diamondStoneNames,
            styleNo,
            `${pk}-diamond-${line.id ?? index}`,
          ),
        ),
      );

      (card.colorstone_lines ?? []).forEach((line: any, index: number) =>
        rows.push(
          picturePresentationStoneRow(
            line,
            colorStoneNames,
            styleNo,
            `${pk}-colorstone-${line.id ?? index}`,
          ),
        ),
      );
    }

    return rows;
  }, [
    loadedCards,
    missingCardsQuery.data,
    picturePresentationCards,
    diamondStoneNames,
    colorStoneNames,
  ]);

  /*
   * The pricing inputs apply to the export as a whole, so a figure is only
   * pre-filled when every seeded card agrees on it - otherwise the field is
   * left empty rather than presenting one card's number as if it covered all
   * of them. The troy ounce price is split by metal the same way the export
   * itself splits it: on the metal purity name.
   */
  const pricingValues = useCallback(
    (records: any[]) => {
      const isSilver = (record: any) =>
        (metalPurityNameByPk[record.metal_purity] ?? "")
          .toLowerCase()
          .includes("silver");

      const sharedValue = (records: any[], field: string) => {
        let shared: any;

        for (const record of records) {
          const value = record?.[field];

          if (value === null || value === undefined || value === "") {
            return undefined;
          }

          if (shared === undefined) {
            shared = value;
          } else if (String(shared) !== String(value)) {
            return undefined;
          }
        }

        return shared;
      };

      return {
        duty_pct: sharedValue(records, "duty_pct"),
        margin_pct: sharedValue(records, "margin_pct"),
        gold_troy_ounce: sharedValue(
          records.filter((record: any) => !isSilver(record)),
          "troy_ounce_price",
        ),
        silver_troy_ounce: sharedValue(
          records.filter((record: any) => isSilver(record)),
          "troy_ounce_price",
        ),
      };
    },
    [metalPurityNameByPk],
  );

  const picturePresentationValues = useMemo(() => {
    return {
      // Always handed to the field (even when empty), so that dropping the
      // cards which do not belong to a newly selected P.O. also clears them
      // from the picker
      stylenumber: picturePresentationCards,
      ...(seedPo ? { ponumber: seedPo } : {}),
      ...pricingValues(seedRecords),
    };
  }, [seedRecords, seedPo, picturePresentationCards, pricingValues]);

  const picturePresentationFormFields = useMemo((): ApiFormFieldSet => {
    const fields = picturePresentationFields(picturePresentationPo);

    const values: Record<string, any> = {
      ...picturePresentationValues,
      stones: picturePresentationStones,
    };

    const prefilled: ApiFormFieldSet = {};

    for (const [name, field] of Object.entries(fields)) {
      const value = values[name];
      prefilled[name] = value === undefined ? field : { ...field, value };
    }

    // Track the pricing inputs, so the Cost Card Representation export - which
    // does not go through the form submit - picks up any edits made here
    for (const name of PRESENTATION_OVERRIDE_FIELDS) {
      prefilled[name] = {
        ...prefilled[name],
        onValueChange: (value: any) =>
          setPresentationOverrides((current) => ({
            ...current,
            [name]: value,
          })),
      };
    }

    // Track the picker, so removing a style from the form also removes its
    // stones from the preview (and the card from the export)
    prefilled.stylenumber = {
      ...prefilled.stylenumber,
      onValueChange: (value: any) => {
        const ids = Array.isArray(value) ? value : value ? [value] : [];
        setPicturePresentationCards(ids.map((pk: any) => Number(pk)));
      },
    };

    /*
     * Selecting a P.O. narrows the style picker to the cost cards that order
     * is linked to. The order carries its line items with it, so the cards
     * already picked which are *not* on the order are dropped here - leaving
     * them selected would export styles the order does not cover.
     */
    prefilled.ponumber = {
      ...prefilled.ponumber,
      onValueChange: (value: any, record?: any) => {
        const pk = value ? Number(value) : null;

        setPicturePresentationPo(pk);

        if (!pk) {
          return;
        }

        const linked = new Set<number>(
          (record?.lines ?? [])
            .map((line: any) => line?.costcardid)
            .filter((id: any) => !!id)
            .map((id: any) => Number(id)),
        );

        setPicturePresentationCards((current) =>
          current.filter((id) => linked.has(id)),
        );
      },
    };

    return prefilled;
  }, [
    picturePresentationValues,
    picturePresentationStones,
    picturePresentationPo,
  ]);

  // The export view filters on `cost_card_ids`, and the style-number picker
  // returns cost card PKs - so fold them together into that one parameter.
  const processPicturePresentationData = useCallback(
    (data: any) => {
      const { stylenumber, ...rest } = data;

      const picked = Array.isArray(stylenumber)
        ? stylenumber
        : stylenumber
          ? [stylenumber]
          : [];

      // The picker starts out holding the seeded cards, so it is what the user
      // last said should be exported; fall back to the seed only if they
      // emptied it entirely. With a P.O. selected there is no fallback: the
      // seeded cards are not necessarily linked to that order.
      const ids = picked.length > 0 || rest.ponumber ? picked : seedPks;

      if (ids.length === 0) {
        return rest;
      }

      return { ...rest, cost_card_ids: Array.from(new Set(ids)).join(",") };
    },
    [seedPks],
  );

  /*
   * The Cost Card Representation export builds a different sheet from the same
   * cost cards and pricing overrides, so it runs from a button on the form
   * rather than by submitting it - the request is issued here instead, and its
   * data output is handed to the same download monitor the submit uses.
   */
  const representationRunning = useRef<boolean>(false);
  const closePicturePresentation = useRef<() => void>(() => {});

  const exportCostCardRepresentation = useCallback(async () => {
    if (representationRunning.current) {
      return;
    }

    // Same fallback as the submit: the picker holds what the user last said
    // should be exported, and only an emptied (P.O.-less) form falls back to
    // the seeded cards
    const ids =
      picturePresentationCards.length > 0 || picturePresentationPo
        ? picturePresentationCards
        : seedPks;

    if (ids.length === 0) {
      showNotification({
        title: t`Cost Card Representation`,
        message: t`Select at least one cost card`,
        color: "red",
      });
      return;
    }

    const params = new URLSearchParams();

    // `cost_card_ids` is repeated once per cost card
    Array.from(new Set(ids)).forEach((pk) =>
      params.append("cost_card_ids", String(pk)),
    );

    for (const name of PRESENTATION_OVERRIDE_FIELDS) {
      const value = presentationOverrides[name];

      if (value !== undefined && value !== null && value !== "") {
        params.append(name, String(value));
      }
    }

    representationRunning.current = true;

    try {
      const response = await api.get(
        apiUrl(ApiEndpoints.cost_card_representation),
        { params: params, timeout: 30 * 1000 },
      );

      setRepresentationId(response.data?.pk);
      closePicturePresentation.current();
    } catch (error: any) {
      showApiErrorMessage({
        error: error,
        title: t`Cost Card Representation`,
      });
    } finally {
      representationRunning.current = false;
    }
  }, [
    picturePresentationCards,
    picturePresentationPo,
    presentationOverrides,
    seedPks,
  ]);

  const picturePresentationModal = useCreateApiFormModal({
    url: ApiEndpoints.cost_card_picture_presentation,
    queryParams: picturePresentationParams,
    method: "GET",
    title: t`Presentation`,
    fields: picturePresentationFormFields,
    processFormData: processPicturePresentationData,
    // Both exports are offered from a dropdown in the modal header, keeping
    // the (tall) form itself free of a button row
    headerActions: true,
    actions: [
      {
        text: t`Cost Card Representation`,
        onClick: exportCostCardRepresentation,
      },
    ],
    submitText: t`Picture Presentation`,
    successMessage: null,
    timeout: 30 * 1000,
    gridColumns: PURCHASE_REQUEST_FORM_GRID_COLUMNS,
    size: "80rem",
    alwaysEnableSubmit: true,
    onOpen: () => setPicturePresentationOpen(true),
    onClose: () => setPicturePresentationOpen(false),
    onFormSuccess: (response: any) => setExportId(response.pk),
  });

  useEffect(() => {
    closePicturePresentation.current = picturePresentationModal.close;
  }, [picturePresentationModal.close]);

  // Seed the form *before* it mounts, so the fields come up already filled in
  // rather than being populated a render later
  const open = useCallback(
    ({ records, po = null }: PicturePresentationSeed) => {
      setSeedRecords(records);
      setPicturePresentationCards(
        records.map((record: any) => Number(record.pk)),
      );
      // The P.O. field drives the style picker's filter, so both start out
      // matching the seed
      setSeedPo(po);
      setPicturePresentationPo(po);
      // The pricing inputs come up holding the figures shared by the seed
      const pricing: Record<string, any> = pricingValues(records);
      setPresentationOverrides(
        Object.fromEntries(
          PRESENTATION_OVERRIDE_FIELDS.map((name) => [name, pricing[name]]),
        ),
      );
      picturePresentationModal.open();
    },
    [pricingValues, picturePresentationModal.open],
  );

  return { modal: picturePresentationModal.modal, open };
}
