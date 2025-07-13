from services.do_service import process_do

class DOController:
    def process_do(self, file):
        """
        Process a delivery order document to extract DO ID and check for signature
        
        Args:
            file: File object (PDF or Image)
            
        Returns:
            dict: Result containing DO ID and signature status
        """
        return process_do(file)
