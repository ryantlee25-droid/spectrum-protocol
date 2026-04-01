# Contract: event-service-0331

**Frozen at**: 2026-03-31T13:15:00Z
**Status**: FROZEN — do not modify. File AMENDMENT.md if changes are needed.

---

## Shared Types

All Howlers importing shared types MUST use the paths defined here. Do not re-declare these types.

### SchemaRef (source: howler-schema-registry)
```typescript
// src/schema-registry/resolver.ts
export interface SchemaRef {
  subject: string;       // Confluent Schema Registry subject name
  version: number;       // Schema version (positive integer)
  schemaId: number;      // Confluent schema ID (used in Avro wire format header)
}
```

### EventEnvelope (source: howler-producer)
```typescript
// src/producer/serializer.ts (re-exported)
export interface EventEnvelope {
  eventId: string;             // UUID
  eventType: string;           // e.g., "user.created", "order.fulfilled"
  schemaRef: SchemaRef;
  payload: unknown;            // Avro-serialized; deserialized shape depends on schemaRef
  producedAt: string;          // ISO 8601 timestamp
  traceId?: string;            // OpenTelemetry trace ID
}
```

### ConsumerError (source: howler-consumer)
```typescript
// src/consumer/error-classifier.ts
export type ConsumerErrorClass =
  | "transient"     // Network blip, broker timeout — retry immediately
  | "retriable"     // Deserialization failure with known cause — retry with backoff
  | "poison"        // Malformed message that will never succeed — route to DLQ
  | "fatal";        // Infrastructure failure — halt consumer group

export interface ConsumerError {
  eventId: string;
  errorClass: ConsumerErrorClass;
  errorMessage: string;
  originalPayload: Buffer;     // Raw Kafka message bytes for DLQ envelope
  attemptCount: number;
  failedAt: Date;
}
```

### DlqEnvelope (source: howler-dlq)
```typescript
// src/dlq/failure-envelope.ts
export interface DlqEnvelope {
  originalEventId: string;
  originalTopic: string;
  originalPartition: number;
  originalOffset: number;
  error: ConsumerError;
  dlqRoutedAt: Date;
  retryEligible: boolean;      // false for "poison" errors
}
```

---

## Naming Conventions

- **Kafka topics**: defined as constants in `src/producer/router.ts` — format: `{service}.{entity}.{event}` (e.g., `payments.invoice.created`)
- **Consumer group IDs**: `{service}-{consumer-name}-cg` (e.g., `billing-invoice-consumer-cg`)
- **DLQ topics**: `{original-topic}.dlq` (e.g., `payments.invoice.created.dlq`)
- **Metric names**: `{service}_{component}_{measurement}_{unit}` (e.g., `billing_consumer_lag_messages`)
- **Schema subjects**: `{topic}-value` (Confluent convention)
- **Avro schemas**: stored in `src/schemas/{entity}.avsc` (owned by howler-schema-registry)

---

## Integration Points

| From | To | Interface | Where |
|------|----|-----------|-------|
| howler-schema-registry | howler-producer | `SchemaRef` type + schema resolution | producer's serializer calls schema registry to get schemaId |
| howler-schema-registry | howler-consumer | `SchemaRef` type + schema resolution | consumer's deserializer resolves schemaId to Avro schema |
| howler-producer | howler-consumer | `EventEnvelope` format | consumer deserializes messages produced in EventEnvelope format |
| howler-consumer | howler-dlq | `ConsumerError` type | DLQ routes ConsumerError.errorClass == "poison" messages |
| howler-dlq | howler-monitoring | `DlqEnvelope` type (for DLQ depth metric) | monitoring reads DLQ topic lag as proxy for DLQ depth |
| howler-producer | howler-monitoring | Producer metrics | monitoring instruments producer with Prometheus counters |
| howler-consumer | howler-monitoring | Consumer lag metric | monitoring reads consumer group offset lag |

---

## Design-by-Contract: howler-schema-registry

### Preconditions
- Confluent Schema Registry available at `SCHEMA_REGISTRY_URL`
- `@confluentinc/schemaregistry` or `avro-js` in `package.json`

### Postconditions
- `src/schema-registry/client.ts` exports singleton `schemaRegistryClient`
- `src/schema-registry/resolver.ts` exports `resolveSchema(subject: string, version?: number): Promise<SchemaRef>`
- `src/schema-registry/validator.ts` exports `validateEvolution(subject: string, newSchema: object): Promise<boolean>`
- Avro schema files exist at `src/schemas/*.avsc` for all event types in scope

### Invariants
- Schema registry client is a singleton (never instantiated twice)
- `resolveSchema` caches results in memory for the process lifetime (avoids registry round-trips per message)

