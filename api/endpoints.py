from fastapi import APIRouter, HTTPException
from service.vehicle_clustering import CarGrouper
from dto.grouping_data import VehicleGroupingRequest, VehicleGroupingResponse
import logging 


# Define the router for the FastAPI app
router = APIRouter()

# Logging configuration
logging.basicConfig(
    format = '%(levelname)s:     %(asctime)s, %(module)s, %(processName)s, %(message)s', 
    level = logging.INFO)

# Instantiate logger
logger = logging.getLogger(__name__)


# Define a POST request handler for the '/vehicle_grouping' endpoint
@router.post(
        '/vehicle_grouping',                                 # Endpoint name
        response_model = VehicleGroupingResponse,  # Data model for the response 
        tags = ['Vehicle Grouping']               # Tag used for documentation
        )
# Define an asynchronous function accepting a 'VehicleGroupingRequest' as request body
async def groups(input_data: VehicleGroupingRequest):
    '''
    Analyze a folder of images with vehicles and return image groups by color of vehicle.
    
    Parameters:
      - input_data[VehicleGroupingRequest]: Request data including 'images_path' (str).

    Returns:
      - VehicleGroupingResponse: Response data containing a list of groups.

    Example Usage:
      - Send a POST request with JSON data containing the 'images_path' to download folder and apply clustewring technique.
    '''

    # Log request information
    logger.info(f'Analysis for folder: {input_data.images_path}.')
    
    # Perform the color extraction
    try:
        
        # Instantiate the ColorAnalyzer class for image processing
        output_json = CarGrouper(
                input_data.images_path
            ).group_vehicles()

        logger.info(f'Analysis completed.')
        
        # Return the groups
        return {'vehicle_groups': output_json}

    # If an error occurs
    except Exception as e:
        
        # Log the error message 
        logger.error(f'Exception in folder processing: {str(e)}.')

        # Raise an exception
        raise HTTPException(status_code=500, detail=str(e))