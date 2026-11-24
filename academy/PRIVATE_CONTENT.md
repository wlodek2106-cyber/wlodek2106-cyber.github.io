# Private curriculum migration

The public repository and its history contain the legacy curriculum and exam answers. They cannot be made secret by deleting a file. Do not reuse those questions as a secure assessment.

Owner-only Private Curriculum accepts one new lesson or exam bank at a time, in JSON (request limit 16 KiB). Data is written to the existing Academy database, not GitHub. Every upload is versioned by revision number and the change is audited. Only the latest version is kept, not a full revision history. Student endpoints return lesson content only after enrollment/unlock checks; exam endpoints sample and shuffle questions without correct answers. The tutor uses the replacement lesson when available.

Populate original, independently reviewed banks for all 45 days in English, optionally add RU/UK/PL variants. Missing translations fall back to English. After verifying coverage, owner may enable ACADEMY_PRIVATE_EXAMS_REQUIRED=true and ACADEMY_PRIVATE_LESSONS_REQUIRED=true on Render. Without coverage, strict mode blocks the corresponding missing lessons/exams; do not enable prematurely. Existing public content, existing attempts, agent-lab and Pro library are not retroactively made private. Database encryption at the application level is not implemented. Never place new answer banks in public Git commits.
