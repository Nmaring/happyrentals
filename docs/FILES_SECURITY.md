File security baseline:
- Store files in private S3-compatible storage (MinIO locally; S3 in production)
- Store only metadata in DB; never public URLs
- Serve downloads via short-lived signed URLs after RBAC checks
- Tenant access: only their lease/docs/receipts
- Landlord access: anything within org
- Add checksum (sha256), size limit, MIME allowlist
- Add malware scanning pipeline before marking file "available" (Phase 2)
