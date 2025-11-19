"""
API routes for building energy simulation
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.schemas import (
    SimulationRequest,
    SimulationResponse,
    PresetResponse,
    ConfigSaveRequest,
    ComparisonRequest,
    ComparisonResponse,
    CalibrationRequest,
    CalibrationResponse,
    CalibrationResult,
    FloorSpecSchema,
    EquipmentSpecSchema,
    MonthlyConditionSchema,
)
from app.models.building_energy_model import (
    BuildingEnergyModel,
    FloorSpec,
    EquipmentSpec,
    MonthlyCondition,
)
from app.models.presets import get_modern_office_preset, get_old_office_preset
from app.calibration import (
    calculate_metrics,
    extract_comparison_values,
    grid_search_calibration,
    optimize_calibration,
)
from typing import List
import json
import io
from datetime import datetime

router = APIRouter()


def convert_schema_to_dataclass(floor_spec: FloorSpecSchema,
                                equipment_spec: EquipmentSpecSchema,
                                monthly_conditions: List[MonthlyConditionSchema]):
    """Convert Pydantic schemas to dataclasses"""
    floor = FloorSpec(**floor_spec.model_dump())
    equipment = EquipmentSpec(**equipment_spec.model_dump())
    conditions = [MonthlyCondition(**cond.model_dump()) for cond in monthly_conditions]
    return floor, equipment, conditions


def convert_preset_to_schema(preset: dict) -> PresetResponse:
    """Convert preset dict to Pydantic schema"""
    return PresetResponse(
        name=preset['name'],
        description=preset['description'],
        floor_spec=FloorSpecSchema(**preset['floor_spec'].__dict__),
        equipment_spec=EquipmentSpecSchema(**preset['equipment_spec'].__dict__),
        monthly_conditions=[
            MonthlyConditionSchema(**cond.__dict__)
            for cond in preset['monthly_conditions']
        ]
    )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@router.post("/simulate", response_model=SimulationResponse)
async def simulate(request: SimulationRequest):
    """
    Run building energy simulation
    """
    try:
        # Convert schemas to dataclasses
        floor, equipment, conditions = convert_schema_to_dataclass(
            request.floor_spec,
            request.equipment_spec,
            request.monthly_conditions
        )

        # Create model and run simulation
        model = BuildingEnergyModel(floor, equipment, conditions)
        results_df = model.simulate_year()

        # Convert results to response format
        results = results_df.to_dict('records')

        # Calculate summary statistics
        # Get total operation hours from input conditions
        total_operation_hours = sum(cond.operation_hours for cond in conditions)

        summary = {
            "annual_central_total_kWh": float(results_df['central_total_kWh'].sum()),
            "annual_local_total_kWh": float(results_df['local_total_kWh'].sum()),
            "annual_total_load_kWh": float(results_df['total_load_kW'].sum() * total_operation_hours / 12),
            "average_monthly_load_kW": float(results_df['total_load_kW'].mean()),
        }

        return SimulationResponse(results=results, summary=summary)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets/modern", response_model=PresetResponse)
async def get_modern_preset():
    """Get modern office preset configuration"""
    try:
        preset = get_modern_office_preset()
        return convert_preset_to_schema(preset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets/old", response_model=PresetResponse)
async def get_old_preset():
    """Get old office preset configuration"""
    try:
        preset = get_old_office_preset()
        return convert_preset_to_schema(preset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/presets")
async def list_presets():
    """List available presets"""
    return {
        "presets": [
            {
                "id": "modern",
                "name": "最新オフィス",
                "description": "高効率設備を備えた最新オフィスビル"
            },
            {
                "id": "old",
                "name": "旧式オフィス",
                "description": "従来型設備の旧式オフィスビル"
            }
        ]
    }


@router.post("/config/save")
async def save_config(request: ConfigSaveRequest):
    """Save configuration as JSON"""
    try:
        # Create config dict
        config = {
            "name": request.name,
            "description": request.description,
            "floor_spec": request.floor_spec.model_dump(),
            "equipment_spec": request.equipment_spec.model_dump(),
            "monthly_conditions": [cond.model_dump() for cond in request.monthly_conditions]
        }

        # Create JSON string
        config_json = json.dumps(config, ensure_ascii=False, indent=2)

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{request.name}_{timestamp}.json"

        # Return as downloadable file
        return StreamingResponse(
            io.BytesIO(config_json.encode('utf-8')),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/results/save")
async def save_results(request: SimulationRequest):
    """Run simulation and save results as CSV"""
    try:
        # Convert schemas to dataclasses
        floor, equipment, conditions = convert_schema_to_dataclass(
            request.floor_spec,
            request.equipment_spec,
            request.monthly_conditions
        )

        # Create model and run simulation
        model = BuildingEnergyModel(floor, equipment, conditions)
        results_df = model.simulate_year()

        # Convert to CSV
        csv_buffer = io.StringIO()
        results_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_content = csv_buffer.getvalue()

        # Create filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simulation_results_{timestamp}.csv"

        # Return as downloadable file
        return StreamingResponse(
            io.BytesIO(csv_content.encode('utf-8-sig')),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare", response_model=ComparisonResponse)
async def compare_with_actual(request: ComparisonRequest):
    """
    Compare simulation results with actual data
    """
    try:
        # Convert schemas to dataclasses
        floor, equipment, conditions = convert_schema_to_dataclass(
            request.floor_spec,
            request.equipment_spec,
            request.monthly_conditions
        )

        # Run simulation
        model = BuildingEnergyModel(floor, equipment, conditions)
        results_df = model.simulate_year()

        # Extract comparison values
        simulated, actual = extract_comparison_values(
            results_df, request.actual_data, request.comparison_target
        )

        # Calculate metrics
        metrics = calculate_metrics(simulated, actual)

        return ComparisonResponse(
            simulation_results=results_df.to_dict('records'),
            actual_data=request.actual_data,
            metrics=metrics,
            comparison_target=request.comparison_target,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calibrate", response_model=CalibrationResponse)
async def calibrate_parameters(request: CalibrationRequest):
    """
    Calibrate parameters to match actual data
    """
    try:
        # Convert schemas to dataclasses
        floor, equipment, conditions = convert_schema_to_dataclass(
            request.floor_spec,
            request.equipment_spec,
            request.monthly_conditions
        )

        # Choose calibration method
        if request.method == "grid":
            results = grid_search_calibration(
                floor,
                equipment,
                conditions,
                request.actual_data,
                request.comparison_target,
                request.parameter_ranges,
            )
        elif request.method == "optimize":
            results = optimize_calibration(
                floor,
                equipment,
                conditions,
                request.actual_data,
                request.comparison_target,
                request.parameter_ranges,
            )
        else:
            raise ValueError(f"Unknown calibration method: {request.method}")

        # Convert results to CalibrationResult objects
        calibration_results = [
            CalibrationResult(**result) for result in results
        ]

        return CalibrationResponse(
            best_result=calibration_results[0],
            all_results=calibration_results,
            method=request.method,
            iterations=len(calibration_results),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
