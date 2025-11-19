"""
Calibration utilities for matching simulation with actual data
"""
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Any
from copy import deepcopy
from scipy.optimize import differential_evolution
from app.models.building_energy_model import (
    BuildingEnergyModel,
    FloorSpec,
    EquipmentSpec,
    MonthlyCondition,
)
from app.schemas import (
    ActualDataSchema,
    ComparisonMetrics,
    ParameterRange,
)


def calculate_metrics(
    simulated: List[float],
    actual: List[float]
) -> ComparisonMetrics:
    """
    Calculate comparison metrics between simulated and actual data

    Args:
        simulated: List of simulated values
        actual: List of actual values

    Returns:
        ComparisonMetrics with calculated metrics
    """
    sim_array = np.array(simulated)
    act_array = np.array(actual)

    # Remove NaN values
    mask = ~(np.isnan(sim_array) | np.isnan(act_array))
    sim_array = sim_array[mask]
    act_array = act_array[mask]

    if len(sim_array) == 0:
        raise ValueError("No valid data points for comparison")

    # Calculate errors
    errors = sim_array - act_array
    abs_errors = np.abs(errors)

    # RMSE (Root Mean Square Error)
    rmse = float(np.sqrt(np.mean(errors ** 2)))

    # MAE (Mean Absolute Error)
    mae = float(np.mean(abs_errors))

    # MAPE (Mean Absolute Percentage Error)
    # Avoid division by zero
    mape_mask = act_array != 0
    if np.any(mape_mask):
        mape = float(np.mean(np.abs(errors[mape_mask] / act_array[mape_mask]) * 100))
    else:
        mape = 0.0

    # R-squared (Coefficient of determination)
    ss_res = np.sum(errors ** 2)
    ss_tot = np.sum((act_array - np.mean(act_array)) ** 2)
    r_squared = float(1 - (ss_res / ss_tot) if ss_tot != 0 else 0)

    # Max error
    max_error_idx = int(np.argmax(abs_errors))
    max_error = float(abs_errors[max_error_idx])
    max_error_month = int(max_error_idx + 1)  # 1-indexed month

    return ComparisonMetrics(
        rmse=rmse,
        mae=mae,
        mape=mape,
        r_squared=r_squared,
        max_error=max_error,
        max_error_month=max_error_month,
    )


def run_simulation_with_params(
    floor_spec: FloorSpec,
    equipment_spec: EquipmentSpec,
    monthly_conditions: List[MonthlyCondition],
    parameters: Dict[str, float],
) -> pd.DataFrame:
    """
    Run simulation with modified parameters

    Args:
        floor_spec: Floor specification
        equipment_spec: Equipment specification
        monthly_conditions: Monthly conditions
        parameters: Dictionary of parameters to modify (e.g., {"floor_spec.wall_u_value": 0.5})

    Returns:
        DataFrame with simulation results
    """
    # Deep copy to avoid modifying originals
    floor = deepcopy(floor_spec)
    equipment = deepcopy(equipment_spec)

    # Apply parameter modifications
    for param_name, value in parameters.items():
        parts = param_name.split('.')
        if parts[0] == 'floor_spec':
            setattr(floor, parts[1], value)
        elif parts[0] == 'equipment_spec':
            setattr(equipment, parts[1], value)

    # Run simulation
    model = BuildingEnergyModel(floor, equipment, monthly_conditions)
    results_df = model.simulate_year()

    return results_df


def extract_comparison_values(
    results_df: pd.DataFrame,
    actual_data: List[ActualDataSchema],
    comparison_target: str,
) -> Tuple[List[float], List[float]]:
    """
    Extract simulated and actual values for comparison

    Args:
        results_df: Simulation results DataFrame
        actual_data: Actual data
        comparison_target: Target column name (e.g., "total_kWh")

    Returns:
        Tuple of (simulated_values, actual_values)
    """
    simulated = []
    actual = []

    for data in actual_data:
        month_idx = data.month - 1  # Convert to 0-indexed

        # Get actual value
        actual_value = getattr(data, comparison_target)
        if actual_value is None:
            continue

        # Get simulated value
        if comparison_target == "total_kWh":
            sim_value = (
                results_df.iloc[month_idx]['central_total_kWh'] +
                results_df.iloc[month_idx]['local_total_kWh']
            )
        else:
            sim_value = results_df.iloc[month_idx][comparison_target]

        simulated.append(float(sim_value))
        actual.append(float(actual_value))

    return simulated, actual


