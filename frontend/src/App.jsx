import { useEffect, useMemo, useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5000';
const API_URL = `${API_BASE_URL}/api/anomalies`;
const FEATURE_PLAN_URL = `${API_BASE_URL}/api/feature-plan`;
const PAYMENT_CATEGORIES_URL = `${API_BASE_URL}/api/payment-categories`;
const REVIEW_URL = `${API_BASE_URL}/api/anomaly-review`;
const SCAN_URL = `${API_BASE_URL}/api/run-scan`;
const SCAN_STATUS_URL = `${API_BASE_URL}/api/scan-status`;
const LLM_PROVIDER_URL = `${API_BASE_URL}/api/llm-provider`;
const PROVIDER_LABELS = { vllm: 'Local vLLM', ollama: 'Local Ollama', groq: 'Groq Cloud' };
const POLL_INTERVAL_MS = 4000;
const MAX_FEEDBACK_LENGTH = 100;
const PAGE_SIZE_OPTIONS = [25, 50, 100];
const SEARCH_DEBOUNCE_MS = 350;

function normalizeAlerts(payload) {
  if (!Array.isArray(payload)) {
    return [];
  }

  return payload.map((alert) => ({
    transaction_id: String(alert.transaction_id ?? 'unknown'),
    table_name: alert.table_name ? String(alert.table_name) : 'unknown',
    source_record_id: alert.source_record_id ? String(alert.source_record_id) : 'unknown',
    anomaly_score: Number(alert.anomaly_score ?? 0),
    isolation_score: Number(alert.isolation_score ?? 0),
    autoencoder_score: alert.autoencoder_score == null ? null : Number(alert.autoencoder_score),
    detected_at: alert.detected_at ?? new Date().toISOString(),
    feature_snapshot: alert.feature_snapshot ?? {},
    explanation: alert.explanation ?? 'No explanation was provided for this anomaly.',
  }));
}

function formatDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return 'Unknown';
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

function formatCurrency(value) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) {
    return 'Not available';
  }

  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 2,
  }).format(amount);
}

function firstAvailable(...values) {
  return values.find((value) => value !== undefined && value !== null && value !== '') ?? 'Not available';
}

function forensicDetails(alert) {
  const snapshot = alert?.feature_snapshot ?? {};
  const engineered = snapshot.engineered_feature_values ?? {};
  const dakId = firstAvailable(
    snapshot.display_dak_id,
    snapshot.fk_dak,
    snapshot.dak_id,
    snapshot.source_db_table === 'dak' ? snapshot.transaction_id : null,
    alert.source_record_id,
  );
  const billAmount = firstAvailable(
    snapshot.display_bill_amount_claimed,
    snapshot.amount_claimed,
    engineered.amount_claimed,
    snapshot.source_db_table === 'bill' ? snapshot.amount_in_rupees : null,
  );
  const sectionName = firstAvailable(
    snapshot.display_section_name,
    snapshot.section_name,
    snapshot.bill_fk_section_section_section_name,
    snapshot.dak_fk_section_section_section_name,
    snapshot.display_section_id ? `Section ${snapshot.display_section_id}` : null,
    snapshot.fk_section ? `Section ${snapshot.fk_section}` : null,
  );

  return {
    dakId,
    billAmount: billAmount === 'Not available' ? billAmount : formatCurrency(billAmount),
    sectionName,
  };
}

function getSeverity(score) {
  if (score >= 12) {
    return { label: 'Critical', className: 'severityCritical' };
  }

  if (score >= 8) {
    return { label: 'High', className: 'severityHigh' };
  }

  return { label: 'Elevated', className: 'severityElevated' };
}

const SORTABLE_HEADERS = [
  { key: 'transaction_id', label: 'Transaction', sortable: true },
  { key: 'table_name', label: 'Table', sortable: true },
  { key: 'severity', label: 'Severity', sortable: false },
  { key: 'anomaly_score', label: 'Score', sortable: true },
  { key: 'isolation', label: 'IF', sortable: false },
  { key: 'other', label: 'Other', sortable: false },
  { key: 'detected_at', label: 'Detected', sortable: true },
];

