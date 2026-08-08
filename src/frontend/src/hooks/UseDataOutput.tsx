import useMonitorDataOutput from '@lib/hooks/MonitorDataOutput';
import { useApi } from '@context/ApiContext';
import { useLocalState } from '@store/LocalState';

/**
 * Hook for monitoring a data output process running on the server
 */
export default function useDataOutput({
  title,
  id
}: {
  title: string;
  id?: number;
}) {
  const api = useApi();
  const { getHost } = useLocalState.getState();

  return useMonitorDataOutput({
    api: api,
    title: title,
    id: id,
    hostname: getHost()
  });
}
