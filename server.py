from mcp.server.fastmcp import FastMCP, Context

import logging
from dataclasses import dataclass
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, List
import os
import sys

if 'SUMO_HOME' in os.environ:
    sys.path.append(os.path.join(os.environ['SUMO_HOME'], 'tools'))

import traci

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger("SUMOMCPServer")

@dataclass
class SUMOConnection:
    """Class representing a connection to the SUMO server."""
    name: str
    host: str
    port: int

    def connect(self):
        """Establish a connection to the SUMO server."""
        logger.info(f"Connecting to SUMO server {self.name} at {self.host}:{self.port}")
        try:
            traci.connect(host=self.host, port=self.port)
            logger.info(f"Connected to SUMO server {self.name}")
        except Exception as e:
            logger.error(f"Failed to connect to SUMO server {self.name}: {e}")
            raise

    def disconnect(self):
        """Disconnect from the SUMO server."""
        logger.info(f"Disconnecting from SUMO server {self.name}")
        try:
            traci.close()
            logger.info(f"Disconnected from SUMO server {self.name}")
        except Exception as e:
            logger.error(f"Failed to disconnect from SUMO server {self.name}: {e}")
            raise

    def get_vehicles(self) -> List[str]:
        """Get the list of vehicles from the SUMO server."""
        try:
            vehicles = traci.vehicle.getIDList()
            logger.info(f"Retrieved vehicles: {vehicles}")
            return vehicles
        except Exception as e:
            logger.error(f"Failed to get vehicles from SUMO server: {e}")
            raise
    def get_vehicle_speed(self, vehicle_id: str) -> float:
        """Get the speed of a specific vehicle."""
        try:
            speed = traci.vehicle.getSpeed(vehicle_id)
            logger.info(f"Retrieved speed for vehicle {vehicle_id}: {speed}")
            return speed
        except Exception as e:
            logger.error(f"Failed to get speed for vehicle {vehicle_id}: {e}")
            raise
    def get_vehicle_position(self, vehicle_id: str) -> List[float]:
        """Get the position of a specific vehicle."""
        try:
            position = traci.vehicle.getPosition(vehicle_id)
            logger.info(f"Retrieved position for vehicle {vehicle_id}: {position}")
            return position
        except Exception as e:
            logger.error(f"Failed to get position for vehicle {vehicle_id}: {e}")
            raise
    def get_vehicle_acceleration(self, vehicle_id: str) -> float:
        """Get the acceleration of a specific vehicle."""
        try:
            acceleration = traci.vehicle.getAcceleration(vehicle_id)
            logger.info(f"Retrieved acceleration for vehicle {vehicle_id}: {acceleration}")
            return acceleration
        except Exception as e:
            logger.error(f"Failed to get acceleration for vehicle {vehicle_id}: {e}")
            raise
    def get_vehicle_lane(self, vehicle_id: str) -> str:
        """Get the lane of a specific vehicle."""
        try:
            lane = traci.vehicle.getLaneID(vehicle_id)
            logger.info(f"Retrieved lane for vehicle {vehicle_id}: {lane}")
            return lane
        except Exception as e:
            logger.error(f"Failed to get lane for vehicle {vehicle_id}: {e}")
            raise
    def get_vehicle_route(self, vehicle_id: str) -> List[str]:
        """Get the route of a specific vehicle."""
        try:
            route = traci.vehicle.getRoute(vehicle_id)
            logger.info(f"Retrieved route for vehicle {vehicle_id}: {route}")
            return route
        except Exception as e:
            logger.error(f"Failed to get route for vehicle {vehicle_id}: {e}")
            raise
    def get_vehicle_route_edges(self, vehicle_id: str) -> List[str]:
        """Get the route edges of a specific vehicle."""
        try:
            route_edges = traci.vehicle.getRouteID(vehicle_id)
            logger.info(f"Retrieved route edges for vehicle {vehicle_id}: {route_edges}")
            return route_edges
        except Exception as e:
            logger.error(f"Failed to get route edges for vehicle {vehicle_id}: {e}")
            raise
            

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Lifespan context manager for the FastMCP server."""
    try:
        logger.info("Starting FastMCP server")
        try:
            sumo = get_sumo_connection()
            logger.info("Sucessfully connected to SUMO server")
        except Exception as e:
            logger.error(f"Failed to connect to SUMO server: {e}")
        yield {}
    finally:
            global _sumo_connection
            if _sumo_connection:
                logger.info("Disconnecting from SUMO on shutdown")
                _sumo_connection.disconnect()
            logger.info("SUMOMCP server shut down")

mcp = FastMCP(
    "SUMOMCP",
    description="SUMO integration through the Model Context Protocol",
    lifespan=server_lifespan
)

_sumo_connection = None

def get_sumo_connection():
    """Get the SUMO connection."""
    global _sumo_connection
    if _sumo_connection is None:
        try:
            _sumo_connection = SUMOConnection(name="SUMO", host="localhost", port=8813)
            _sumo_connection.connect()
            logger.info("Connected to SUMO server")
        except Exception as e:
            logger.error(f"Failed to connect to SUMO server: {e}")
            raise
    else:
        try:
            traci.start(["sumo", "-c", "your_sumo_config_file.sumocfg"])
            logger.info("SUMO started successfully")
        except Exception as e:
            logger.error(f"Failed to start SUMO: {e}")
            raise
    return _sumo_connection

@mcp.tool()
def get_vehicles(ctx: Context) -> List[str]:
    """Get the list of vehicles from the SUMO server."""
    logger.info("Getting vehicles from SUMO server")
    try:
        sumo = get_sumo_connection()
        vehicles = sumo.get_vehicles()
        logger.info(f"Retrieved vehicles: {vehicles}")
        return vehicles
    except Exception as e:
        logger.error(f"Failed to get vehicles from SUMO server: {e}")
        raise

@mcp.tool()
def get_vehicle_speed(ctx: Context, vehicle_id: str) -> float:
    """Get the speed of a specific vehicle."""
    logger.info(f"Getting speed for vehicle {vehicle_id}")
    try:
        sumo = get_sumo_connection()
        speed = sumo.get_vehicle_speed(vehicle_id)
        logger.info(f"Retrieved speed for vehicle {vehicle_id}: {speed}")
        return speed
    except Exception as e:
        logger.error(f"Failed to get speed for vehicle {vehicle_id}: {e}")
        raise

@mcp.tool()
def get_vehicle_position(ctx: Context, vehicle_id: str) -> List[float]:
    """Get the position of a specific vehicle."""
    logger.info(f"Getting position for vehicle {vehicle_id}")
    try:
        sumo = get_sumo_connection()
        position = sumo.get_vehicle_position(vehicle_id)
        logger.info(f"Retrieved position for vehicle {vehicle_id}: {position}")
        return position
    except Exception as e:
        logger.error(f"Failed to get position for vehicle {vehicle_id}: {e}")
        raise

@mcp.tool()
def get_vehicle_acceleration(ctx: Context, vehicle_id: str) -> float:
    """Get the acceleration of a specific vehicle."""
    logger.info(f"Getting acceleration for vehicle {vehicle_id}")
    try:
        sumo = get_sumo_connection()
        acceleration = sumo.get_vehicle_acceleration(vehicle_id)
        logger.info(f"Retrieved acceleration for vehicle {vehicle_id}: {acceleration}")
        return acceleration
    except Exception as e:
        logger.error(f"Failed to get acceleration for vehicle {vehicle_id}: {e}")
        raise

@mcp.tool()
def get_vehicle_lane(ctx: Context, vehicle_id: str) -> str:
    """Get the lane of a specific vehicle."""
    logger.info(f"Getting lane for vehicle {vehicle_id}")
    try:
        sumo = get_sumo_connection()
        lane = sumo.get_vehicle_lane(vehicle_id)
        logger.info(f"Retrieved lane for vehicle {vehicle_id}: {lane}")
        return lane
    except Exception as e:
        logger.error(f"Failed to get lane for vehicle {vehicle_id}: {e}")
        raise

@mcp.tool()
def get_vehicle_route(ctx: Context, vehicle_id: str) -> List[str]:
    """Get the route of a specific vehicle."""
    logger.info(f"Getting route for vehicle {vehicle_id}")
    try:
        sumo = get_sumo_connection()
        route = sumo.get_vehicle_route(vehicle_id)
        logger.info(f"Retrieved route for vehicle {vehicle_id}: {route}")
        return route
    except Exception as e:
        logger.error(f"Failed to get route for vehicle {vehicle_id}: {e}")
        raise

@mcp.tool()
def get_vehicle_route_edges(ctx: Context, vehicle_id: str) -> List[str]:
    """Get the route edges of a specific vehicle."""
    logger.info(f"Getting route edges for vehicle {vehicle_id}")
    try:
        sumo = get_sumo_connection()
        route_edges = sumo.get_vehicle_route_edges(vehicle_id)
        logger.info(f"Retrieved route edges for vehicle {vehicle_id}: {route_edges}")
        return route_edges
    except Exception as e:
        logger.error(f"Failed to get route edges for vehicle {vehicle_id}: {e}")
        raise

def main():
    """Run the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()