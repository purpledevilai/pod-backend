import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import {
  DynamoDBDocumentClient,
  BatchWriteCommand,
} from "@aws-sdk/lib-dynamodb";

const RECYCLEMATE_API = "https://api.recyclemate.com.au/v2";
const API_CONCURRENCY = 1000;
const DDB_WRITE_CONCURRENCY = 25;
const MAX_RETRIES = 3;
const DDB_BATCH_SIZE = 25;

const ddbDoc = DynamoDBDocumentClient.from(new DynamoDBClient({}));

// ---------------------------------------------------------------------------
// Types matching the RecycleMate API responses
// ---------------------------------------------------------------------------

interface CouncilSummary {
  id: string;
  name: string;
  mapId: string;
}

interface ApiBin {
  id: string;
  acceptsCardboard: boolean;
  acceptsContainers: boolean;
  acceptsFood: boolean;
  acceptsGarbage: boolean;
  acceptsGarden: boolean;
  acceptsGlass: boolean;
  acceptsSoftPlastics: boolean;
  appearance: string;
  type: string;
  extras: string[];
  instructions?: unknown;
  message?: string;
}

interface ApiBinSystem {
  id: string;
  isDefault?: boolean;
  bins: ApiBin[];
}

interface CouncilDetail {
  id: string;
  name: string;
  slug: string;
  mapId: string;
  binSystems: ApiBinSystem[];
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/** Run `fn` over every item with at most `concurrency` in-flight at once. */
async function asyncPool<T, R>(
  concurrency: number,
  items: T[],
  fn: (item: T) => Promise<R>,
): Promise<R[]> {
  const results = new Array<R>(items.length);
  let idx = 0;

  async function worker() {
    while (idx < items.length) {
      const i = idx++;
      results[i] = await fn(items[i]);
    }
  }

  await Promise.all(
    Array.from({ length: Math.min(concurrency, items.length) }, () => worker()),
  );
  return results;
}

/** fetch() with exponential-backoff retries for 429 / 5xx. */
async function fetchRetry(url: string): Promise<Response> {
  for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
    try {
      const res = await fetch(url);
      if (res.ok || (res.status < 500 && res.status !== 429)) return res;
      if (attempt < MAX_RETRIES) {
        await sleep(2 ** attempt * 1000);
        continue;
      }
      return res;
    } catch (err) {
      if (attempt === MAX_RETRIES) throw err;
      await sleep(2 ** attempt * 1000);
    }
  }
  throw new Error(`Failed to fetch ${url}`);
}

/** Write a single batch of ≤25 items, retrying any unprocessed items. */
async function writeBatch(
  tableName: string,
  requests: { PutRequest: { Item: Record<string, unknown> } }[],
): Promise<void> {
  let pending = requests;
  for (let attempt = 0; pending.length > 0 && attempt <= MAX_RETRIES; attempt++) {
    const result = await ddbDoc.send(
      new BatchWriteCommand({ RequestItems: { [tableName]: pending } }),
    );
    const unprocessed = result.UnprocessedItems?.[tableName];
    if (unprocessed && unprocessed.length > 0) {
      pending = unprocessed as typeof pending;
      await sleep(2 ** attempt * 200);
    } else {
      return;
    }
  }
}

/** Batch-write items to a DynamoDB table with concurrent batch requests. */
async function batchWrite(
  tableName: string,
  items: Record<string, unknown>[],
): Promise<void> {
  const batches: { PutRequest: { Item: Record<string, unknown> } }[][] = [];
  for (let i = 0; i < items.length; i += DDB_BATCH_SIZE) {
    batches.push(
      items.slice(i, i + DDB_BATCH_SIZE).map((item) => ({
        PutRequest: { Item: item },
      })),
    );
  }
  await asyncPool(DDB_WRITE_CONCURRENCY, batches, (batch) =>
    writeBatch(tableName, batch),
  );
}

// ---------------------------------------------------------------------------
// RecycleMate API calls
// ---------------------------------------------------------------------------

function generatePostcodes(): string[] {
  const postcodes: string[] = [];
  for (let i = 200; i <= 9999; i++) {
    postcodes.push(String(i).padStart(4, "0"));
  }
  return postcodes;
}

let postcodesDone = 0;
let postcodesTotal = 0;

async function fetchCouncilsForPostcode(
  postcode: string,
): Promise<{ postcode: string; councils: CouncilSummary[] }> {
  try {
    const res = await fetchRetry(
      `${RECYCLEMATE_API}/location/councils?postcode=${postcode}&softPlastics=1`,
    );
    if (!res.ok) return { postcode, councils: [] };
    const data = (await res.json()) as CouncilSummary[];
    return { postcode, councils: Array.isArray(data) ? data : [] };
  } catch {
    return { postcode, councils: [] };
  } finally {
    const done = ++postcodesDone;
    if (done % 500 === 0 || done === postcodesTotal) {
      console.log(`Postcodes: ${done}/${postcodesTotal} (${((done / postcodesTotal) * 100).toFixed(1)}%)`);
    }
  }
}

