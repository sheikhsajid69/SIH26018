# Design System

## Philosophy and Brand

LANDSYNC should feel like dependable digital public infrastructure: calm, specific, legible, and evidentiary—not an AI startup. The brand uses a deep ink-blue foundation, paper-like surfaces, teal for confirmed consistency, and saffron for review-required attention. “MOCK / SYNTHETIC / NOT CONNECTED” notices are first-class interface elements, not footnotes.

## Foundations

Use a practical sans-serif system stack; data labels are compact uppercase and values are readable sentence case. Core colors: navy `#102A43`, ink `#17324D`, paper `#F7F5EF`, teal `#0E7490`, saffron `#C66A12`, border `#D8DEE6`, positive `#176B4D`. Use a 4px spacing rhythm, generous 16–24px card padding, and sharp-but-not-harsh 10–14px radii.

## Components and Information

The responsive shell contains institutional navigation, a role context, the Digital Land Profile heading, legal advisory status, and a compact source legend. Cards organize status, parcel facts, documents, provenance, confidence, GIS/blueprint, validation matrix, review workflow, and audit timeline. Tables retain field/document/authority/result labels on mobile through stacked rows. Status always includes text and an icon/shape, never color alone.

## Key States

Upload is a labelled drop zone with file constraints and progress. The document viewer exposes original vs derived output and hash. The map calls geometry “synthetic demo GeoJSON” until an authorized dataset exists; a blueprint overlay labels detected/unknown edges separately. Confidence is numeric and describes method/provider. Validation matrix distinguishes MATCH, PARTIAL_MATCH, MISMATCH, MISSING, and REVIEW_REQUIRED. Officer review requires a reason and displays the immutable audit consequence.

## Accessibility and Responsive Behavior

Use semantic landmarks, headings, labelled inputs, keyboard-operable file controls, visible focus rings, 4.5:1 text contrast, live status announcements, and table alternatives on narrow screens. Empty states say “Not available” or “Not connected”; loading preserves layout; errors expose an action and request-safe message; confirmations state what evidence or review action was recorded. Future i18n extracts user-facing strings and supports Indian regional language review without asserting untested OCR capability.

## Role-Specific UI

Citizen surfaces their permitted parcels, upload, extracted values, and review request. Officer additionally receives discrepancy queue, source comparison, notes, and decision controls. Administrator receives adapter/dataset/configuration health only; it does not grant magical record-edit capability.
