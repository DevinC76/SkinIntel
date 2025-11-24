import logging
from roboflow import Roboflow
from app.config import ROBOFLOW_API_KEY

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages Roboflow ML models"""

    def __init__(self):
        self.acne_model = None
        self.skin_disease_model = None
        self.skin_class_model = None
        self._initialized = False

    def initialize(self):
        """Initialize all Roboflow models"""
        if self._initialized:
            return

        logger.info("Initializing Roboflow models...")
        rf = Roboflow(api_key=ROBOFLOW_API_KEY)

        self.acne_model = rf.workspace().project("acnedet-v1").version(2).model
        self.skin_disease_model = rf.workspace("kelixo").project("skin_disease_ak").version(1).model
        self.skin_class_model = rf.workspace("skn-f1vaw").project("skn-1").version(1).model

        self._initialized = True
        logger.info("Models loaded successfully")

    @property
    def is_initialized(self):
        return self._initialized

# Global model manager instance
model_manager = ModelManager()
