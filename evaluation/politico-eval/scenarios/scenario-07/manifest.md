# Manifest: event-service-0331

**Rain ID**: event-service-0331
**Mode**: full
**Base Branch**: main
**Base Commit**: 8f2a5e1

## Task List

| Howler | Scope | Effort | Serial Risk |
|--------|-------|--------|-------------|
| howler-producer | Implement Kafka event producer: message serialization, topic routing, partition key selection, and producer health check | M | no |
| howler-consumer | Implement Kafka event consumer: message deserialization, consumer group management, offset committing, and error classification | L | no |
| howler-schema-registry | Integrate Confluent Schema Registry: Avro schema registration, schema evolution validation, and schema ID resolution | M | no |
| howler-dlq | Implement dead-letter queue: DLQ topic routing, failure envelope creation, DLQ consumer for manual review, and retry-from-DLQ flow | M | no |
| howler-monitoring | Add observability: Prometheus metrics for producer/consumer lag, topic health, DLQ depth, and OpenTelemetry tracing | M | no |
| howler-deployment | Write Kubernetes manifests, Helm chart values, and docker-compose for local development | S | no |

## File Ownership Matrix

| File | Howler | Action |
|------|--------|--------|
| `src/producer/producer.ts` | howler-producer | CREATES |
| `src/producer/serializer.ts` | howler-producer | CREATES |
| `src/producer/router.ts` | howler-producer | CREATES |
| `src/producer/health.ts` | howler-producer | CREATES |
| `src/consumer/consumer.ts` | howler-consumer | CREATES |
| `src/consumer/deserializer.ts` | howler-consumer | CREATES |
| `src/consumer/group-manager.ts` | howler-consumer | CREATES |
| `src/consumer/error-classifier.ts` | howler-consumer | CREATES |
| `src/schema-registry/client.ts` | howler-schema-registry | CREATES |
| `src/schema-registry/validator.ts` | howler-schema-registry | CREATES |
| `src/schema-registry/resolver.ts` | howler-schema-registry | CREATES |
| `src/dlq/dlq-producer.ts` | howler-dlq | CREATES |
| `src/dlq/failure-envelope.ts` | howler-dlq | CREATES |
| `src/dlq/dlq-consumer.ts` | howler-dlq | CREATES |
| `src/dlq/retry.ts` | howler-dlq | CREATES |
| `src/monitoring/metrics.ts` | howler-monitoring | CREATES |
| `src/monitoring/tracing.ts` | howler-monitoring | CREATES |
| `src/monitoring/consumer-lag.ts` | howler-monitoring | CREATES |
| `src/monitoring/dlq-depth.ts` | howler-monitoring | CREATES |
| `k8s/deployment.yaml` | howler-deployment | CREATES |
| `k8s/service.yaml` | howler-deployment | CREATES |
| `k8s/configmap.yaml` | howler-deployment | CREATES |
| `helm/values.yaml` | howler-deployment | CREATES |
| `helm/Chart.yaml` | howler-deployment | CREATES |

**CONFLICTS**: none (verified — no file appears in more than one Howler's ownership)

## Dependency Graph (DAG)

```yaml
- id: howler-schema-registry
  deps: []
  branch: spectrum/event-service-0331/howler-schema-registry
  base_branch: main
  base_commit: 8f2a5e1

- id: howler-producer
  deps: [howler-schema-registry#types]
  branch: spectrum/event-service-0331/howler-producer
  base_branch: main
  base_commit: 8f2a5e1

- id: howler-consumer
  deps: [howler-schema-registry#types]
  branch: spectrum/event-service-0331/howler-consumer
  base_branch: main
  base_commit: 8f2a5e1

- id: howler-dlq
  deps: [howler-consumer#types]
  branch: spectrum/event-service-0331/howler-dlq
  base_branch: main
  base_commit: 8f2a5e1

- id: howler-monitoring
  deps: []
  branch: spectrum/event-service-0331/howler-monitoring
  base_branch: main
  base_commit: 8f2a5e1

- id: howler-deployment
  deps: []
  branch: spectrum/event-service-0331/howler-deployment
  base_branch: main
  base_commit: 8f2a5e1
```

## Decomposition Rationale

I chose 6 Howlers because schema registry integration, producer, consumer, DLQ, monitoring, and deployment are independent concerns. howler-schema-registry runs first (shared foundation for serialization). howler-producer and howler-consumer are parallel after schema-registry#types (both need schema validation but are independent implementations). howler-dlq depends on howler-consumer#types because the DLQ failure envelope references the consumer's error classification output. howler-monitoring and howler-deployment are independent — monitoring instrument names are defined in the monitoring Howler independently of the other implementations. Alternative: merging producer+consumer — rejected because producer and consumer have opposite data flows and separate operational concerns.

## Politico Review

_Not yet conducted — pre-freeze review scheduled._
