from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from landsync.adapters.state.demo import DemoAuthorityAdapter
from landsync.auth import get_current_user, require_roles
from landsync.database import get_db
from landsync.models import ConsistencyReport, LandParcel, ReviewCase, Role
from landsync.repositories import (
    LandParcelRepository,
    MutationEventRepository,
    OwnershipRepository,
    ReviewCaseRepository,
    ValidationRepository,
)
from landsync.services import LocalEvidenceStorage, make_document, validate

router = APIRouter(prefix="/api/v1/parcels", tags=["Land Parcels & Spatial Cadastre"])
adapter = DemoAuthorityAdapter()
default_store = LocalEvidenceStorage()


@router.get("/search")
def search_parcels(
    q: Annotated[str, Query(min_length=1)] = "",
    _: tuple[str, Role] = Depends(require_roles(Role.CITIZEN, Role.OFFICER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Search synthetic land parcels across survey number, ULPIN, or village."""
    repo = LandParcelRepository(db)
    db_results = repo.search(q)
    if db_results:
        results = [
            {
                "parcel_id": p.id,
                "survey_number": p.survey_number,
                "village": p.village,
                "area": p.area,
                "owner": p.owner,
            }
            for p in db_results
        ]
    else:
        results = adapter.search(q)

    return {
        "query": q,
        "count": len(results),
        "results": results,
        "notice": "SYNTHETIC DEMO SEARCH: Results from local synthetic authority fixtures only.",
    }


@router.get("/{parcel_id}")
def get_parcel(
    parcel_id: str,
    _: tuple[str, Role] = Depends(require_roles(Role.CITIZEN, Role.OFFICER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Retrieve authoritative parcel cadastral details."""
    repo = LandParcelRepository(db)
    record = repo.get_dict(parcel_id)
    if not record:
        try:
            record = adapter.parcel(parcel_id)
        except KeyError:
            raise HTTPException(
                status_code=404,
                detail=f"Parcel '{parcel_id}' is not available in the demo dataset.",
            )
    return {
        "record": record,
        "notice": "SYNTHETIC DEMO DATA — not connected to government records.",
    }


@router.get("/{parcel_id}/ownership")
def get_ownership(
    parcel_id: str,
    _: tuple[str, Role] = Depends(require_roles(Role.CITIZEN, Role.OFFICER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Retrieve synthetic ownership titles and Khatedar details."""
    repo = OwnershipRepository(db)
    ownerships = repo.get_by_parcel(parcel_id)
    if ownerships:
        return {
            "parcel_id": parcel_id,
            "ownership": ownerships,
            "notice": "SYNTHETIC DEMO OWNERSHIP RECORD",
        }

    try:
        adapter.parcel(parcel_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Parcel is not available in the demo dataset.")
    return {
        "parcel_id": parcel_id,
        "ownership": adapter.ownership(parcel_id),
        "notice": "SYNTHETIC DEMO OWNERSHIP RECORD",
    }


@router.get("/{parcel_id}/history")
def get_history(
    parcel_id: str,
    _: tuple[str, Role] = Depends(require_roles(Role.CITIZEN, Role.OFFICER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Retrieve chronologically ordered mutation and transaction history."""
    repo = MutationEventRepository(db)
    mutations = repo.get_by_parcel(parcel_id)
    if mutations:
        return {
            "parcel_id": parcel_id,
            "mutation_history": mutations,
            "notice": "SYNTHETIC MUTATION TIMELINE: All historic records are demonstration fixtures.",
        }

    try:
        adapter.parcel(parcel_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Parcel is not available in the demo dataset.")
    return {
        "parcel_id": parcel_id,
        "mutation_history": adapter.mutation_history(parcel_id),
        "notice": "SYNTHETIC MUTATION TIMELINE: All historic records are demonstration fixtures.",
    }


@router.get("/{parcel_id}/report")
def report(
    parcel_id: str,
    _: tuple[str, Role] = Depends(require_roles(Role.CITIZEN, Role.OFFICER, Role.ADMIN)),
    db: Session = Depends(get_db),
) -> ConsistencyReport:
    """Generate comprehensive Digital Land Profile & Consistency Report."""
    try:
        parcel_model = adapter.parcel_model(parcel_id)
        auth_record = adapter.parcel(parcel_id)
    except KeyError:
        # Check DB
        repo_p = LandParcelRepository(db)
        p_orm = repo_p.get_by_id(parcel_id)
        if not p_orm:
            raise HTTPException(status_code=404, detail="Parcel is not available in the demo dataset.")
        parcel_model = LandParcel(
            id=p_orm.id,
            ulpin=p_orm.ulpin,
            survey_number=p_orm.survey_number,
            plot_number=p_orm.plot_number,
            state=p_orm.state,
            district=p_orm.district,
            tehsil=p_orm.tehsil,
            village=p_orm.village,
            area=p_orm.area,
            normalized_area_sqm=p_orm.normalized_area_sqm,
            land_use=p_orm.land_use,
            geometry=p_orm.geometry,
            geometry_source=p_orm.geometry_source,
            authoritative_source=p_orm.authoritative_source,
        )
        auth_record = {
            "parcel_id": p_orm.id,
            "ulpin": p_orm.ulpin,
            "survey_number": p_orm.survey_number,
            "plot_number": p_orm.plot_number,
            "owner": p_orm.owner,
            "area": p_orm.area,
            "state": p_orm.state,
            "district": p_orm.district,
            "tehsil": p_orm.tehsil,
            "village": p_orm.village,
            "land_use": p_orm.land_use,
            "geometry": p_orm.geometry,
        }

    # Ownership
    repo_own = OwnershipRepository(db)
    ownership = repo_own.get_by_parcel(parcel_id) or adapter.ownership(parcel_id)

    # Mutation history
    repo_mut = MutationEventRepository(db)
    mutation_history = repo_mut.get_by_parcel(parcel_id) or adapter.mutation_history(parcel_id)

    # Validation
    val_repo = ValidationRepository(db)
    val_results = val_repo.get_by_parcel(parcel_id)
    if not val_results:
        # Compute dynamic validation from synthetic baseline deed
        synth_doc = make_document(parcel_id, "seed_deed.pdf", "application/pdf", b"seed", "system", default_store)
        val_results = validate(synth_doc.extraction, auth_record)

    # Review case
    case_repo = ReviewCaseRepository(db)
    case_orm = case_repo.get_by_parcel(parcel_id)
    if case_orm:
        case = case_repo.to_domain(case_orm)
    else:
        case = ReviewCase(
            id=f"rc-{parcel_id.lower()}",
            parcel_id=parcel_id,
            reason="Synthetic baseline consistency review for demo parcel.",
            severity="LOW",
            status="OPEN",
            priority="P2_NORMAL",
        )

    return ConsistencyReport(
        parcel=parcel_model,
        ownership=ownership,
        validation_summary=val_results,
        review_case=case,
        mutation_history=mutation_history,
    )