function listToCsv(value) {
  return Array.isArray(value) ? value.join(', ') : '';
}

function csvToStrings(value) {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

function csvToPositiveIntegers(value) {
  const items = csvToStrings(value);
  const numbers = items.map((item) => Number(item));
  if (numbers.some((item) => !Number.isInteger(item) || item <= 0)) {
    throw new Error('Section IDs must be positive integers');
  }
  return numbers;
}

export default function App() {
  const [alerts, setAlerts] = useState([]);
  const [total, setTotal] = useState(0);
  const [tables, setTables] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [status, setStatus] = useState('loading');
  const [lastUpdated, setLastUpdated] = useState(null);
  const [scanStatus, setScanStatus] = useState({ running: false, last_result: null, last_error: null });
  const [scanMessage, setScanMessage] = useState('');
  const [featurePlan, setFeaturePlan] = useState([]);
  const [paymentCategories, setPaymentCategories] = useState([]);
  const [paymentDrafts, setPaymentDrafts] = useState({});
  const [paymentMessage, setPaymentMessage] = useState('');
  const [paymentSaving, setPaymentSaving] = useState('');
  const [openCards, setOpenCards] = useState(() => new Set());
  const [llmProvider, setLlmProvider] = useState({ provider: 'vllm', available: ['vllm', 'ollama', 'groq'], model: '' });
  const [providerSaving, setProviderSaving] = useState(false);
  const [reviewFeedback, setReviewFeedback] = useState('');
  const [reviewError, setReviewError] = useState('');
  const [reviewSaving, setReviewSaving] = useState(false);

  // Filtering, sorting, pagination (all server-driven).
  const [tableFilter, setTableFilter] = useState('');
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [sort, setSort] = useState('detected_at');
  const [direction, setDirection] = useState('desc');
  const [page, setPage] = useState(0);
  const [pageSize, setPageSize] = useState(25);

  const pageCount = Math.max(1, Math.ceil(total / pageSize));

  const buildAnomaliesUrl = () => {
    const url = new URL(API_URL);
    url.searchParams.set('limit', String(pageSize));
    url.searchParams.set('offset', String(page * pageSize));
    url.searchParams.set('sort', sort);
    url.searchParams.set('direction', direction);
    if (tableFilter) {
      url.searchParams.set('table', tableFilter);
    }
    if (debouncedSearch) {
      url.searchParams.set('q', debouncedSearch);
    }
    return url;
  };

  const fetchAlerts = async ({ signal, showLoading = false } = {}) => {
    if (showLoading) {
      setStatus('loading');
    }

    try {
      const response = await fetch(buildAnomaliesUrl(), { signal });
      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }

      const payload = await response.json();
      setAlerts(normalizeAlerts(payload.items));
      setTotal(Number(payload.total ?? 0));
      if (Array.isArray(payload.tables)) {
        setTables(payload.tables);
      }
      setStatus('live');
      setLastUpdated(new Date());
    } catch (error) {
      if (error.name === 'AbortError') {
        return;
      }

      setAlerts([]);
      setTotal(0);
      setStatus('error');
      setLastUpdated(new Date());
    }
  };

  const fetchScanStatus = async ({ signal } = {}) => {
    try {
      const response = await fetch(SCAN_STATUS_URL, { signal });
      if (!response.ok) {
        throw new Error(`Scan status returned ${response.status}`);
      }
      setScanStatus(await response.json());
    } catch (error) {
      if (error.name !== 'AbortError') {
        setScanStatus((current) => ({ ...current, last_error: 'Scan status unavailable' }));
      }
    }
  };

  const fetchFeaturePlan = async ({ signal } = {}) => {
    try {
      const response = await fetch(FEATURE_PLAN_URL, { signal });
      if (!response.ok) {
        throw new Error(`Feature plan returned ${response.status}`);
      }
      const payload = await response.json();
      setFeaturePlan(Array.isArray(payload) ? payload : []);
    } catch (error) {
      if (error.name !== 'AbortError') {
        setFeaturePlan([]);
      }
    }
  };

  const fetchPaymentCategories = async ({ signal } = {}) => {
    try {
      const response = await fetch(PAYMENT_CATEGORIES_URL, { signal });
      if (!response.ok) {
        throw new Error(`Payment categories returned ${response.status}`);
      }
      const payload = await response.json();
      const categories = Array.isArray(payload) ? payload : [];
      setPaymentCategories(categories);
      setPaymentDrafts(
        categories.reduce((drafts, category) => {
          drafts[category.category_name] = {
            source_tables: listToCsv(category.source_tables),
            dak_section_ids: listToCsv(category.dak_section_ids),
            enabled: Boolean(category.enabled),
          };
          return drafts;
        }, {})
      );
    } catch (error) {
      if (error.name !== 'AbortError') {
        setPaymentCategories([]);
        setPaymentMessage('Payment categories unavailable');
      }
    }
  };

  const fetchProvider = async ({ signal } = {}) => {
    try {
      const response = await fetch(LLM_PROVIDER_URL, { signal });
      if (!response.ok) {
        throw new Error(`Provider returned ${response.status}`);
      }
      setLlmProvider(await response.json());
    } catch (error) {
      if (error.name !== 'AbortError') {
        // Leave the last known provider in place.
      }
    }
  };

  const changeProvider = async (provider) => {
    if (provider === llmProvider.provider || providerSaving) {
      return;
    }
    setProviderSaving(true);
    try {
      const response = await fetch(LLM_PROVIDER_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider }),
      });
      if (!response.ok) {
        throw new Error(`Switch failed with ${response.status}`);
      }
      setLlmProvider(await response.json());
    } catch {
      fetchProvider();
    } finally {
      setProviderSaving(false);
    }
  };

  const updatePaymentDraft = (categoryName, field, value) => {
    setPaymentDrafts((current) => ({
      ...current,
      [categoryName]: {
        ...current[categoryName],
        [field]: value,
      },
    }));
  };

  const savePaymentCategory = async (categoryName) => {
    const draft = paymentDrafts[categoryName];
    if (!draft || paymentSaving) {
      return;
    }

    setPaymentSaving(categoryName);
    setPaymentMessage('');
    try {
      const body = {
        category_name: categoryName,
        source_tables: csvToStrings(draft.source_tables),
        dak_section_ids: csvToPositiveIntegers(draft.dak_section_ids),
        enabled: Boolean(draft.enabled),
      };
      const response = await fetch(PAYMENT_CATEGORIES_URL, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload.error || `Save failed with ${response.status}`);
      }
      setPaymentMessage(`${categoryName} saved`);
      fetchPaymentCategories();
      fetchFeaturePlan();
    } catch (error) {
      setPaymentMessage(error.message || 'Unable to save payment category');
    } finally {
      setPaymentSaving('');
    }
  };

  const runScan = async () => {
    setScanMessage('Starting scan...');
    try {
      const response = await fetch(SCAN_URL, { method: 'POST' });
      const payload = await response.json();
      setScanStatus(payload.status);
      setScanMessage(payload.started ? 'Scan started' : 'A scan is already running');
    } catch {
      setScanMessage('Unable to start scan');
    }
  };

  const submitReview = async (decision) => {
    if (!selectedAlert || reviewSaving) {
      return;
    }

    setReviewSaving(true);
    setReviewError('');

    try {
      const response = await fetch(REVIEW_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transaction_id: selectedAlert.transaction_id,
          decision,
          feedback: reviewFeedback.trim().slice(0, MAX_FEEDBACK_LENGTH),
        }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(payload.error || `Review failed with ${response.status}`);
      }

      setSelectedAlert(null);
      setReviewFeedback('');
      // Counts and pages shift after a review; refetch the current page.
      fetchAlerts();
    } catch (error) {
      setReviewError(error.message || 'Unable to save review');
    } finally {
      setReviewSaving(false);
    }
  };

  const toggleCard = (table) => {
    setOpenCards((current) => {
      const next = new Set(current);
      if (next.has(table)) {
        next.delete(table);
      } else {
        next.add(table);
      }
      return next;
    });
  };

  const handleSort = (key) => {
    if (sort === key) {
      setDirection((current) => (current === 'asc' ? 'desc' : 'asc'));
    } else {
      setSort(key);
      setDirection('desc');
    }
  };

  // Debounce the transaction search box.
  useEffect(() => {
    const id = window.setTimeout(() => setDebouncedSearch(search.trim()), SEARCH_DEBOUNCE_MS);
    return () => window.clearTimeout(id);
  }, [search]);

  // Any filter/sort/page-size change resets to the first page.
  useEffect(() => {
    setPage(0);
  }, [tableFilter, debouncedSearch, pageSize, sort, direction]);

  // Fetch on mount and whenever the query parameters change; keep polling.
  useEffect(() => {
    const controller = new AbortController();
    fetchAlerts({ signal: controller.signal, showLoading: true });
    fetchScanStatus({ signal: controller.signal });

    const intervalId = window.setInterval(() => {
      fetchAlerts();
      fetchScanStatus();
    }, POLL_INTERVAL_MS);

    return () => {
      controller.abort();
      window.clearInterval(intervalId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, pageSize, tableFilter, debouncedSearch, sort, direction]);

  useEffect(() => {
    const controller = new AbortController();
    fetchFeaturePlan({ signal: controller.signal });
    fetchPaymentCategories({ signal: controller.signal });
    fetchProvider({ signal: controller.signal });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    setReviewFeedback('');
    setReviewError('');
    setReviewSaving(false);
  }, [selectedAlert?.transaction_id]);

  const metrics = useMemo(() => {
    const critical = alerts.filter((alert) => alert.anomaly_score >= 12).length;
    const high = alerts.filter((alert) => alert.anomaly_score >= 8 && alert.anomaly_score < 12).length;
    const maxScore = alerts.reduce((max, alert) => Math.max(max, alert.anomaly_score), 0);

    return { critical, high, maxScore };
  }, [alerts]);

  const rangeStart = total === 0 ? 0 : page * pageSize + 1;
  const rangeEnd = Math.min(total, page * pageSize + alerts.length);
  const sortIndicator = (key) => (sort === key ? (direction === 'asc' ? ' ▲' : ' ▼') : '');

  return (
    <main className="appShell">
      <section className="workspace">
        <header className="topbar">
          <div>
            <p className="eyebrow">Tulip 2.0 Risk Operations</p>
            <h1>Anomaly Command Center</h1>
          </div>

          <div className="toolbar">
            <span className={`connectionBadge ${status}`}>
              {status === 'live' ? 'Live API' : status === 'loading' ? 'Connecting' : 'API unavailable'}
            </span>
            <span className={`connectionBadge ${scanStatus.running ? 'loading' : 'live'}`}>
              {scanStatus.running ? 'Scan running' : 'Scanner ready'}
            </span>
            <label className="providerToggle" title={llmProvider.model ? `Model: ${llmProvider.model}` : 'Select LLM'}>
              <span>LLM</span>
              <select
                value={llmProvider.provider}
                onChange={(event) => changeProvider(event.target.value)}
                disabled={providerSaving || scanStatus.running}
              >
                {(llmProvider.available || ['vllm', 'ollama', 'groq']).map((name) => (
                  <option key={name} value={name}>
                    {PROVIDER_LABELS[name] ?? name}
                  </option>
                ))}
              </select>
            </label>
            <button className="secondaryButton" type="button" onClick={runScan} disabled={scanStatus.running}>
              Run scan
            </button>
            <button className="secondaryButton" type="button" onClick={() => fetchAlerts({ showLoading: true })}>
              Refresh
            </button>
          </div>
        </header>

        <section className="metricGrid" aria-label="Anomaly summary">
          <article className="metricCard">
            <span>Open anomalies</span>
            <strong>{total}</strong>
          </article>
          <article className="metricCard">
            <span>Critical (page)</span>
            <strong>{metrics.critical}</strong>
          </article>
          <article className="metricCard">
            <span>High risk (page)</span>
            <strong>{metrics.high}</strong>
          </article>
          <article className="metricCard">
            <span>Peak score (page)</span>
            <strong>{metrics.maxScore.toFixed(2)}</strong>
          </article>
        </section>

        <section className="contentBand">
          <div className="sectionHeader">
            <div>
              <h2>Detected anomalies</h2>
              <p>
                {lastUpdated ? `Last updated ${formatDate(lastUpdated)}` : 'Waiting for the first API response'}
                {scanMessage ? ` · ${scanMessage}` : ''}
                {scanStatus.last_result
                  ? ` · Last scan stored ${scanStatus.last_result.anomalies_stored} anomaly record(s) from ${scanStatus.last_result.tables_scanned ?? 1} table(s)`
                  : ''}
                {scanStatus.last_error ? ` · ${scanStatus.last_error}` : ''}
              </p>
            </div>
          </div>

          <div className="filterBar" role="search">
            <label className="filterField">
              <span>Transaction</span>
              <input
                type="search"
                value={search}
                onChange={(event) => setSearch(event.target.value)}
                placeholder="Search transaction id (e.g. bill:324)"
              />
            </label>

            <label className="filterField">
              <span>Table</span>
              <select value={tableFilter} onChange={(event) => setTableFilter(event.target.value)}>
                <option value="">All tables</option>
                {tables.map((name) => (
                  <option key={name} value={name}>
                    {name}
                  </option>
                ))}
              </select>
            </label>

            <label className="filterField">
              <span>Page size</span>
              <select value={pageSize} onChange={(event) => setPageSize(Number(event.target.value))}>
                {PAGE_SIZE_OPTIONS.map((size) => (
                  <option key={size} value={size}>
                    {size}
                  </option>
                ))}
              </select>
            </label>

            {(tableFilter || search) && (
              <button
                className="secondaryButton"
                type="button"
                onClick={() => {
                  setTableFilter('');
                  setSearch('');
                }}
              >
                Clear filters
              </button>
            )}
          </div>

          <div className="tableFrame">
            <table>
              <thead>
                <tr>
                  {SORTABLE_HEADERS.map((header) =>
                    header.sortable ? (
                      <th
                        key={header.key}
                        className="sortableHeader"
                        onClick={() => handleSort(header.key)}
                        aria-sort={sort === header.key ? (direction === 'asc' ? 'ascending' : 'descending') : 'none'}
                      >
                        {header.label}
                        {sortIndicator(header.key)}
                      </th>
                    ) : (
                      <th key={header.key}>{header.label}</th>
                    ),
                  )}
                  <th aria-label="Actions" />
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert) => {
                  const severity = getSeverity(alert.anomaly_score);

                  return (
                    <tr key={alert.transaction_id}>
                      <td>
                        <span className="transactionId">{alert.transaction_id}</span>
                      </td>
                      <td>{alert.table_name}</td>
                      <td>
                        <span className={`severityPill ${severity.className}`}>{severity.label}</span>
                      </td>
                      <td>{alert.anomaly_score.toFixed(2)}</td>
                      <td>{alert.isolation_score.toFixed(2)}</td>
                      <td>{alert.autoencoder_score == null ? 'n/a' : alert.autoencoder_score.toFixed(2)}</td>
                      <td>{formatDate(alert.detected_at)}</td>
                      <td className="actionCell">
                        <button className="primaryButton" type="button" onClick={() => setSelectedAlert(alert)}>
                          Inspect
                        </button>
                      </td>
                    </tr>
                  );
                })}

                {alerts.length === 0 && (
                  <tr>
                    <td className="emptyState" colSpan={SORTABLE_HEADERS.length + 1}>
                      {status === 'loading' ? 'Loading anomalies...' : 'No anomalies match the current filter.'}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          <div className="pager">
            <span className="pagerInfo">
              {total === 0 ? 'No results' : `Showing ${rangeStart}-${rangeEnd} of ${total}`}
            </span>
            <div className="pagerControls">
              <button
                className="secondaryButton"
                type="button"
                onClick={() => setPage(0)}
                disabled={page === 0}
              >
                « First
              </button>
              <button
                className="secondaryButton"
                type="button"
                onClick={() => setPage((current) => Math.max(0, current - 1))}
                disabled={page === 0}
              >
                ‹ Prev
              </button>
              <span className="pagerInfo">
                Page {page + 1} of {pageCount}
              </span>
              <button
                className="secondaryButton"
                type="button"
                onClick={() => setPage((current) => Math.min(pageCount - 1, current + 1))}
                disabled={page >= pageCount - 1}
              >
                Next ›
              </button>
              <button
                className="secondaryButton"
                type="button"
                onClick={() => setPage(pageCount - 1)}
                disabled={page >= pageCount - 1}
              >
                Last »
              </button>
            </div>
          </div>
        </section>

        <section className="paymentConfigBand" aria-label="Payment category configuration">
          <div className="sectionHeader">
            <div>
              <h2>Payment categories</h2>
              <p>{paymentMessage || `${paymentCategories.length} configured payment type(s)`}</p>
            </div>
          </div>

          <div className="paymentConfigGrid">
            {paymentCategories.map((category) => {
              const draft = paymentDrafts[category.category_name] || {
                source_tables: listToCsv(category.source_tables),
                dak_section_ids: listToCsv(category.dak_section_ids),
                enabled: Boolean(category.enabled),
              };
              const isSaving = paymentSaving === category.category_name;

              return (
                <article className="paymentConfigCard" key={category.category_name}>
                  <div className="paymentConfigHeader">
                    <strong>{category.category_name}</strong>
                    <label className="switchField">
                      <input
                        type="checkbox"
                        checked={draft.enabled}
                        onChange={(event) => updatePaymentDraft(category.category_name, 'enabled', event.target.checked)}
                      />
                      <span>Enabled</span>
                    </label>
                  </div>

                  <div className="paymentConfigFields">
                    <label className="filterField">
                      <span>Source tables</span>
                      <input
                        value={draft.source_tables}
                        onChange={(event) => updatePaymentDraft(category.category_name, 'source_tables', event.target.value)}
                      />
                    </label>
                    <label className="filterField">
                      <span>Dak sections</span>
                      <input
                        value={draft.dak_section_ids}
                        onChange={(event) => updatePaymentDraft(category.category_name, 'dak_section_ids', event.target.value)}
                      />
                    </label>
                  </div>

                  <button
                    className="secondaryButton"
                    type="button"
                    onClick={() => savePaymentCategory(category.category_name)}
                    disabled={Boolean(paymentSaving)}
                  >
                    {isSaving ? 'Saving' : 'Save'}
                  </button>
                </article>
              );
            })}

            {paymentCategories.length === 0 && (
              <div className="featurePlanEmpty">
                Payment categories are not available.
              </div>
            )}
          </div>
        </section>

        <section className="featurePlanBand" aria-label="LLM feature plan">
          <div className="sectionHeader">
            <div>
              <h2>LLM feature plan</h2>
              <p>{featurePlan.length ? `${featurePlan.length} schema-validated table plan(s)` : 'No LLM feature plan loaded'}</p>
            </div>
          </div>

          <div className="featurePlanGrid">
            {featurePlan.map((source) => {
              const sourceName = source.scan_name || source.table;
              const isOpen = openCards.has(sourceName);
              const featureCount = (source.feature_plan || []).length;

              return (
                <article className={`featurePlanCard ${isOpen ? 'isOpen' : ''}`} key={sourceName}>
                  <button
                    type="button"
                    className="featurePlanCardHeader"
                    aria-expanded={isOpen}
                    onClick={() => toggleCard(sourceName)}
                  >
                    <span className="featurePlanTitle">
                      <span className="featurePlanTableName">{sourceName}</span>
                      <span className="featurePlanCount">{featureCount} feature{featureCount === 1 ? '' : 's'}</span>
                      {source.table && source.table !== sourceName ? (
                        <span className="featurePlanCount">{source.table}</span>
                      ) : null}
                    </span>
                    <span className="featurePlanAmount">{source.amount_column}</span>
                    <span className="featurePlanChevron" aria-hidden="true">▸</span>
                  </button>

                  <div className="featurePlanCardBody">
                    <div className="featurePlanCardBodyInner">
                      <ul>
                        {(source.feature_plan || []).map((feature) => (
                          <li key={`${sourceName}-${feature.name}`}>
                            <strong>{feature.name}</strong>
                            <span>
                              {feature.op}
                              {feature.source ? ` · ${feature.source}` : ''}
                              {feature.group_by ? ` · ${feature.group_by}` : ''}
                            </span>
                            <span>{feature.reason || 'Selected by the LLM'}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </article>
              );
            })}

            {featurePlan.length === 0 && (
              <div className="featurePlanEmpty">
                Run the architect step to generate table-specific feature plans.
              </div>
            )}
          </div>
        </section>
      </section>

      {selectedAlert && (
        <div className="modalOverlay" role="presentation" onMouseDown={() => setSelectedAlert(null)}>
          <section className="modalPanel" role="dialog" aria-modal="true" onMouseDown={(event) => event.stopPropagation()}>
            <div className="modalHeader">
              <div>
                <p className="eyebrow">Case file</p>
                <h2>{selectedAlert.transaction_id}</h2>
              </div>
              <button className="iconButton" type="button" aria-label="Close details" onClick={() => setSelectedAlert(null)}>
                x
              </button>
            </div>

            <dl className="detailGrid">
              <div>
                <dt>Severity</dt>
                <dd>{getSeverity(selectedAlert.anomaly_score).label}</dd>
              </div>
              <div>
                <dt>Score</dt>
                <dd>{selectedAlert.anomaly_score.toFixed(2)}</dd>
              </div>
              <div>
                <dt>Table</dt>
                <dd>{selectedAlert.table_name}</dd>
              </div>
              <div>
                <dt>Isolation</dt>
                <dd>{selectedAlert.isolation_score.toFixed(2)}</dd>
              </div>
              <div>
                <dt>Other score</dt>
                <dd>{selectedAlert.autoencoder_score == null ? 'n/a' : selectedAlert.autoencoder_score.toFixed(2)}</dd>
              </div>
              <div>
                <dt>Detected</dt>
                <dd>{formatDate(selectedAlert.detected_at)}</dd>
              </div>
            </dl>

            <div className="forensicDetails">
              {Object.entries(forensicDetails(selectedAlert)).map(([key, value]) => (
                <div className="forensicDetailLine" key={key}>
                  <span>
                    {key === 'dakId' ? 'DAK ID' : key === 'billAmount' ? 'Bill amount claimed' : 'Section name'}
                  </span>
                  <strong>{value}</strong>
                </div>
              ))}
            </div>

            <div className="explanationBox">
              <h3>Reasoning</h3>
              <p>{selectedAlert.explanation}</p>
            </div>

            <div className="explanationBox">
              <h3>Feature snapshot</h3>
              <pre>{JSON.stringify(selectedAlert.feature_snapshot, null, 2)}</pre>
            </div>

            <div className="reviewBox">
              <label htmlFor="reviewFeedback">Feedback</label>
              <textarea
                id="reviewFeedback"
                maxLength={MAX_FEEDBACK_LENGTH}
                onChange={(event) => setReviewFeedback(event.target.value)}
                placeholder="Add a short review note"
                rows="3"
                value={reviewFeedback}
              />
              <div className="reviewMeta">
                <span>{reviewFeedback.length}/{MAX_FEEDBACK_LENGTH}</span>
                {reviewError ? <span className="reviewError">{reviewError}</span> : null}
              </div>
              <div className="reviewActions" aria-label="Review decision">
                <button className="acceptButton" type="button" onClick={() => submitReview('accept')} disabled={reviewSaving}>
                  Accept
                </button>
                <button className="rejectButton" type="button" onClick={() => submitReview('reject')} disabled={reviewSaving}>
                  Reject
                </button>
                <button className="maybeButton" type="button" onClick={() => submitReview('maybe')} disabled={reviewSaving}>
                  Maybe
                </button>
              </div>
            </div>
          </section>
        </div>
      )}
    </main>
  );
}