def grid_search_calibration(
    floor_spec: FloorSpec,
    equipment_spec: EquipmentSpec,
    monthly_conditions: List[MonthlyCondition],
    actual_data: List[ActualDataSchema],
    comparison_target: str,
    parameter_ranges: List[ParameterRange],
    max_combinations: int = 1000,
) -> List[Dict[str, Any]]:
    """
    Perform grid search calibration

    Args:
        floor_spec: Floor specification
        equipment_spec: Equipment specification
        monthly_conditions: Monthly conditions
        actual_data: Actual data
        comparison_target: Target column for comparison
        parameter_ranges: List of parameter ranges to search
        max_combinations: Maximum number of combinations to try

    Returns:
        List of results sorted by RMSE
    """
    # Generate parameter grids
    param_grids = {}
    for param_range in parameter_ranges:
        if param_range.step is not None:
            values = np.arange(
                param_range.min_value,
                param_range.max_value + param_range.step / 2,
                param_range.step
            )
        else:
            values = np.linspace(
                param_range.min_value,
                param_range.max_value,
                param_range.num_steps
            )
        param_grids[param_range.parameter_name] = values

    # Generate all combinations
    from itertools import product

    param_names = list(param_grids.keys())
    param_values = list(param_grids.values())

    results = []
    combinations = list(product(*param_values))

    # Limit combinations
    if len(combinations) > max_combinations:
        # Sample randomly
        import random
        combinations = random.sample(combinations, max_combinations)

    for combo in combinations:
        parameters = dict(zip(param_names, combo))

        # Run simulation
        results_df = run_simulation_with_params(
            floor_spec, equipment_spec, monthly_conditions, parameters
        )

        # Extract comparison values
        simulated, actual = extract_comparison_values(
            results_df, actual_data, comparison_target
        )

        # Calculate metrics
        metrics = calculate_metrics(simulated, actual)

        results.append({
            'parameters': parameters,
            'metrics': metrics,
            'simulation_results': results_df.to_dict('records'),
        })

    # Sort by RMSE
    results.sort(key=lambda x: x['metrics'].rmse)

    return results


def optimize_calibration(
    floor_spec: FloorSpec,
    equipment_spec: EquipmentSpec,
    monthly_conditions: List[MonthlyCondition],
    actual_data: List[ActualDataSchema],
    comparison_target: str,
    parameter_ranges: List[ParameterRange],
    max_iterations: int = 100,
) -> List[Dict[str, Any]]:
    """
    Perform optimization-based calibration using differential evolution

    Args:
        floor_spec: Floor specification
        equipment_spec: Equipment specification
        monthly_conditions: Monthly conditions
        actual_data: Actual data
        comparison_target: Target column for comparison
        parameter_ranges: List of parameter ranges
        max_iterations: Maximum number of iterations

    Returns:
        List with best result and optimization history
    """
    # Prepare bounds and parameter names
    bounds = []
    param_names = []
    for param_range in parameter_ranges:
        bounds.append((param_range.min_value, param_range.max_value))
        param_names.append(param_range.parameter_name)

    # Store optimization history
    history = []

    def objective_function(x):
        """Objective function to minimize (RMSE)"""
        parameters = dict(zip(param_names, x))

        try:
            # Run simulation
            results_df = run_simulation_with_params(
                floor_spec, equipment_spec, monthly_conditions, parameters
            )

            # Extract comparison values
            simulated, actual = extract_comparison_values(
                results_df, actual_data, comparison_target
            )

            # Calculate metrics
            metrics = calculate_metrics(simulated, actual)

            # Store in history
            history.append({
                'parameters': parameters.copy(),
                'metrics': metrics,
                'simulation_results': None,  # Don't store all results to save memory
            })

            return metrics.rmse
        except Exception as e:
            # Return large value if simulation fails
            return 1e10

    # Run optimization
    result = differential_evolution(
        objective_function,
        bounds,
        maxiter=max_iterations,
        seed=42,
        workers=1,
        updating='deferred',
        atol=1e-6,
        tol=1e-6,
    )

    # Get best parameters
    best_parameters = dict(zip(param_names, result.x))

    # Run final simulation with best parameters
    results_df = run_simulation_with_params(
        floor_spec, equipment_spec, monthly_conditions, best_parameters
    )

    simulated, actual = extract_comparison_values(
        results_df, actual_data, comparison_target
    )

    best_metrics = calculate_metrics(simulated, actual)

    # Prepare results
    results = [{
        'parameters': best_parameters,
        'metrics': best_metrics,
        'simulation_results': results_df.to_dict('records'),
    }]

    # Add some history results (keep last 10)
    results.extend(history[-10:])

    return results