let councilsDone = 0;
let councilsTotal = 0;

async function fetchCouncilDetail(
  councilId: string,
): Promise<CouncilDetail | null> {
  try {
    const res = await fetchRetry(`${RECYCLEMATE_API}/councils/${councilId}`);
    if (!res.ok) return null;
    return (await res.json()) as CouncilDetail;
  } catch {
    return null;
  } finally {
    const done = ++councilsDone;
    if (done % 50 === 0 || done === councilsTotal) {
      console.log(`Councils: ${done}/${councilsTotal} (${((done / councilsTotal) * 100).toFixed(1)}%)`);
    }
  }
}

// ---------------------------------------------------------------------------
// Handler
// ---------------------------------------------------------------------------

export const handler = async (): Promise<unknown> => {
  console.log("Starting RecycleMate data refresh");

  // Phase 1 — Fetch councils for every 4-digit postcode
  const postcodes = generatePostcodes();
  postcodesTotal = postcodes.length;
  postcodesDone = 0;
  console.log(`Querying ${postcodes.length} postcodes…`);

  const postcodeResults = await asyncPool(
    API_CONCURRENCY,
    postcodes,
    fetchCouncilsForPostcode,
  );

  // Build postcode→council map and collect unique councils
  const postcodeToCouncilItems: Record<string, unknown>[] = [];
  const uniqueCouncils = new Map<string, CouncilSummary>();

  for (const { postcode, councils } of postcodeResults) {
    if (councils.length === 0) continue;
    postcodeToCouncilItems.push({
      postcode,
      council_ids: councils.map((c) => c.id),
    });
    for (const c of councils) {
      uniqueCouncils.set(c.id, c);
    }
  }

  console.log(
    `${postcodeToCouncilItems.length} postcodes with councils, ${uniqueCouncils.size} unique councils`,
  );

  // Phase 2 — Fetch full detail for each unique council
  const councilIds = Array.from(uniqueCouncils.keys());
  councilsTotal = councilIds.length;
  councilsDone = 0;
  console.log(`Fetching details for ${councilIds.length} councils…`);

  const councilDetails = await asyncPool(
    API_CONCURRENCY,
    councilIds,
    fetchCouncilDetail,
  );

  // Phase 3 — Transform into per-table items
  const councilItems: Record<string, unknown>[] = [];
  const councilToBinSystemItems: Record<string, unknown>[] = [];
  const binSystemsMap = new Map<string, Record<string, unknown>>();

  for (const detail of councilDetails) {
    if (!detail) continue;

    councilItems.push({
      id: detail.id,
      name: detail.name,
      mapId: detail.mapId,
    });

    councilToBinSystemItems.push({
      council_id: detail.id,
      council_name: detail.name,
      bin_systems: detail.binSystems.map((bs) => ({
        id: bs.id,
        is_default: bs.isDefault ?? false,
        bins: bs.bins.map((b) => b.id),
      })),
    });

    for (const bs of detail.binSystems) {
      if (binSystemsMap.has(bs.id)) continue;
      binSystemsMap.set(bs.id, {
        id: bs.id,
        bins: bs.bins.map((b) => ({
          id: b.id,
          acceptsCardboard: b.acceptsCardboard,
          acceptsContainers: b.acceptsContainers,
          acceptsFood: b.acceptsFood,
          acceptsGarbage: b.acceptsGarbage,
          acceptsGarden: b.acceptsGarden,
          acceptsGlass: b.acceptsGlass,
          acceptsSoftPlastics: b.acceptsSoftPlastics,
          appearance: b.appearance,
          type: b.type,
          extras: b.extras ?? [],
        })),
      });
    }
  }

  const binSystemItems = Array.from(binSystemsMap.values());

  console.log(
    `Writing: ${postcodeToCouncilItems.length} postcodes, ` +
      `${councilItems.length} councils, ` +
      `${councilToBinSystemItems.length} council-to-bin-systems, ` +
      `${binSystemItems.length} bin systems`,
  );

  // Phase 4 — Batch write to all four tables in parallel
  await Promise.all([
    batchWrite("postcode_to_council", postcodeToCouncilItems),
    batchWrite("councils", councilItems),
    batchWrite("council_to_bin_system", councilToBinSystemItems),
    batchWrite("bin_systems", binSystemItems),
  ]);

  const summary = {
    postcodes: postcodeToCouncilItems.length,
    councils: councilItems.length,
    councilToBinSystems: councilToBinSystemItems.length,
    binSystems: binSystemItems.length,
  };

  console.log("Refresh complete", JSON.stringify(summary));
  return { statusCode: 200, body: JSON.stringify(summary) };
};
