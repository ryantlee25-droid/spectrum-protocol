# Manifest: billing-system-0331

**Rain ID**: billing-system-0331
**Mode**: full
**Base Branch**: main
**Base Commit**: 5e4c8b2

## Task List

| Howler | Scope | Effort | Serial Risk |
|--------|-------|--------|-------------|
| howler-subscriptions | Implement subscription plan management: plan CRUD, customer plan assignment, proration logic, plan change workflows | L | no |
| howler-invoices | Build invoice generation: invoice creation from subscription events, line item calculation, PDF generation, invoice state machine | L | no |
| howler-payments | Integrate Stripe payment processing: PaymentIntent creation, charge capture, payment method management, retry logic | L | no |
| howler-webhooks | Handle Stripe webhook events: event signature validation, idempotent event processing, webhook retry state | M | no |
| howler-notifications | Send billing notifications: payment success/failure emails, invoice ready emails, dunning emails | M | no |
| howler-integration | Wire all billing modules into the Express router, apply middleware, and write integration tests for the full billing lifecycle | L | yes |

## File Ownership Matrix

| File | Howler | Action |
|------|--------|--------|
| `src/billing/subscriptions/plan.service.ts` | howler-subscriptions | CREATES |
| `src/billing/subscriptions/proration.ts` | howler-subscriptions | CREATES |
| `src/billing/subscriptions/plan.routes.ts` | howler-subscriptions | CREATES |
| `src/billing/subscriptions/plan.schema.ts` | howler-subscriptions | CREATES |
| `src/billing/invoices/invoice.service.ts` | howler-invoices | CREATES |
| `src/billing/invoices/line-items.ts` | howler-invoices | CREATES |
| `src/billing/invoices/pdf.ts` | howler-invoices | CREATES |
| `src/billing/invoices/invoice.routes.ts` | howler-invoices | CREATES |
| `src/billing/invoices/invoice.schema.ts` | howler-invoices | CREATES |
| `src/billing/payments/payment.service.ts` | howler-payments | CREATES |
| `src/billing/payments/stripe.client.ts` | howler-payments | CREATES |
| `src/billing/payments/retry.ts` | howler-payments | CREATES |
| `src/billing/payments/payment.routes.ts` | howler-payments | CREATES |
| `src/billing/webhooks/webhook.handler.ts` | howler-webhooks | CREATES |
| `src/billing/webhooks/idempotency.ts` | howler-webhooks | CREATES |
| `src/billing/webhooks/webhook.routes.ts` | howler-webhooks | CREATES |
| `src/billing/notifications/email.service.ts` | howler-notifications | CREATES |
| `src/billing/notifications/templates.ts` | howler-notifications | CREATES |
| `src/billing/notifications/dunning.ts` | howler-notifications | CREATES |
| `src/billing/router.ts` | howler-integration | CREATES |
| `src/billing/middleware.ts` | howler-integration | CREATES |
| `tests/billing.integration.test.ts` | howler-integration | CREATES |
| `tests/billing.fixtures.ts` | howler-integration | CREATES |

**CONFLICTS**: none (verified — no file appears in more than one Howler's ownership)

## Dependency Graph (DAG)

```yaml
- id: howler-subscriptions
  deps: []
  branch: spectrum/billing-system-0331/howler-subscriptions
  base_branch: main
  base_commit: 5e4c8b2

- id: howler-invoices
  deps: [howler-subscriptions#types]
  branch: spectrum/billing-system-0331/howler-invoices
  base_branch: main
  base_commit: 5e4c8b2

- id: howler-payments
  deps: []
  branch: spectrum/billing-system-0331/howler-payments
  base_branch: main
  base_commit: 5e4c8b2

- id: howler-webhooks
  deps: [howler-payments#types]
  branch: spectrum/billing-system-0331/howler-webhooks
  base_branch: main
  base_commit: 5e4c8b2

- id: howler-notifications
  deps: []
  branch: spectrum/billing-system-0331/howler-notifications
  base_branch: main
  base_commit: 5e4c8b2

- id: howler-integration
  deps: [howler-subscriptions, howler-invoices, howler-payments, howler-webhooks, howler-notifications]
  branch: spectrum/billing-system-0331/howler-integration
  base_branch: main
  base_commit: 5e4c8b2
```

## Decomposition Rationale

I chose 6 Howlers because subscriptions, invoices, payments, webhooks, notifications, and integration are independent billing domains. howler-subscriptions runs first with no deps (plans are the root entity). howler-invoices depends on subscription types (invoices are created from subscription events). howler-payments is independent (Stripe integration is standalone). howler-webhooks depends on payments#types because it processes Stripe payment events and needs the PaymentIntent type. howler-notifications is independent (email templates don't depend on payment logic). howler-integration is sequential on all five because it wires everything together and can only write the router and integration tests when all modules exist. Alternative: merging payments+webhooks — rejected because Stripe webhook handling is a distinct infrastructure concern from payment creation.

## Politico Review

_Not yet conducted — pre-freeze review scheduled._
