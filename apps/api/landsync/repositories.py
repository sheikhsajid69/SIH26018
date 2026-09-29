from __future__ import annotations

from typing import Any
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, joinedload
from landsync.db_models import (
    AdministrativeActionOrm,
    AuditEventOrm,
    DocumentOrm,
    ExtractedFieldOrm,
    ExtractionOrm,
    LandParcelOrm,
    MutationEventOrm,
    OwnershipRelationshipOrm,
    ReviewCaseOrm,
    UserOrm,
    ValidationResultOrm,
)
from landsync.models import (
    AuditEvent,
    Document,
    ExtractedField,
    Extraction,
    LandParcel,
    MutationEvent,
    OwnershipRelationship,
    ReviewCase,
    ValidationResult,
    ValidationState,
)


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: str) -> UserOrm | None:
        return self.db.execute(select(UserOrm).where(UserOrm.id == user_id)).scalar_one_or_none()

    def get_by_username(self, username: str) -> UserOrm | None:
        return self.db.execute(select(UserOrm).where(UserOrm.username == username)).scalar_one_or_none()

    def get_by_email(self, email: str) -> UserOrm | None:
        return self.db.execute(select(UserOrm).where(UserOrm.email == email)).scalar_one_or_none()

    def get_by_email_or_username(self, identifier: str) -> UserOrm | None:
        clean = identifier.strip()
        return self.db.execute(
            select(UserOrm).where(
                or_(
                    UserOrm.username == clean,
                    UserOrm.email == clean,
                    UserOrm.id == clean,
                )
            )
        ).scalar_one_or_none()

    def list_users(
        self,
        search: str | None = None,
        role: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[UserOrm], int]:
        stmt = select(UserOrm)
        if search:
            q = f"%{search.strip()}%"
            stmt = stmt.where(or_(UserOrm.name.ilike(q), UserOrm.email.ilike(q), UserOrm.username.ilike(q), UserOrm.id.ilike(q)))
        if role:
            stmt = stmt.where(UserOrm.role == role)
        if status:
            stmt = stmt.where(UserOrm.status == status)

        total = len(self.db.execute(stmt).scalars().all())
        users = self.db.execute(stmt.order_by(UserOrm.created_at.desc()).offset(offset).limit(limit)).scalars().all()
        return list(users), total

    def update_status(self, user_id: str, new_status: str) -> UserOrm | None:
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.status = new_status
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_role(self, user_id: str, new_role: str) -> UserOrm | None:
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.role = new_role
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_last_login(self, user_id: str) -> None:
        from datetime import datetime, timezone
        user = self.get_by_id(user_id) or self.get_by_username(user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
            self.db.commit()

    def list_officers(self) -> list[UserOrm]:
        return list(self.db.execute(select(UserOrm).where(UserOrm.role == "revenue_officer")).scalars().all())

    def create(self, user_orm: UserOrm) -> UserOrm:
        self.db.add(user_orm)
        self.db.commit()
        self.db.refresh(user_orm)
        return user_orm

    def count(self) -> int:
        return len(self.db.execute(select(UserOrm.id)).scalars().all())


class LandParcelRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, parcel_id: str) -> LandParcel | None:
        orm = self.db.execute(select(LandParcelOrm).where(LandParcelOrm.id == parcel_id)).scalar_one_or_none()
        return self._to_model(orm) if orm else None

    get_by_id = get
    get_parcel = get

    def get_orm(self, parcel_id: str) -> LandParcelOrm | None:
        return self.db.execute(select(LandParcelOrm).where(LandParcelOrm.id == parcel_id)).scalar_one_or_none()

    def get_dict(self, parcel_id: str) -> dict[str, Any] | None:
        orm = self.get_orm(parcel_id)
        if not orm:
            return None
        return {
            "id": orm.id,
            "ulpin": orm.ulpin,
            "survey_number": orm.survey_number,
            "plot_number": orm.plot_number,
            "owner": orm.owner,
            "area": orm.area,
            "area_unit": orm.area_unit,
            "normalized_area_sqm": orm.normalized_area_sqm,
            "state": orm.state,
            "district": orm.district,
            "tehsil": orm.tehsil,
            "village": orm.village,
            "land_use": orm.land_use,
            "geometry": orm.geometry,
            "geometry_source": orm.geometry_source,
            "authoritative_source": orm.authoritative_source,
        }

    def list_all_ids(self) -> list[str]:
        return list(self.db.execute(select(LandParcelOrm.id)).scalars().all())

    def search(self, query: str) -> list[dict[str, Any]]:
        q = f"%{query.strip().lower()}%"
        stmt = select(LandParcelOrm).where(
            or_(
                LandParcelOrm.id.ilike(q),
                LandParcelOrm.ulpin.ilike(q),
                LandParcelOrm.survey_number.ilike(q),
                LandParcelOrm.village.ilike(q),
                LandParcelOrm.owner.ilike(q),
                LandParcelOrm.district.ilike(q),
            )
        )
        results = self.db.execute(stmt).scalars().all()
        return [self.get_dict(p.id) for p in results if p is not None]  # type: ignore

    def upsert(self, orm: LandParcelOrm) -> LandParcel:
        existing = self.get_orm(orm.id)
        if existing:
            for k in ("ulpin", "survey_number", "plot_number", "owner", "area", "normalized_area_sqm", "state", "district", "tehsil", "village", "land_use", "geometry", "geometry_source", "authoritative_source"):
                setattr(existing, k, getattr(orm, k))
            self.db.commit()
            self.db.refresh(existing)
            return self._to_model(existing)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_model(orm)

    def count(self) -> int:
        return len(self.db.execute(select(LandParcelOrm.id)).scalars().all())

    @staticmethod
    def _to_model(orm: LandParcelOrm) -> LandParcel:
        return LandParcel(
            id=orm.id,
            ulpin=orm.ulpin,
            survey_number=orm.survey_number,
            plot_number=orm.plot_number,
            state=orm.state,
            district=orm.district,
            tehsil=orm.tehsil,
            village=orm.village,
            area=orm.area,
            normalized_area_sqm=orm.normalized_area_sqm,
            land_use=orm.land_use,
            geometry=orm.geometry or {},
            geometry_source=orm.geometry_source,
            authoritative_source=orm.authoritative_source,
        )


class OwnershipRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_parcel(self, parcel_id: str) -> list[OwnershipRelationship]:
        stmt = select(OwnershipRelationshipOrm).where(OwnershipRelationshipOrm.parcel_id == parcel_id)
        rows = self.db.execute(stmt).scalars().all()
        return [
            OwnershipRelationship(
                id=r.id,
                parcel_id=r.parcel_id,
                holder_name=r.holder_name,
                share_extent=r.share_extent,
                relationship_type=r.relationship_type,
                recorded_date=r.recorded_date,
                source_ref=r.source_ref,
                is_synthetic=r.is_synthetic,
            )
            for r in rows
        ]

    def add(self, orm: OwnershipRelationshipOrm) -> None:
        self.db.add(orm)
        self.db.commit()


class MutationEventRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_parcel(self, parcel_id: str) -> list[MutationEvent]:
        stmt = select(MutationEventOrm).where(MutationEventOrm.parcel_id == parcel_id).order_by(MutationEventOrm.recorded_date.asc())
        rows = self.db.execute(stmt).scalars().all()
        return [
            MutationEvent(
                id=r.id,
                parcel_id=r.parcel_id,
                mutation_number=r.mutation_number,
                event_type=r.event_type,
                recorded_date=r.recorded_date,
                parties_involved=r.parties_involved,
                description=r.description,
                order_reference=r.order_reference,
                is_synthetic=r.is_synthetic,
            )
            for r in rows
        ]

    def add(self, orm: MutationEventOrm) -> None:
        self.db.add(orm)
        self.db.commit()


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, document_id: str) -> Document | None:
        stmt = select(DocumentOrm).options(
            joinedload(DocumentOrm.extraction).joinedload(ExtractionOrm.fields)
        ).where(DocumentOrm.id == document_id)
        orm = self.db.execute(stmt).unique().scalar_one_or_none()
        return self._to_model(orm) if orm else None

    def get_by_hash(self, sha256_hash: str) -> Document | None:
        stmt = select(DocumentOrm).options(
            joinedload(DocumentOrm.extraction).joinedload(ExtractionOrm.fields)
        ).where(DocumentOrm.sha256 == sha256_hash)
        orm = self.db.execute(stmt).unique().scalar_one_or_none()
        return self._to_model(orm) if orm else None

    def list_by_parcel(self, parcel_id: str) -> list[Document]:
        stmt = select(DocumentOrm).options(
            joinedload(DocumentOrm.extraction).joinedload(ExtractionOrm.fields)
        ).where(DocumentOrm.parcel_id == parcel_id).order_by(DocumentOrm.uploaded_at.desc())
        rows = self.db.execute(stmt).unique().scalars().all()
        return [self._to_model(r) for r in rows]

    def list_all(self, limit: int = 100) -> list[Document]:
        stmt = select(DocumentOrm).options(
            joinedload(DocumentOrm.extraction).joinedload(ExtractionOrm.fields)
        ).order_by(DocumentOrm.uploaded_at.desc()).limit(limit)
        rows = self.db.execute(stmt).unique().scalars().all()
        return [self._to_model(r) for r in rows]

    def count(self) -> int:
        return len(self.db.execute(select(DocumentOrm.id)).scalars().all())

    def save(self, doc_model: Document) -> Document:
        existing_orm = self.db.execute(
            select(DocumentOrm).options(
                joinedload(DocumentOrm.extraction).joinedload(ExtractionOrm.fields)
            ).where(
                or_(
                    DocumentOrm.id == doc_model.id,
                    DocumentOrm.storage_key == doc_model.storage_key,
                )
            )
        ).unique().scalar_one_or_none()
        if existing_orm:
            return self._to_model(existing_orm)

        doc_orm = DocumentOrm(
            id=doc_model.id,
            parcel_id=doc_model.parcel_id,
            document_type=doc_model.document_type,
            original_file_name=doc_model.original_file_name,
            mime_type=doc_model.mime_type,
            storage_key=doc_model.storage_key,
            sha256=doc_model.sha256,
            file_size=doc_model.file_size,
            source=doc_model.source,
            uploaded_by=doc_model.uploaded_by,
            uploaded_at=doc_model.uploaded_at,
            version=doc_model.version,
            processing_status=doc_model.processing_status,
        )
        self.db.add(doc_orm)

        if doc_model.extraction:
            ext_orm = ExtractionOrm(
                id=f"ext-{doc_model.id}",
                document_id=doc_model.id,
                provider=doc_model.extraction.provider,
                model_version=doc_model.extraction.model_version,
                created_at=doc_model.extraction.created_at,
            )
            self.db.add(ext_orm)
            for f in doc_model.extraction.fields:
                field_orm = ExtractedFieldOrm(
                    id=f"ef-{doc_model.id}-{f.field_name}",
                    extraction_id=ext_orm.id,
                    field_name=f.field_name,
                    extracted_value=f.extracted_value,
                    normalized_value=f.normalized_value,
                    confidence=f.confidence,
                    source_location=f.source_location,
                    page_number=f.page_number,
                    extraction_method=f.extraction_method,
                    reviewer_status=f.reviewer_status,
                )
                self.db.add(field_orm)

        self.db.commit()
        return self.get(doc_model.id) or doc_model

    save_document = save
    get_by_id = get

    @staticmethod
    def _to_model(orm: DocumentOrm) -> Document:
        ext_model = None
        if orm.extraction:
            fields = [
                ExtractedField(
                    field_name=f.field_name,
                    extracted_value=f.extracted_value,
                    normalized_value=f.normalized_value,
                    confidence=f.confidence,
                    source_location=f.source_location,
                    page_number=f.page_number,
                    extraction_method=f.extraction_method,
                    reviewer_status=f.reviewer_status,
                )
                for f in orm.extraction.fields
            ]
            ext_model = Extraction(
                provider=orm.extraction.provider,
                model_version=orm.extraction.model_version,
                created_at=orm.extraction.created_at,
                fields=fields,
            )

        return Document(
            id=orm.id,
            parcel_id=orm.parcel_id,
            document_type=orm.document_type,
            original_file_name=orm.original_file_name,
            mime_type=orm.mime_type,
            storage_key=orm.storage_key,
            sha256=orm.sha256,
            file_size=orm.file_size,
            source=orm.source,
            uploaded_by=orm.uploaded_by,
            uploaded_at=orm.uploaded_at,
            version=orm.version,
            processing_status=orm.processing_status,
            extraction=ext_model,
        )


class ValidationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save_batch(self, parcel_id: str, document_id: str | None, results: list[ValidationResult]) -> None:
        for r in results:
            orm = ValidationResultOrm(
                id=f"val-{parcel_id}-{r.field}-{r.created_at.timestamp()}",
                parcel_id=parcel_id,
                document_id=document_id,
                field=r.field,
                source_a=r.source_a,
                value_a=r.value_a,
                source_b=r.source_b,
                value_b=r.value_b,
                comparison_operator=r.comparison_operator,
                result=r.result.value,
                confidence=r.confidence,
                severity=r.severity,
                explanation=r.explanation,
                created_at=r.created_at,
            )
            self.db.add(orm)
        self.db.commit()

    save_results = save_batch

    def get_by_parcel(self, parcel_id: str) -> list[ValidationResult]:
        stmt = select(ValidationResultOrm).where(ValidationResultOrm.parcel_id == parcel_id).order_by(ValidationResultOrm.created_at.desc()).limit(10)
        rows = self.db.execute(stmt).scalars().all()
        return [
            ValidationResult(
                field=r.field,
                source_a=r.source_a,
                value_a=r.value_a,
                source_b=r.source_b,
                value_b=r.value_b,
                comparison_operator=r.comparison_operator,
                result=ValidationState(r.result),
                confidence=r.confidence,
                severity=r.severity,
                explanation=r.explanation,
                created_at=r.created_at,
            )
            for r in rows
        ]


class ReviewCaseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, case_id: str) -> ReviewCase | None:
        orm = self.db.execute(select(ReviewCaseOrm).where(ReviewCaseOrm.id == case_id)).scalar_one_or_none()
        return self._to_model(orm) if orm else None

    def get_orm(self, case_id: str) -> ReviewCaseOrm | None:
        return self.db.execute(select(ReviewCaseOrm).where(ReviewCaseOrm.id == case_id)).scalar_one_or_none()

    def list_cases(self, status: str | None = None, status_filter: str | None = None) -> list[ReviewCase]:
        stmt = select(ReviewCaseOrm)
        filter_status = status or status_filter
        if filter_status:
            stmt = stmt.where(ReviewCaseOrm.status == filter_status.upper())
        stmt = stmt.order_by(ReviewCaseOrm.created_at.desc())
        rows = self.db.execute(stmt).scalars().all()
        return [self._to_model(r) for r in rows]

    def get_by_parcel_and_field(self, parcel_id: str, field: str, status: str = "OPEN") -> ReviewCase | None:
        stmt = select(ReviewCaseOrm).where(
            ReviewCaseOrm.parcel_id == parcel_id,
            ReviewCaseOrm.discrepancy_field == field,
            ReviewCaseOrm.status == status,
        )
        orm = self.db.execute(stmt).scalar_one_or_none()
        return self._to_model(orm) if orm else None

    def upsert(self, case: ReviewCase, document_id: str | None = None) -> ReviewCase:
        existing = self.get_orm(case.id)
        if existing:
            existing.status = case.status
            existing.assigned_officer = case.assigned_officer
            existing.reviewer_notes = case.reviewer_notes
            existing.resolution = case.resolution
            existing.resolved_at = case.resolved_at
            if document_id:
                existing.document_id = document_id
            self.db.commit()
            self.db.refresh(existing)
            return self._to_model(existing)

        orm = ReviewCaseOrm(
            id=case.id,
            parcel_id=case.parcel_id,
            document_id=document_id,
            reason=case.reason,
            severity=case.severity,
            status=case.status,
            priority=case.priority,
            discrepancy_field=case.discrepancy_field,
            claimed_value=case.claimed_value,
            authoritative_value=case.authoritative_value,
            assigned_officer=case.assigned_officer,
            reviewer_notes=case.reviewer_notes,
            resolution=case.resolution,
            created_at=case.created_at,
            resolved_at=case.resolved_at,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return self._to_model(orm)

    def count_open(self) -> int:
        stmt = select(ReviewCaseOrm.id).where(ReviewCaseOrm.status == "OPEN")
        return len(self.db.execute(stmt).scalars().all())

    get_by_id = get_orm
    create_or_update = upsert
    list_all = list_cases

    def get_by_parcel(self, parcel_id: str) -> ReviewCaseOrm | None:
        stmt = select(ReviewCaseOrm).where(ReviewCaseOrm.parcel_id == parcel_id).order_by(ReviewCaseOrm.created_at.desc())
        return self.db.execute(stmt).scalars().first()

    @classmethod
    def to_domain(cls, orm: ReviewCaseOrm) -> ReviewCase:
        return cls._to_model(orm)

    @staticmethod
    def _to_model(orm: ReviewCaseOrm) -> ReviewCase:
        return ReviewCase(
            id=orm.id,
            parcel_id=orm.parcel_id,
            reason=orm.reason,
            severity=orm.severity,
            status=orm.status,
            priority=orm.priority,
            discrepancy_field=orm.discrepancy_field,
            claimed_value=orm.claimed_value,
            authoritative_value=orm.authoritative_value,
            assigned_officer=orm.assigned_officer,
            reviewer_notes=orm.reviewer_notes,
            resolution=orm.resolution,
            created_at=orm.created_at,
            resolved_at=orm.resolved_at,
        )


class AuditRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def append(self, event: AuditEvent) -> AuditEvent:
        orm = AuditEventOrm(
            actor_id=event.actor_id,
            action=event.action,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            timestamp=event.timestamp,
            before_state=event.before_state,
            after_state=event.after_state,
            reason=event.reason,
            trace_id=event.trace_id,
        )
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return AuditEvent(
            id=orm.id,
            actor_id=orm.actor_id,
            action=orm.action,
            entity_type=orm.entity_type,
            entity_id=orm.entity_id,
            timestamp=orm.timestamp,
            before_state=orm.before_state,
            after_state=orm.after_state,
            reason=orm.reason,
            trace_id=orm.trace_id,
        )

    def list_all(self, limit: int = 100, actor_id: str | None = None, entity_type: str | None = None) -> list[AuditEvent]:
        stmt = select(AuditEventOrm)
        if actor_id:
            stmt = stmt.where(AuditEventOrm.actor_id == actor_id)
        if entity_type:
            stmt = stmt.where(AuditEventOrm.entity_type == entity_type)
        stmt = stmt.order_by(AuditEventOrm.timestamp.desc()).limit(limit)
        rows = self.db.execute(stmt).scalars().all()
        return [
            AuditEvent(
                id=r.id,
                actor_id=r.actor_id,
                action=r.action,
                entity_type=r.entity_type,
                entity_id=r.entity_id,
                timestamp=r.timestamp,
                before_state=r.before_state,
                after_state=r.after_state,
                reason=r.reason,
                trace_id=r.trace_id,
            )
            for r in rows
        ]

    list_events = list_all

    def log(
        self,
        actor_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        before_state: dict[str, Any] | None = None,
        after_state: dict[str, Any] | None = None,
        before: dict[str, Any] | None = None,
        after: dict[str, Any] | None = None,
        reason: str | None = None,
        trace_id: str | None = None,
    ) -> AuditEvent:
        from uuid import uuid4
        event = AuditEvent(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_state=before_state or before,
            after_state=after_state or after,
            reason=reason,
            trace_id=trace_id or uuid4().hex,
        )
        return self.append(event)

    def count(self) -> int:
        return len(self.db.execute(select(AuditEventOrm.id)).scalars().all())


class AdministrativeActionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, action: AdministrativeActionOrm) -> AdministrativeActionOrm:
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action

    def list_actions(
        self,
        action_type: str | None = None,
        actor_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[AdministrativeActionOrm], int]:
        stmt = select(AdministrativeActionOrm)
        if action_type:
            stmt = stmt.where(AdministrativeActionOrm.action_type == action_type)
        if actor_id:
            stmt = stmt.where(AdministrativeActionOrm.actor_id == actor_id)

        total = len(self.db.execute(stmt).scalars().all())
        actions = self.db.execute(
            stmt.order_by(AdministrativeActionOrm.created_at.desc()).offset(offset).limit(limit)
        ).scalars().all()
        return list(actions), total

    def count(self) -> int:
        return len(self.db.execute(select(AdministrativeActionOrm.id)).scalars().all())