---

## Design-by-Contract: howler-producer

### Preconditions
- `howler-schema-registry#types` checkpoint is STABLE (`SchemaRef` type finalized)
- Kafka broker available at `KAFKA_BROKERS`
- `kafkajs` in `package.json`

### Postconditions
- `src/producer/producer.ts` exports `KafkaProducer` class with `produce(envelope: EventEnvelope): Promise<void>` method
- `src/producer/serializer.ts` exports `serialize(event: EventEnvelope): Buffer` and re-exports `EventEnvelope`
- `src/producer/router.ts` exports topic constants for all event types in scope
- `src/producer/health.ts` exports `checkProducerHealth(): Promise<{ connected: boolean; latencyMs: number }>`

### Invariants
- All produced messages use Avro encoding with Confluent wire format header (magic byte + schema ID)
- Producer uses `acks: "all"` for durability
- `EventEnvelope.payload` is the Avro-serialized form of the domain event — never a plain JS object

---

## Design-by-Contract: howler-consumer

### Preconditions
- `howler-schema-registry#types` checkpoint is STABLE (`SchemaRef` type finalized)
- Kafka broker available at `KAFKA_BROKERS`

### Postconditions
- `src/consumer/consumer.ts` exports `KafkaConsumer` class with `start()`, `stop()`, `subscribe(topics: string[])` methods
- `src/consumer/deserializer.ts` exports `deserialize(buffer: Buffer): EventEnvelope` — inverse of producer's serialize
- `src/consumer/group-manager.ts` exports `ConsumerGroupManager` for offset management
- `src/consumer/error-classifier.ts` exports `classifyError(err: Error, attemptCount: number): ConsumerErrorClass` and `ConsumerError` type

### Invariants
- Consumer commits offsets only after successful processing or DLQ routing (at-least-once semantics)
- `classifyError` is a pure function — no side effects, deterministic for same inputs
- Errors classified as "fatal" halt the consumer group and emit an alert metric

---

## Design-by-Contract: howler-dlq

### Preconditions
- `howler-consumer#types` checkpoint is STABLE (`ConsumerError` and `ConsumerErrorClass` finalized)

### Postconditions
- `src/dlq/dlq-producer.ts` exports `routeToDlq(error: ConsumerError, originalMessage: KafkaMessage): Promise<void>`
- `src/dlq/failure-envelope.ts` exports `createDlqEnvelope(error: ConsumerError, message: KafkaMessage): DlqEnvelope` and `DlqEnvelope` type
- `src/dlq/dlq-consumer.ts` exports `DlqConsumer` that reads from `*.dlq` topics and exposes messages for manual review
- `src/dlq/retry.ts` exports `retryFromDlq(envelope: DlqEnvelope): Promise<void>` — re-produces to original topic

### Invariants
- Only `ConsumerError` with `errorClass == "poison"` or `errorClass == "retriable"` are routed to DLQ
- `retryFromDlq` is blocked for envelopes where `retryEligible == false`
- DLQ envelopes are serialized as JSON (not Avro) for human readability

---

## Design-by-Contract: howler-monitoring

### Preconditions
- None (instruments other components via Prometheus pull model — no type dependencies)
- `prom-client` and `@opentelemetry/sdk-node` in `package.json`

### Postconditions
- `src/monitoring/metrics.ts` exports Prometheus metric definitions (counters, gauges, histograms)
- `src/monitoring/tracing.ts` exports OpenTelemetry tracer configured for the service
- `src/monitoring/consumer-lag.ts` exports `measureConsumerLag(groupId: string): Promise<number>`
- `src/monitoring/dlq-depth.ts` exports `measureDlqDepth(topic: string): Promise<number>`
- Metrics exposed at `/metrics` endpoint (Prometheus scrape format)

### Invariants
- All metric names follow the `{service}_{component}_{measurement}_{unit}` convention
- Tracing is configured with W3C TraceContext propagation

---

## Conventions Only: howler-deployment

_(Pure-create Howler — simplified contract)_

- Kubernetes manifests in `k8s/`: Deployment (2 replicas), Service (ClusterIP), ConfigMap for non-secret config
- Helm chart in `helm/`: `Chart.yaml` with apiVersion v2, `values.yaml` with kafka/schemaRegistry/monitoring config
- docker-compose for local development: kafka + zookeeper + schema-registry + the service itself
- Resource limits: 256Mi memory, 250m CPU requests; 512Mi memory, 500m CPU limits
- Liveness probe: `GET /health`, readiness probe: `GET /ready`
- No secrets in manifests — all secrets via `secretKeyRef` pointing to a pre-existing Secret
