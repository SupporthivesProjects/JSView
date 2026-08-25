import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import { useApi } from "@context/ApiContext";
import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { apiUrl } from "@lib/functions/Api";

export function useStoneShapeLookup() {
  const api = useApi();

  const stoneShapeQuery = useQuery({
    queryKey: ["stone-shape-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.color_stone_shape_list), {
          params: { limit: 1000 },
        })
        .then(
          (response) =>
            response.data?.results ?? response.data ?? [],
        ),
    staleTime: 5 * 60 * 1000,
  });

  const stoneShapeNameByPk = useMemo(() => {
    const map: Record<number, string> = {};

    (stoneShapeQuery.data ?? []).forEach((stoneShape: any) => {
      map[stoneShape.pk] = stoneShape.name;
    });

    return map;
  }, [stoneShapeQuery.data]);

  return {
    stoneShapeQuery,
    stoneShapeNameByPk,
  };
}


export function useStoneSizeLookup() {
  const api = useApi();

  const stoneSizeQuery = useQuery({
    queryKey: ["stone-size-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.color_stone_size_list), {
          params: { limit: 1000 },
        })
        .then(
          (response) =>
            response.data?.results ?? response.data ?? [],
        ),
    staleTime: 5 * 60 * 1000,
  });

  const stoneSizeNameByPk = useMemo(() => {
    const map: Record<number, string> = {};

    (stoneSizeQuery.data ?? []).forEach((stoneSize: any) => {
      map[stoneSize.pk] = stoneSize.mm_size;
    });

    return map;
  }, [stoneSizeQuery.data]);

  return {
    stoneSizeQuery,
    stoneSizeNameByPk,
  };
}

export function useStoneStoneLookup() {
  const api = useApi();

  const stoneStoneQuery = useQuery({
    queryKey: ["stone-stone-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.color_stone_type_list), {
          params: { limit: 1000 },
        })
        .then(
          (response) =>
            response.data?.results ?? response.data ?? [],
        ),
    staleTime: 5 * 60 * 1000,
  });

  const stoneStoneNameByPk = useMemo(() => {
    const map: Record<number, string> = {};

    (stoneStoneQuery.data ?? []).forEach((stoneStone: any) => {
      map[stoneStone.pk] = stoneStone.name;
    });

    return map;
  }, [stoneStoneQuery.data]);

  return {
    stoneStoneQuery,
    stoneStoneNameByPk,
  };
}

export function useStoneColorLookup() {
  const api = useApi();

  const stoneColorQuery = useQuery({
    queryKey: ["stone-color-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.color_stone_color_list), {
          params: { limit: 1000 },
        })
        .then(
          (response) =>
            response.data?.results ?? response.data ?? [],
        ),
    staleTime: 5 * 60 * 1000,
  });

  const stoneColorNameByPk = useMemo(() => {
    const map: Record<number, string> = {};

    (stoneColorQuery.data ?? []).forEach((stoneColor: any) => {
      map[stoneColor.pk] = stoneColor.name;
    });

    return map;
  }, [stoneColorQuery.data]);

  return {
    stoneColorQuery,
    stoneColorNameByPk,
  };
}
export function useStoneCutLookup() {
  const api = useApi();

  const stoneCutQuery = useQuery({
    queryKey: ["stone-cut-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.color_stone_cut_list), {
          params: { limit: 1000 },
        })
        .then(
          (response) =>
            response.data?.results ?? response.data ?? [],
        ),
    staleTime: 5 * 60 * 1000,
  });

  const stoneCutNameByPk = useMemo(() => {
    const map: Record<number, string> = {};

    (stoneCutQuery.data ?? []).forEach((stoneCut: any) => {
      map[stoneCut.pk] = stoneCut.name;
    });

    return map;
  }, [stoneCutQuery.data]);

  return {
    stoneCutQuery,
    stoneCutNameByPk,
  };
}

export function useStoneQualityLookup() {
  const api = useApi();

  const stoneQualityQuery = useQuery({
    queryKey: ["stone-quality-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.color_stone_quality_list), {
          params: { limit: 1000 },
        })
        .then(
          (response) =>
            response.data?.results ?? response.data ?? [],
        ),
    staleTime: 5 * 60 * 1000,
  });

  const stoneQualityNameByPk = useMemo(() => {
    const map: Record<number, string> = {};

    (stoneQualityQuery.data ?? []).forEach((stoneQuality: any) => {
      map[stoneQuality.pk] = stoneQuality.name;
    });

    return map;
  }, [stoneQualityQuery.data]);

  return {
    stoneQualityQuery,
    stoneQualityNameByPk,
  };
}