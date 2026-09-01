import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import type { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { apiUrl } from "@lib/functions/Api";
import { useApi } from "@context/ApiContext";

/**
 * Fetch every record for a lookup endpoint and build a pk -> name map.
 *
 * Handy for rendering foreign-key columns in a table (e.g. "stone",
 * "shape", "setting") without needing a server-side join, mirroring the
 * pattern used for the customer/vendor columns in CostCardTable.
 */
export default function useNameLookup(
  endpoint: ApiEndpoints,
  queryKey: string,
) {
  const api = useApi();

  const query = useQuery({
    queryKey: [queryKey],
    queryFn: () =>
      api
        .get(apiUrl(endpoint), { params: { limit: 1000 } })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
    refetchOnMount: "always",
  });

  const nameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (query.data ?? []).forEach((record: any) => {
      map[record.pk] = record.name;
    });
    return map;
  }, [query.data]);

  return { nameByPk, isLoading: query.isLoading };
}
